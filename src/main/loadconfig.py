import os
from dotenv import load_dotenv
def load_config(config_file="config.env"):
    """
    Load configuration from .env file using python-dotenv
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    # Load .env file
    load_dotenv(config_file)
    
    # Get environment variables
    token = os.getenv('TOKEN')
    group_ids_str = os.getenv('GROUP_IDS')
    message_count = int(os.getenv('MESSAGE_COUNT', '20'))
    work_time = os.getenv('WORK_TIME', '02:00')
    send_time = os.getenv('SEND_TIME', '08:50')
    base_url = os.getenv('BASE_URL', 'http://localhost:3001')
    
    # Validate required fields
    if not token:
        print("Error: TOKEN is required in config file")
        return None
    if not group_ids_str:
        print("Error: GROUP_IDS is required in config file")
        return None
    
    # Parse group IDs
    group_ids = [gid.strip() for gid in group_ids_str.split(',') if gid.strip()]
    groups = []
    for group_id in group_ids:
        groups.append({
            'group_id': group_id,
            "message_seq": "",
            'message_count': message_count, 
            "reverseOrder": "false"
        })
    send_id = os.getenv('SEND_ID')
    model = os.getenv('MODEL')
    working_qq = os.getenv('WORKING_QQ')
    config = {
        "api": {
            "base_url": base_url,
            "token": token,
            "timeout": 10
        },
        "groups": groups,
        "send_id": send_id,
        "work_time": work_time,
        "send_time": send_time,
        "model": model,
        "working_qq": working_qq
    }
    
    return config