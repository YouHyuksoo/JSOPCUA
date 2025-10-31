"""
PLC 통신 유틸리티 함수

태그 주소 파싱, 그룹화 등의 유틸리티 함수를 제공합니다.
"""

import re
from typing import List, Dict, Tuple, Optional
from . import logger


def parse_tag_address(tag_address: str) -> Optional[Tuple[str, int]]:
    """
    태그 주소를 디바이스 타입과 번호로 파싱

    Args:
        tag_address: 태그 주소 (예: "D100", "X10", "Y20")

    Returns:
        (디바이스 타입, 번호) 튜플 또는 None (파싱 실패 시)

    Examples:
        >>> parse_tag_address("D100")
        ('D', 100)
        >>> parse_tag_address("X10")
        ('X', 10)
        >>> parse_tag_address("M200")
        ('M', 200)
    """
    # 정규식: 영문자(1개 이상) + 숫자
    pattern = r'^([A-Z]+)(\d+)$'
    match = re.match(pattern, tag_address.upper())

    if match:
        device_type = match.group(1)
        device_number = int(match.group(2))
        return (device_type, device_number)

    logger.warning(f"Failed to parse tag address: {tag_address}")
    return None


def group_continuous_addresses(tag_addresses: List[str]) -> Dict[str, List[Tuple[int, int, List[str]]]]:
    """
    연속된 태그 주소를 그룹화

    동일한 디바이스 타입의 연속된 주소들을 그룹으로 묶어서
    배치 읽기를 최적화합니다.

    Args:
        tag_addresses: 태그 주소 리스트

    Returns:
        디바이스 타입별 그룹 딕셔너리
        - Key: 디바이스 타입 (예: "D", "X")
        - Value: [(시작 주소, 개수, 원본 태그 리스트), ...]

    Examples:
        >>> group_continuous_addresses(["D100", "D101", "D102", "D200", "X10"])
        {
            'D': [(100, 3, ['D100', 'D101', 'D102']), (200, 1, ['D200'])],
            'X': [(10, 1, ['X10'])]
        }
    """
    # 1. 태그 주소 파싱
    parsed_tags = []
    for tag in tag_addresses:
        result = parse_tag_address(tag)
        if result:
            device_type, device_number = result
            parsed_tags.append((device_type, device_number, tag))
        else:
            logger.warning(f"Skipping invalid tag address: {tag}")

    if not parsed_tags:
        return {}

    # 2. 디바이스 타입별로 정렬
    parsed_tags.sort(key=lambda x: (x[0], x[1]))

    # 3. 연속된 주소 그룹화
    groups: Dict[str, List[Tuple[int, int, List[str]]]] = {}

    current_device = None
    current_start = None
    current_tags = []

    for device_type, device_number, original_tag in parsed_tags:
        if current_device != device_type:
            # 새로운 디바이스 타입
            if current_device and current_tags:
                # 이전 그룹 저장
                if current_device not in groups:
                    groups[current_device] = []
                groups[current_device].append((current_start, len(current_tags), current_tags))

            # 새 그룹 시작
            current_device = device_type
            current_start = device_number
            current_tags = [original_tag]

        elif device_number == current_start + len(current_tags):
            # 연속된 주소
            current_tags.append(original_tag)

        else:
            # 비연속 주소 - 이전 그룹 저장하고 새 그룹 시작
            if current_device not in groups:
                groups[current_device] = []
            groups[current_device].append((current_start, len(current_tags), current_tags))

            current_start = device_number
            current_tags = [original_tag]

    # 마지막 그룹 저장
    if current_device and current_tags:
        if current_device not in groups:
            groups[current_device] = []
        groups[current_device].append((current_start, len(current_tags), current_tags))

    return groups


def optimize_batch_reads(tag_addresses: List[str], max_batch_size: int = 50) -> List[List[str]]:
    """
    배치 읽기 최적화

    연속된 주소는 그룹화하고, 배치 크기를 제한합니다.

    Args:
        tag_addresses: 태그 주소 리스트
        max_batch_size: 최대 배치 크기 (기본 50)

    Returns:
        최적화된 배치 리스트

    Examples:
        >>> optimize_batch_reads(["D100", "D101", "D102"])
        [['D100', 'D101', 'D102']]
    """
    groups = group_continuous_addresses(tag_addresses)

    batches = []

    for device_type, group_list in groups.items():
        for start_addr, count, tags in group_list:
            if count <= max_batch_size:
                # 단일 배치로 처리 가능
                batches.append(tags)
            else:
                # 배치 크기 초과 - 분할
                for i in range(0, count, max_batch_size):
                    batch = tags[i:i + max_batch_size]
                    batches.append(batch)

    return batches


def format_device_address(device_type: str, device_number: int) -> str:
    """
    디바이스 타입과 번호를 주소 문자열로 변환

    Args:
        device_type: 디바이스 타입 (예: "D", "X")
        device_number: 디바이스 번호

    Returns:
        태그 주소 문자열

    Examples:
        >>> format_device_address("D", 100)
        'D100'
    """
    return f"{device_type}{device_number}"
