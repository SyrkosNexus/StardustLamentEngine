"""
日志配置模块，提供统一的日志配置
"""
import os
import logging
from datetime import datetime

def setup_logging(log_dir="logs", level=logging.INFO):
    """
    配置日志系统
    
    参数:
        log_dir: 日志目录
        level: 日志级别
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"stardust-lament-engine_{timestamp}.log")
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return log_file