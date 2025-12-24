"""
@file tests/unit/test_mc_address_parsing.py
@description
MC 프로토콜 주소 파싱 및 비트 주소 지원에 대한 단위 테스트입니다.
W327C.6 형식의 새로운 비트 주소 형식 지원을 검증합니다.

테스트 항목:
1. 기본 주소 파싱 (D100, X10, Y20 등)
2. 확장 주소 파싱 (W327C, W327C.6)
3. 비트 오프셋 검증 (0-7만 유효)
4. 주소 그룹화 (비트 주소 개별 처리)
5. 고장난 주소 처리

@example
pytest tests/unit/test_mc_address_parsing.py -v
"""

import pytest
from src.plc.utils import parse_tag_address, group_continuous_addresses


class TestParseTagAddress:
    """태그 주소 파싱 테스트"""

    def test_parse_basic_word_address(self):
        """기본 워드 주소 파싱 테스트"""
        # D100 형식
        result = parse_tag_address("D100")
        assert result == ('D', 100, None, None)

        # W200 형식
        result = parse_tag_address("W200")
        assert result == ('W', 200, None, None)

        # X10, Y20 형식
        result = parse_tag_address("X10")
        assert result == ('X', 10, None, None)

        result = parse_tag_address("Y20")
        assert result == ('Y', 20, None, None)

    def test_parse_extended_address_without_bit(self):
        """확장 주소 파싱 (비트 오프셋 없음)"""
        # W327C 형식 (새로운 링크 디바이스 형식)
        result = parse_tag_address("W327C")
        assert result == ('W', 327, 'C', None)

        # W100A, W100B 등
        result = parse_tag_address("W100A")
        assert result == ('W', 100, 'A', None)

        result = parse_tag_address("W999Z")
        assert result == ('W', 999, 'Z', None)

    def test_parse_extended_address_with_bit(self):
        """확장 주소 파싱 (비트 오프셋 포함 - 숫자)"""
        # W327C.6 형식 (링크 디바이스 비트 주소)
        result = parse_tag_address("W327C.6")
        assert result == ('W', 327, 'C', 6)

        # W327C.0 ~ W327C.9 모두 테스트 (숫자)
        for bit in range(10):
            result = parse_tag_address(f"W327C.{bit}")
            assert result == ('W', 327, 'C', bit), f"비트 {bit} 파싱 실패"

    def test_parse_extended_address_with_char_bit(self):
        """확장 주소 파싱 (비트 오프셋 포함 - 문자)"""
        # W327C.A ~ W327C.Z 형식 (문자 오프셋)
        result = parse_tag_address("W327C.A")
        assert result == ('W', 327, 'C', 'A')

        result = parse_tag_address("W327C.Z")
        assert result == ('W', 327, 'C', 'Z')

        # W327C.A ~ W327C.F 모두 테스트
        for i, char in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            result = parse_tag_address(f"W327C.{char}")
            assert result == ('W', 327, 'C', char), f"비트 {char} 파싱 실패"

    def test_parse_case_insensitive(self):
        """대소문자 무관 파싱"""
        # 소문자 입력
        result = parse_tag_address("d100")
        assert result == ('D', 100, None, None)

        # 혼합 입력
        result = parse_tag_address("w327c.6")
        assert result == ('W', 327, 'C', 6)

    def test_parse_all_valid_offsets(self):
        """모든 유효한 비트 오프셋 테스트"""
        # 숫자 오프셋 0-9
        for bit in range(10):
            result = parse_tag_address(f"W327C.{bit}")
            assert result == ('W', 327, 'C', bit)

        # 문자 오프셋 A-Z
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            result = parse_tag_address(f"W327C.{char}")
            assert result == ('W', 327, 'C', char)

    def test_parse_invalid_format(self):
        """유효하지 않은 주소 형식 테스트"""
        # 숫자 없음
        result = parse_tag_address("D")
        assert result is None

        # 문자 없음
        result = parse_tag_address("100")
        assert result is None

        # 점 뒤에 두 자리 숫자 (한 자리만 가능)
        result = parse_tag_address("D100.99")
        assert result is None

        # 특수 문자 포함
        result = parse_tag_address("D100@")
        assert result is None

        # 점 뒤에 특수 문자
        result = parse_tag_address("D100.!")
        assert result is None

    def test_parse_large_address_numbers(self):
        """큰 번호 주소 파싱"""
        result = parse_tag_address("D9999")
        assert result == ('D', 9999, None, None)

        result = parse_tag_address("W99999C")
        assert result == ('W', 99999, 'C', None)


