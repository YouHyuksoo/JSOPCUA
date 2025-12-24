"""
PLC Communication Package

Mitsubishi Q Series PLC와의 MC 3E ASCII 프로토콜 통신을 담당하는 패키지입니다.
"""

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name: str = 'plc', log_dir: str = 'logs', level: int = logging.INFO) -> logging.Logger:
    """
    PLC 통신 로거 설정

    Args:
        name: 로거 이름
        log_dir: 로그 파일 디렉토리
        level: 로그 레벨

    Returns:
        설정된 Logger 객체
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 설정되어 있으면 중복 설정 방지
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 로그 디렉토리 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 파일 핸들러 (10MB, 최대 5개 백업)
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 기본 로거 생성
logger = setup_logger()

__all__ = ['setup_logger', 'logger']
