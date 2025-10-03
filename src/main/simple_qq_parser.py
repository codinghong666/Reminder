#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple QQ group message fetcher and parser
Only outputs text content and sender nickname
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from loadconfig import load_config





def get_group_messages(group_id, count, config):
    """
    Get group message history
    
    Args:
        group_id: Group ID
        count: Number of messages to fetch
        config: Configuration dictionary
    """
    api_config = config.get('api', {})
    base_url = api_config.get('base_url', 'http://localhost:3001')
    token = api_config.get('token', '1145141919810')
    timeout = api_config.get('timeout', 10)
    
    url = f"{base_url}/get_group_msg_history"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    payload = {
        "group_id": group_id,
        "message_seq": "",
        "count": count,
        "reverseOrder": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误 - 无法连接到 {base_url}: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"请求超时 - {base_url}: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误 - {base_url}: {e}")
        return None
    except Exception as e:
        print(f"API请求失败 - {base_url}: {e}")
        return None


def parse_text_only(api_response):
    """
    Parse API response, extract only text content and sender nickname
    
    Args:
        api_response: API response data
    """
    if not api_response or api_response.get('status') != 'ok':
        print("API response error")
        return []
    
    messages = api_response.get('data', {}).get('messages', [])
    
    print(f"=== Group Message Text Content ({len(messages)} messages) ===\n")
    
    message_list = []
    sender_list = []
    message_id_list = []
    for message in messages:
        # Get sender info
        sender = message.get('sender', {})
        message_id = message.get('message_id')
        message_time = message.get('time')
        sender_name = sender.get('card', sender.get('nickname', 'Unknown User'))
        
        # Extract text content
        message_parts = message.get('message', [])
        text_parts = []
        
        for msg_part in message_parts:
            if msg_part.get('type') == 'text':
                text_content = msg_part.get('data', {}).get('text', '')
                if text_content.strip():
                    text_parts.append(text_content.strip())
        
        # Output if has text content
        if text_parts:
            text_content = '\n'.join(text_parts)
            
            # Format message
            formatted_message = text_content
            message_id_list.append(message_id)
            sender_list.append(sender_name)
            message_list.append(formatted_message)
    return message_list, sender_list, message_id_list


def get_and_parse_messages(config_file="config.env"):
    """
    Main function to get and parse messages from configured groups
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary with group results
    """
    config = load_config(config_file)
    if not config:
        return {}
    
    groups = config.get('groups', [])
    results = {}
    
    print("Fetching group messages...")
    
    for group in groups:
        group_id = group.get('group_id')
        group_name = group.get('group_name', f'Group {group_id}')
        message_count = group.get('message_count', 20)
        
        print(f"\n=== Processing {group_name} (ID: {group_id}) ===")
        
        # Get messages
        response = get_group_messages(group_id, message_count, config)
        
        if response:
            # Parse and output text content
            message_list, sender_list, message_id_list = parse_text_only(response)
            results[group_id] = {
                'group_name': group_name,
                'messages': message_list,
                'senders': sender_list,
                'message_ids': message_id_list
            }
        else:
            print(f"Failed to get messages for group {group_name}")
            results[group_id] = {
                'group_name': group_name,
                'messages': []
            }
    
    return results

if __name__ == "__main__":
   print(get_and_parse_messages())