class TestGroupContinuousAddresses:
    """연속 주소 그룹화 테스트"""

    def test_group_basic_continuous_addresses(self):
        """기본 연속 주소 그룹화"""
        # D100, D101, D102 연속
        result = group_continuous_addresses(["D100", "D101", "D102"])
        assert 'D' in result
        assert result['D'] == [(100, 3, ['D100', 'D101', 'D102'])]

    def test_group_multiple_device_types(self):
        """여러 디바이스 타입 그룹화"""
        addresses = ["D100", "D101", "X10", "D200"]
        result = group_continuous_addresses(addresses)

        assert 'D' in result
        assert 'X' in result

        # D는 두 개 그룹으로 나뉨 (100-101, 200)
        assert len(result['D']) == 2
        assert result['D'][0] == (100, 2, ['D100', 'D101'])
        assert result['D'][1] == (200, 1, ['D200'])

        # X는 하나 그룹
        assert len(result['X']) == 1
        assert result['X'][0] == (10, 1, ['X10'])

    def test_group_bit_addresses_not_grouped(self):
        """비트 주소는 개별 처리 (그룹화 안 함)"""
        # W327C.6은 개별 항목으로 처리됨
        addresses = ["W327C.6", "W327C.7"]
        result = group_continuous_addresses(addresses)

        assert 'W' in result
        # 각각 개별 항목
        assert len(result['W']) == 2
        assert result['W'][0] == (327, 1, ['W327C.6'])
        assert result['W'][1] == (327, 1, ['W327C.7'])

    def test_group_mixed_word_and_bit_addresses(self):
        """워드 주소와 비트 주소 혼합"""
        addresses = ["D100", "D101", "W327C.6", "X10"]
        result = group_continuous_addresses(addresses)

        # D: 연속 그룹 (D100, D101)
        assert 'D' in result
        assert result['D'] == [(100, 2, ['D100', 'D101'])]

        # W: 비트 주소는 개별
        assert 'W' in result
        assert result['W'] == [(327, 1, ['W327C.6'])]

        # X: 단일 항목
        assert 'X' in result
        assert result['X'] == [(10, 1, ['X10'])]

    def test_group_empty_addresses(self):
        """빈 주소 리스트"""
        result = group_continuous_addresses([])
        assert result == {}

    def test_group_invalid_addresses_skipped(self):
        """유효하지 않은 주소는 무시"""
        addresses = ["D100", "INVALID", "D101"]
        result = group_continuous_addresses(addresses)

        # INVALID는 무시되고 D100, D101만 그룹화
        assert 'D' in result
        assert result['D'] == [(100, 2, ['D100', 'D101'])]

    def test_group_preserves_order(self):
        """주소 그룹화 시 순서 유지"""
        addresses = ["D100", "D101", "D102"]
        result = group_continuous_addresses(addresses)

        # 원본 주소 리스트의 순서 유지
        assert result['D'][0][2] == ['D100', 'D101', 'D102']


class TestAddressParsingIntegration:
    """통합 테스트"""

    def test_workflow_with_new_address_format(self):
        """새로운 주소 형식 전체 흐름 테스트"""
        # 테스트 데이터: 기존 형식 + 새 형식 혼합
        addresses = [
            "D100", "D101", "D102",  # 기존: 연속 워드 주소
            "W327C.6",               # 새로운: 비트 주소
            "X10",                   # 기존: 입력 비트
        ]

        # 1단계: 각 주소 파싱
        parsed = []
        for addr in addresses:
            result = parse_tag_address(addr)
            assert result is not None, f"주소 파싱 실패: {addr}"
            parsed.append(result)

        # 2단계: 그룹화
        groups = group_continuous_addresses(addresses)

        # 검증
        assert 'D' in groups  # D 그룹 있음
        assert 'W' in groups  # W 그룹 있음
        assert 'X' in groups  # X 그룹 있음

        # D는 연속으로 그룹화
        assert groups['D'][0] == (100, 3, ['D100', 'D101', 'D102'])

        # W327C.6은 개별 항목
        assert groups['W'][0] == (327, 1, ['W327C.6'])

        # X10은 단일 항목
        assert groups['X'][0] == (10, 1, ['X10'])

    def test_backward_compatibility(self):
        """기존 주소 형식 호환성"""
        # 기존에 사용하던 주소 형식들이 여전히 작동하는지 확인
        legacy_addresses = [
            "D100", "D101", "D102", "D103", "D104",
            "W200", "W201", "W202",
            "X10", "Y20", "M300",
        ]

        for addr in legacy_addresses:
            result = parse_tag_address(addr)
            assert result is not None, f"기존 호환성 실패: {addr}"
            assert result[2] is None  # 확장 문자 없음
            assert result[3] is None  # 비트 오프셋 없음

        # 그룹화도 정상 작동
        groups = group_continuous_addresses(legacy_addresses)
        assert len(groups) == 5  # D, W, X, Y, M 5개 디바이스


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_single_address(self):
        """단일 주소"""
        result = group_continuous_addresses(["W327C.6"])
        assert 'W' in result
        assert result['W'] == [(327, 1, ['W327C.6'])]

    def test_very_large_device_number(self):
        """매우 큰 디바이스 번호"""
        result = parse_tag_address("D999999")
        assert result == ('D', 999999, None, None)

    def test_whitespace_handling(self):
        """공백 처리"""
        # 공백이 있으면 파싱 실패
        result = parse_tag_address("D 100")
        assert result is None

    def test_all_bit_offsets(self):
        """모든 비트 오프셋 (0-9, A-Z) 테스트"""
        # 숫자 오프셋
        for bit in range(10):
            result = parse_tag_address(f"W100C.{bit}")
            assert result == ('W', 100, 'C', bit)

        # 문자 오프셋
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            result = parse_tag_address(f"W100C.{char}")
            assert result == ('W', 100, 'C', char)


if __name__ == "__main__":
    # 직접 실행 시
    pytest.main([__file__, "-v"])
