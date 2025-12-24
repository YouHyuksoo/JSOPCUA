"""
PLC 통신 유틸리티 함수

태그 주소 파싱, 그룹화 등의 유틸리티 함수를 제공합니다.
"""

import re
from typing import List, Dict, Tuple, Optional
from . import logger


def parse_tag_address(tag_address: str) -> Optional[Tuple[str, int, Optional[str], Optional[int | str]]]:
    """
    태그 주소를 디바이스 타입과 번호로 파싱

    W327C.6, W327C.A ~ W327C.Z 형식의 확장 주소도 지원합니다.

    Args:
        tag_address: 태그 주소
        - 기본 형식: "D100", "X10", "Y20"
        - 확장 형식: "W327C", "W327C.6", "W327C.A" (링크 디바이스 비트)

    Returns:
        (디바이스 타입, 번호, 확장문자, 비트오프셋) 튜플 또는 None (파싱 실패 시)
        - 디바이스 타입: 예) 'W', 'D'
        - 번호: 정수
        - 확장문자: W327C의 "C" (없으면 None)
        - 비트오프셋: 정수(0-9) 또는 문자(A-Z), 없으면 None

    Examples:
        >>> parse_tag_address("D100")
        ('D', 100, None, None)
        >>> parse_tag_address("W327C")
        ('W', 327, 'C', None)
        >>> parse_tag_address("W327C.6")
        ('W', 327, 'C', 6)
        >>> parse_tag_address("W327C.A")
        ('W', 327, 'C', 'A')
        >>> parse_tag_address("X10")
        ('X', 10, None, None)
    """
    # 정규식: 영문자 + 숫자 + [선택: 영문자 + [선택: 점 + 숫자 또는 문자]]
    # W327C.6 → ('W', '327', 'C', '6')
    # W327C.A → ('W', '327', 'C', 'A')
    # W327C.Z → ('W', '327', 'C', 'Z')
    # W327C → ('W', '327', 'C', None)
    # D100 → ('D', '100', None, None)
    pattern = r'^([A-Z]+)(\d+)([A-Z])?(?:\.([0-9A-Z]))?$'
    match = re.match(pattern, tag_address.upper())

    if match:
        device_type = match.group(1)      # 예: 'W', 'D'
        device_number = int(match.group(2))  # 예: 327, 100
        extend_char = match.group(3) or None  # 예: 'C'
        bit_offset_str = match.group(4) or None  # 예: '6' 또는 'A'

        # bit_offset을 저장 (숫자 또는 문자 모두 가능)
        if bit_offset_str is not None:
            # 숫자인 경우 정수로, 문자인 경우 문자 그대로 저장
            if bit_offset_str.isdigit():
                bit_offset = int(bit_offset_str)
            else:
                bit_offset = bit_offset_str
        else:
            bit_offset = None

        return (device_type, device_number, extend_char, bit_offset)

    logger.warning(f"Failed to parse tag address: {tag_address}")
    return None


def group_continuous_addresses(tag_addresses: List[str]) -> Dict[str, List[Tuple[int, int, List[str]]]]:
    """
    연속된 태그 주소를 그룹화

    동일한 디바이스 타입의 연속된 주소들을 그룹으로 묶어서
    배치 읽기를 최적화합니다.

    W327C.6 형식의 비트 주소는 개별 처리됩니다 (그룹화되지 않음).

    Args:
        tag_addresses: 태그 주소 리스트

    Returns:
        디바이스 타입별 그룹 딕셔너리
        - Key: 디바이스 타입 (예: "D", "X", "W")
        - Value: [(시작 주소, 개수, 원본 태그 리스트), ...]

    Examples:
        >>> group_continuous_addresses(["D100", "D101", "D102", "D200", "X10", "W327C.6"])
        {
            'D': [(100, 3, ['D100', 'D101', 'D102']), (200, 1, ['D200'])],
            'X': [(10, 1, ['X10'])],
            'W': [(327, 1, ['W327C.6'])]
        }
    """
    # 1. 태그 주소 파싱
    parsed_tags = []
    for tag in tag_addresses:
        result = parse_tag_address(tag)
        if result:
            device_type, device_number, extend_char, bit_offset = result
            # 비트 오프셋이 있으면 개별 처리 (그룹화 불가)
            parsed_tags.append((device_type, device_number, tag, extend_char, bit_offset))
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

    for device_type, device_number, original_tag, extend_char, bit_offset in parsed_tags:
        # 비트 오프셋이 있으면 그룹화하지 않음
        if bit_offset is not None or extend_char is not None:
            # 이전 그룹 저장
            if current_device and current_tags:
                if current_device not in groups:
                    groups[current_device] = []
                groups[current_device].append((current_start, len(current_tags), current_tags))
                current_tags = []

            # 비트 주소는 개별 항목으로 추가
            if device_type not in groups:
                groups[device_type] = []
            groups[device_type].append((device_number, 1, [original_tag]))

            current_device = None
            current_start = None
            continue

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
