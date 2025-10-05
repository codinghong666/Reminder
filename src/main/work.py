from simple_qq_parser import get_and_parse_messages
from datetime import datetime
import os
from datebase import find_if_exist, insert_data, remove_data, iter_data, init_database
import util
from loadconfig import load_config
import my_llm
def extract_time_info(message:str)->str:
    model = util.get_llm(load_config().get('model_choice'))
    print(f"model: {model}")
    prompt = open("prompt.txt", "r").read() 
    print(f"prompt: {prompt}")
    
    # Build complete prompt
    full_prompt = prompt + "\n" + message
    output = model(full_prompt)
    output = output.strip()
    if not output or output.lower() in ['无', '没有', 'none', 'no', '无时间信息', '未检测到时间信息', 'no time information detected']:
        return None
    return output

def check(group_id, message_id):
    return not find_if_exist(group_id, message_id)

def work():
    # Initialize database first
    init_database()
    
    # Get messages from all configured groups
    results = get_and_parse_messages()
    
    # Create output filename (with timestamp)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/qq_messages_analysis_{timestamp}.txt"
    
    if results:
        print(f"\n=== Summary: Processed {len(results)} groups ===")
        print(f"Output will be saved to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"QQ Group Message Time Information Extraction Results\n")
            f.write(f"Number of groups processed: {len(results)}\n")
            f.write("="*60 + "\n\n")
            
            for group_id, group_data in results.items():
                group_name = group_data['group_name']
                message_count = len(group_data['messages'])
                
                print(f"\n=== Processing Group: {group_name} ({message_count} messages) ===")
                f.write(f"Group: {group_name}\n")
                f.write("-"*40 + "\n")
                # Binary search for first non-existent message
                l, r = 0, message_count - 1
                ans = message_count  # Default to start from the end, skip if all exist
                while l <= r:
                    mid = (l + r) // 2
                    if check(group_id, group_data['message_ids'][mid]):
                        # Current message doesn't exist, record position and continue searching left
                        ans = mid
                        r = mid - 1
                    else:
                        # Current message exists, search right
                        l = mid + 1
                for i in range(ans, message_count):
                    message_id, sender_name, message = group_data['message_ids'][i], group_data['senders'][i], group_data['messages'][i]
                    print(f"\n--- Message {i} ---")
                    print("Original message:")
                    print(message)
                    try:
                        # time_info = extract_time_info(message)
                        time_info = extract_time_info(message)
                        if time_info is None:
                            time_info = "None"
                        result_line = f"{time_info}:\n{message}"
                        print(result_line)
                        f.write(f"{result_line}\n")
                        insert_data(group_id, message_id, message, time_info)
                    except Exception as e:
                        error_msg = f"Time extraction failed: {e}"
                        print(error_msg)
                    print("\n" + "="*50)
        
        print(f"\nAnalysis completed! Results saved to: {output_file}")
        
    else:
        print("No groups processed")
    

def see_data():
    data = iter_data()
    for i in data:
        print(i)
if __name__ == "__main__":
    work()
    see_data()