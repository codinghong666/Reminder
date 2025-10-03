import requests
from loadconfig import load_config
import logging
from datebase import iter_data
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('send.log'),
        logging.StreamHandler()
    ]
)


def send(message,config):
    """
    Get group message history
    
    Args:
        group_id: Group ID
        count: Number of messages to fetch
        config: Configuration dictionary
    """
    api_config = config.get('api', {})
    base_url = api_config.get('base_url', 'http://localhost:3000')
    token = api_config.get('token', '1145141919810')
    timeout = api_config.get('timeout', 10)
    
    url = f"{base_url}/send_private_forward_msg"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    payload = {
        "user_id": config.get('send_id'),
        "messages": [      {
                "type": "text",
                "data": {
                "text": message
                }
            }],
        "news": [],
        "prompt": "textValue",
        "summary": "textValue",
        "source": "textValue"
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed for group {config.get('send_id')}: {e}")
        return None

def check_all():
    try:
        config = load_config()
        if config is None:
            logging.error("Config not loaded, skipping send")
            return
        
        logging.info("Send task started")
        
        # Get data from database
        data = iter_data()
        
        if not data:
            message_content = "datebase is empty"
            logging.info("datebase is empty")
        else:
            # Get current date and next day date
            from datetime import datetime, timedelta
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Build message content
            message_content = "今日时间信息汇总：\n\n"
            filtered_messages = []
            
            for record in data:
                message_time_str = record[4]  # Time field
                if message_time_str:
                    message_time_str = message_time_str.strip()
                    try:
                        # Parse time string (format: MM:DD:HH:MM)
                        if '-' in message_time_str:
                            time_parts_list = message_time_str.split('-')
                            for time_parts in time_parts_list:
                                if len(time_parts) >= 2:
                                    time_parts = time_parts.split(':')
                                    month = int(time_parts[0])
                                    day = int(time_parts[1])
                                    current_year = datetime.now().year
                                    message_date = datetime(current_year, month, day).date()
                                    if message_date >= today and message_date <= tomorrow:
                                        filtered_messages.append(record)
                                        break
                        else:
                            time_parts = message_time_str.split(':')
                            if len(time_parts) >= 2:
                                month = int(time_parts[0])
                                day = int(time_parts[1])
                                
                                # Construct date (assuming current year)
                                current_year = datetime.now().year
                                message_date = datetime(current_year, month, day).date()
                                
                                # Check if it's yesterday or today
                                if message_date >= today and message_date <= tomorrow:
                                    filtered_messages.append(record)
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Invalid time format: {message_time_str}")
                        continue
            
            if filtered_messages:
                for i, record in enumerate(filtered_messages, 1):  
                    message_content += f"{i}. 时间: {record[4]}\n   消息: {record[3]}\n\n"
            else:
                message_content = "今日暂无符合条件的时间信息数据"
                logging.info("No messages found for today or yesterday")
        
        # Send message
        result = send(message_content, config)
        print(result)
        if result:
            logging.info("Send task completed")
        else:
            logging.error("Send task failed")
            
    except Exception as e:
        logging.error(f"Send task error: {e}")
if __name__ == "__main__":
    check_all()