import requests
import os
from simple_qq_parser import get_group_messages, parse_text_only
from loadconfig import load_config
def get_summary():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.env")
    config = load_config(config_path)
    summary_count = config.get('summary_count', 10)
    date_all = ""
    cnt = 0
    
    # 获取所有群组的消息
    for group in config.get('groups', []):
        group_id = group.get('group_id') if isinstance(group, dict) else group
        response = get_group_messages(group_id, summary_count, config)
        if response:
            # 使用parse_text_only函数解析消息
            message_list, sender_list, message_id_list = parse_text_only(response)
            
            # 将消息添加到摘要中
            for i, message in enumerate(message_list):
                sender = sender_list[i] if i < len(sender_list) else "Unknown"
                date_all += f'\n{cnt+1}. [{sender}] {message}'
                cnt += 1
        else:
            print(f"Warning: Failed to get messages for group {group_id}")
            continue
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt_for_summary.txt")
    prompt = open(prompt_path, "r").read()
    prompt = prompt + "\n" + date_all
    print(prompt)

    api_data = {
        "model": "deepseek_reasoner_web",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    # 调用API
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json=api_data,
        timeout=120
    )
    
    if response.status_code != 200:
        print(f"API调用失败，状态码: {response.status_code}")
        return None
    
    result = response.json()
    content = result['choices'][0]['message']['content'].strip()
    
    
    if "<think>" in content:
        content = content.split("<think>")[1].split("</think>")[1]
    # 检查是否包含时间信息
    content = content.strip()
    print(f"Final content: {content}")
    with open("summary.txt", "w") as f:
        f.write(content)

    
if __name__ == "__main__":
    get_summary()