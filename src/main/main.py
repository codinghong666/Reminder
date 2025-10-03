#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Resource QQ Bot Scheduler
Minimal resource consumption task scheduler
Requires installation: pip install apscheduler
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from work import work
from send import check_all
from loadconfig import load_config
from datebase import iter_data
import logging
import subprocess
import time
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minimal_scheduler.log'),
        logging.StreamHandler()
    ]
)

def wait_for_api_ready(base_url="http://localhost:3001", max_wait=30):
    """
    Wait for napcat API to be ready
    
    Args:
        base_url: API base URL
        max_wait: Maximum wait time in seconds
        
    Returns:
        bool: True if API is ready, False if timeout
    """
    logging.info("Waiting for napcat API to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            # Try to connect to the API
            response = requests.get(f"{base_url}/get_group_msg_history", timeout=2)
            if response.status_code == 200:
                logging.info("Napcat API is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
    
    logging.warning(f"API not ready after {max_wait} seconds, proceeding anyway...")
    return False

def run_work_task():
    """Execute work task"""
    try:
        working_qq = load_config().get('working_qq')
        subprocess.run(['sudo','napcat','stop'])
        time.sleep(5)
        subprocess.run(['sudo','napcat','start',working_qq])
        time.sleep(5)
        # Wait for napcat API to be ready
        # wait_for_api_ready(load_config().get('api', {}).get('base_url'))
    except Exception as e:
        logging.error(f"Napcat stop and start failed: {e}")
    try:
        logging.info("Work task started")
        work()
        logging.info("Work task completed")
    except Exception as e:
        logging.error(f"Work task failed: {e}")

def run_send_task():
    """Execute send task"""
    try:
        working_qq = load_config().get('working_qq')
        subprocess.run(['sudo','napcat','stop'])
        time.sleep(5)
        subprocess.run(['sudo','napcat','start',working_qq])
        time.sleep(5)
        # Wait for napcat API to be ready
        # wait_for_api_ready(load_config().get('api', {}).get('base_url'))
    except Exception as e:
        logging.error(f"Napcat stop and start failed: {e}")
    try:
        logging.info("Send task started")
        check_all()
        logging.info("Send task completed")
    except Exception as e:
        logging.error(f"Send task failed: {e}")

def main():
    """Main function"""
    config = load_config()
    if config is None:
        logging.error("Config error, cannot start")
        return
    
    work_time = config.get('work_time', '02:00')
    send_time = config.get('send_time', '08:50')
    
    # Parse time
    work_hour, work_minute = map(int, work_time.split(':'))
    send_hour, send_minute = map(int, send_time.split(':'))
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Add tasks
    scheduler.add_job(
        run_work_task,
        CronTrigger(hour=work_hour, minute=work_minute),
        id='work_task',
        name='Work Task'
    )
    
    scheduler.add_job(
        run_send_task,
        CronTrigger(hour=send_hour, minute=send_minute),
        id='send_task',
        name='Send Task'
    )
    
    logging.info(f"Minimal Scheduler started - Work: {work_time}, Send: {send_time}")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped")
    except Exception as e:
        logging.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()

# MSqDLmgDizGlhYCMZJv9UtNlJMxZzfst