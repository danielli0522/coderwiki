"""
日志工具模块
"""
import logging
import os
from datetime import datetime


def get_logger(name, level=None):
    """
    获取配置好的日志记录器

    Args:
        name (str): 日志记录器名称
        level: 日志级别，默认为None（使用环境变量或默认级别）

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 如果日志记录器已经配置过，直接返回
    if logger.handlers:
        return logger

    # 设置日志级别
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()

    logger.setLevel(getattr(logging, level, logging.INFO))

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level, logging.INFO))

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(console_handler)

    # 创建文件处理器（可选）
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, level, logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def setup_logging():
    """
    设置全局日志配置
    """
    # 设置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # 添加处理器到根日志记录器
    root_logger.addHandler(console_handler)

    # 设置第三方库的日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)




