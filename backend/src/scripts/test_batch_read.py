"""
배치 읽기 성능 테스트 스크립트

개별 읽기 vs 배치 읽기 성능을 비교합니다.
"""

import sys
import os
import time

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.plc.pool_manager import PoolManager
from src.plc.exceptions import PLCException


def test_batch_performance(plc_code: str = None, start_address: int = 100, count: int = 50):
    """
    배치 읽기 성능 테스트

    Args:
        plc_code: 테스트할 PLC 코드 (None이면 첫 번째 활성 PLC 사용)
        start_address: 시작 태그 주소 번호 (기본 100, D100부터 시작)
        count: 읽을 태그 개수 (기본 50)
    """
    db_path = os.path.join(os.path.dirname(__file__), '../../data/scada.db')

    print(f"\n{'='*70}")
    print("Batch Read Performance Test")
    print(f"{'='*70}\n")

    # PoolManager 초기화
    print("📌 Initializing PoolManager...")
    pool_mgr = PoolManager(db_path)

    try:
        pool_mgr.initialize()

        if pool_mgr.get_plc_count() == 0:
            print("❌ No active PLC found")
            return False

        # PLC 코드 결정
        if not plc_code:
            stats = pool_mgr.get_pool_stats()
            plc_code = list(stats.keys())[0]

        print(f"✅ Using PLC: {plc_code}\n")

        # 테스트할 태그 주소 생성
        tag_addresses = [f"D{start_address + i}" for i in range(count)]

        print(f"📋 Test Configuration:")
        print(f"   Start Address: D{start_address}")
        print(f"   Tag Count: {count}")
        print(f"   Tags: {tag_addresses[0]} ~ {tag_addresses[-1]}\n")

        print(f"{'-'*70}\n")

        # 테스트 1: 개별 읽기
        print(f"🔹 Test 1: Individual Read ({count} tags)")
        print(f"   Reading tags one by one...\n")

        individual_times = []
        individual_start = time.time()

        for tag in tag_addresses:
            try:
                tag_start = time.time()
                value = pool_mgr.read_single(plc_code, tag)
                tag_time = (time.time() - tag_start) * 1000
                individual_times.append(tag_time)
                print(f"   {tag}: {value} ({tag_time:.2f}ms)")
            except PLCException as e:
                print(f"   ❌ {tag}: {e}")

        individual_total = (time.time() - individual_start) * 1000

        print(f"\n   📊 Individual Read Results:")
        print(f"      Total Time: {individual_total:.2f}ms")
        print(f"      Average per Tag: {individual_total/count:.2f}ms")
        if individual_times:
            print(f"      Min: {min(individual_times):.2f}ms, Max: {max(individual_times):.2f}ms\n")

        print(f"{'-'*70}\n")

        # 테스트 2: 배치 읽기
        print(f"🔹 Test 2: Batch Read ({count} tags)")
        print(f"   Reading all tags in batches...\n")

        batch_start = time.time()

        try:
            values = pool_mgr.read_batch(plc_code, tag_addresses)
            batch_total = (time.time() - batch_start) * 1000

            print(f"   ✅ Batch read successful!")
            print(f"   Tags read: {len(values)}/{count}\n")

            # 샘플 출력 (처음 5개, 마지막 5개)
            print(f"   Sample values:")
            for i, (tag, value) in enumerate(values.items()):
                if i < 5 or i >= len(values) - 5:
                    print(f"      {tag}: {value}")
                elif i == 5:
                    print(f"      ... ({len(values) - 10} more tags) ...")

            print(f"\n   📊 Batch Read Results:")
            print(f"      Total Time: {batch_total:.2f}ms")
            print(f"      Average per Tag: {batch_total/count:.2f}ms\n")

        except PLCException as e:
            print(f"   ❌ Batch read failed: {e}\n")
            batch_total = 0

        print(f"{'-'*70}\n")

        # 성능 비교
        if batch_total > 0:
            speedup = individual_total / batch_total
            improvement = ((individual_total - batch_total) / individual_total) * 100

            print(f"📈 Performance Comparison:\n")
            print(f"   Individual Read: {individual_total:.2f}ms")
            print(f"   Batch Read:      {batch_total:.2f}ms")
            print(f"   Speedup:         {speedup:.2f}x")
            print(f"   Improvement:     {improvement:.1f}%\n")

            if speedup >= 5:
                print(f"   ✅ SUCCESS: Batch read is {speedup:.1f}x faster (target: ≥5x)\n")
            else:
                print(f"   ⚠️  WARNING: Batch read is only {speedup:.1f}x faster (target: ≥5x)\n")

        print(f"{'='*70}")
        print("✅ Test completed")
        print(f"{'='*70}\n")

        return True

    except Exception as e:
        print(f"\n❌ Test Error: {e}\n")
        print(f"{'='*70}")
        print("❌ Test failed")
        print(f"{'='*70}\n")
        return False

    finally:
        pool_mgr.shutdown()


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Test batch read performance')
    parser.add_argument('--plc', type=str, help='PLC code to test (default: first active PLC)')
    parser.add_argument('--start', type=int, default=100, help='Start address number (default: 100 for D100)')
    parser.add_argument('--count', type=int, default=50, help='Number of tags to read (default: 50)')

    args = parser.parse_args()

    success = test_batch_performance(
        plc_code=args.plc,
        start_address=args.start,
        count=args.count
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
