import os
# 设置环境变量，强制离线模式
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import requests
import json
import util
from loadconfig import load_config
# Global variables to store model and tokenizer
model = None
tokenizer = None

@util.register_llm("local_model")
def use_local_model(prompt:str)->str:   

    def load_model():
        """Load model and tokenizer to GPU, execute only once"""
        global model, tokenizer
        
        if model is not None and tokenizer is not None:
            print("Model already loaded, skipping reload")
            return
        
        print("Loading model to GPU...")
        model_name = "Qwen/Qwen3-8B"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        # Configure 4-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,  # Enable 4-bit quantization
            bnb_4bit_quant_type="nf4",  # Use NF4 data type, more friendly to normal distribution weights
            bnb_4bit_compute_dtype=torch.float16,  # Use float16 for computation
            bnb_4bit_use_double_quant=True,  # Enable nested quantization, saves additional ~0.5GB VRAM
        )

        # Load tokenizer and quantized model from local cache only
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            local_files_only=True  # 只从本地加载，不连接网络
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            quantization_config=quantization_config,  # Key: pass quantization config
            local_files_only=True  # 只从本地加载，不连接网络
        )
        print("Model loading completed")
    def unload_model():
        """Unload model and tokenizer, release GPU memory"""
        global model, tokenizer
        
        if model is not None:
            del model
            model = None
            print("Model unloaded from GPU")
        
        if tokenizer is not None:
            del tokenizer
            tokenizer = None
            print("Tokenizer unloaded")
        
        # Force garbage collection
        import gc
        # import torch
        gc.collect()
        torch.cuda.empty_cache()  # Clear CUDA cache
        print("GPU memory cleared")
    def generate(prompt:str)->str:
            
        global model, tokenizer
        
        # Ensure model is loaded
        if model is None or tokenizer is None:
            load_model()
        
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True  # Switches between thinking and non-thinking modes. Default is True.
        )
        
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # Perform text generation
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=2048,
            temperature=0.1,  # Lower temperature for more stable output
            top_p=0.9,        # Nucleus sampling parameter
            do_sample=True,   # Enable sampling
            repetition_penalty=1.1  # Repetition penalty
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        content = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
        if "<think>" in content:
            content = content.split("<think>")[1].split("</think>")[1]
        # Debug information
        # print(f"Thinking content: {thinking_content[:100]}...")
        print(f"Final content: {content}")
        return content

    load_model()
    output = generate(prompt)
    unload_model()
    return output
@util.register_llm("sdu_model")
def use_sdu_model(prompt:str)->str:
    api_data = {
        "model": "deepseek_reasoner_web",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json=api_data,
        timeout=120
    )
    
    if response.status_code != 200:
        print(f"sdu_model faild: {response.status_code}")
        return None
        
    result = response.json()
    content = result['choices'][0]['message']['content'].strip()
    
    if "<think>" in content:
        content = content.split("<think>")[1].split("</think>")[1]
    # 检查是否包含时间信息
    content = content.strip()
    print(f"sdu_model content: {content}")
    return content

@util.register_llm("api_model")
def use_api_model(prompt:str)->str:
    # Please install OpenAI SDK first: `pip3 install openai`
    
    from openai import OpenAI

    client = OpenAI(
        api_key=load_config().get('api_key'),
        base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是助手，请根据用户的问题给出回答"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    output = response.choices[0].message.content
    if "<think>" in output:
        output = output.split("<think>")[1].split("</think>")[1]
    print(f"api_model content: {output}")
    return output



# if __name__ == "__main__":
#     message1 = "各位同学大家好，现转发一则体育学院通知：山东大学第二十一届体育文化节之山大杯学生跳绳比赛竞赛规程-山东大学体育学院  https://www.tyb.sdu.edu.cn/info/1090/6466.htm对此活动有兴趣的同学请联系体委组 24 化学 姜宝骏同学，联系方式qq:2161044291"
#     message2 = "各位同学：奖学金申请系统现已开启，请【奖学金公示名单】中的同学，于10月3日（周五）14:00前登录山东大学学生管理系统（http://211.86.56.236/login.do）进行申报，申报流程请参考附件1。注：请【威海校区学籍同学】暂时不要进行系统申请，待后续通知。@全体成员"
#     print(extract_time_info(message1))