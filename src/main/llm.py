import os
# 设置环境变量，强制离线模式
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import requests
import json

# Global variables to store model and tokenizer
model = None
tokenizer = None

def load_model():
    """Load model and tokenizer to GPU, execute only once"""
    global model, tokenizer
    
    if model is not None and tokenizer is not None:
        print("Model already loaded, skipping reload")
        return
    
    print("Loading model to GPU...")
    model_name = "Qwen/Qwen3-8B"

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

def extract_time_info(message_text):
    """
    Extract time information from message text
    
    Args:
        message_text: QQ group message text to analyze
        
    Returns:
        Extracted time information string
    """
    global model, tokenizer
    
    # Ensure model is loaded
    if model is None or tokenizer is None:
        load_model()
    
    prompt = open("prompt.txt", "r").read() 
    print(f"prompt: {prompt}")
    
    # Build complete prompt
    full_prompt = prompt + "\n" + message_text
    
    messages = [
        {"role": "user", "content": full_prompt}
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
    
    # Check if contains time information
    if not content or content.lower() in ['无', '没有', 'none', 'no', '无时间信息', '未检测到时间信息', 'no time information detected']:
        return None
    
    # Check if contains time format (MM:DD:time)
    import re
    time_pattern = r'\d{2}:\d{2}:\d{2}:\d{2}'
    if not re.search(time_pattern, content):
        return None
    
    return content

def extract_time_info_by_api(message_text):
    """
    Extract time information from message text using API
    
    Args:
        message_text: QQ group message text to analyze
        
    Returns:
        Extracted time information string
    """
    try:
        # 读取prompt文件
        prompt = open("prompt.txt", "r").read() 
        print(f"prompt: {prompt}")
        
        # 构建完整的prompt
        full_prompt = prompt + "\n" + message_text
        
        # API请求数据
        api_data = {
            "model": "deepseek_reasoner_web",
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "stream": False
        }
        
        # 调用API
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=api_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"API调用失败，状态码: {response.status_code}")
            return None
            
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        print(f"Final content: {content}")
        
        if "<think>" in content:
            content = content.split("<think>")[1].split("</think>")[1]
        # 检查是否包含时间信息
        content = content.strip()
        print(f"Final content: {content}")
        if not content or content.lower() in ['无', '没有', 'none', 'no', '无时间信息', '未检测到时间信息', 'no time information detected']:
            return None
        
        # # 检查是否包含时间格式 (MM:DD:time)
        # import re
        # time_pattern = r'\d{2}:\d{2}:\d{2}:\d{2}'
        # if not re.search(time_pattern, content):
        #     return None
        return content.strip()
        
    except Exception as e:
        print(f"API调用出错: {str(e)}")
        return None

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

