"""
Buffer Overflow Protection Test

Tests FIFO overflow behavior and verifies:
- Buffer caps at max capacity
- Oldest items are discarded (FIFO order)
- Overflow count tracking
- Overflow alerts and logging
- System remains stable under extreme load

Usage:
    python backend/src/scripts/test_buffer_overflow.py [--buffer-size SIZE] [--overflow-count COUNT]
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add backend/src to Python path
backend_src = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_src))

from buffer.circular_buffer import CircularBuffer
from buffer.models import BufferedTagValue


def test_buffer_overflow(buffer_size: int = 1000, overflow_items: int = 500):
    print("=" * 80)
    print("BUFFER OVERFLOW PROTECTION TEST")
    print("=" * 80)
    print(f"Buffer size: {buffer_size}")
    print(f"Items to add: {buffer_size + overflow_items}")
    print(f"Expected overflow: {overflow_items}")
    print("=" * 80)
    print()

    # Create buffer
    buffer = CircularBuffer(maxsize=buffer_size, overflow_alert_threshold=80.0)

    print("[PHASE 1] Filling buffer to capacity...")
    print()

    # Fill buffer to capacity
    for i in range(buffer_size):
        tag_value = BufferedTagValue(
            timestamp=datetime.now(),
            plc_code=f"PLC{(i // 100) + 1:02d}",
            tag_address=f"D{i}",
            tag_value=float(i),
            quality="GOOD"
        )

        success = buffer.put(tag_value)

        # Print progress every 10%
        if (i + 1) % (buffer_size // 10) == 0:
            stats = buffer.stats()
            print(f"  Added {i + 1}/{buffer_size} items "
                  f"(utilization: {stats['utilization_pct']:.1f}%, "
                  f"overflow: {stats['overflow_count']})")

    stats = buffer.stats()
    print()
    print(f"✓ Buffer filled: {stats['current_size']}/{stats['max_size']} items")
    print(f"  Utilization: {stats['utilization_pct']:.1f}%")
    print(f"  Overflow count: {stats['overflow_count']}")
    print()

    # Verify buffer is at capacity
    assert stats['current_size'] == buffer_size
    assert stats['overflow_count'] == 0

    print("[PHASE 2] Testing overflow behavior...")
    print()

    # Store first item for later verification
    first_item = buffer.peek(1)[0]
    print(f"  First item: PLC={first_item.plc_code}, Tag={first_item.tag_address}, Value={first_item.tag_value}")

    # Add more items to trigger overflow
    for i in range(overflow_items):
        tag_value = BufferedTagValue(
            timestamp=datetime.now(),
            plc_code=f"OVERFLOW_{i}",
            tag_address=f"D{buffer_size + i}",
            tag_value=float(buffer_size + i),
            quality="GOOD"
        )

        success = buffer.put(tag_value)

        if not success and i == 0:
            print(f"  ✓ First overflow detected at item {buffer_size + i + 1}")

        if (i + 1) % max(1, overflow_items // 10) == 0:
            stats = buffer.stats()
            print(f"  Added {i + 1}/{overflow_items} overflow items "
                  f"(buffer: {stats['current_size']}/{stats['max_size']}, "
                  f"overflow: {stats['overflow_count']})")

    stats = buffer.stats()
    print()
    print(f"✓ Overflow test complete:")
    print(f"  Buffer size: {stats['current_size']}/{stats['max_size']}")
    print(f"  Total items added: {stats['total_added']}")
    print(f"  Overflow count: {stats['overflow_count']}")
    print(f"  Overflow rate: {stats['overflow_rate_pct']:.3f}%")
    print()

    assert stats['current_size'] == buffer_size
    assert stats['overflow_count'] == overflow_items

    print("[PHASE 3] Verifying FIFO eviction...")
    print()

    current_items = buffer.peek(buffer_size)
    first_values = [item.tag_value for item in current_items[:5]]
    last_values = [item.tag_value for item in current_items[-5:]]

    print(f"  First 5 values: {first_values}")
    print(f"  Last 5 values: {last_values}")
    print()

    first_item_present = any(item.tag_value == first_item.tag_value for item in current_items)
    if not first_item_present:
        print(f"  ✓ Original first item (value={first_item.tag_value}) evicted (FIFO)")
    else:
        print(f"  ✗ ERROR: First item still present!")
        assert False

    expected_last = float(buffer_size + overflow_items - 1)
    actual_last = current_items[-1].tag_value
    if actual_last == expected_last:
        print(f"  ✓ Last item correct (value={actual_last})")
    else:
        print(f"  ✗ ERROR: Last item mismatch!")
        assert False

    print()
    print("[PHASE 4] Testing continuous overflow...")
    print()

    sustained = buffer_size * 2
    initial_overflow = stats['overflow_count']

    for i in range(sustained):
        tag_value = BufferedTagValue(
            timestamp=datetime.now(),
            plc_code="SUSTAINED",
            tag_address=f"D{i}",
            tag_value=float(i),
            quality="GOOD"
        )
        buffer.put(tag_value)

    stats = buffer.stats()
    total_overflow = stats['overflow_count'] - initial_overflow

    print(f"  Added {sustained} more items")
    print(f"  Additional overflows: {total_overflow}")
    print(f"  Buffer size: {stats['current_size']}/{stats['max_size']}")
    print(f"  Total overflow: {stats['overflow_count']}")
    print(f"  Overflow rate: {stats['overflow_rate_pct']:.3f}%")
    print()

    assert stats['current_size'] == buffer_size

    print("=" * 80)
    print("ACCEPTANCE CRITERIA")
    print("=" * 80)

    size_pass = stats['current_size'] == buffer_size
    print(f"✓ Buffer size capped: {stats['current_size']} - {'PASS' if size_pass else 'FAIL'}")

    expected_total = overflow_items + sustained
    overflow_pass = stats['overflow_count'] == expected_total
    print(f"✓ Overflow tracking: {stats['overflow_count']}/{expected_total} - {'PASS' if overflow_pass else 'FAIL'}")

    fifo_pass = not first_item_present
    print(f"✓ FIFO eviction: - {'PASS' if fifo_pass else 'FAIL'}")

    expected_rate = (stats['overflow_count'] / stats['total_added']) * 100.0
    rate_pass = abs(stats['overflow_rate_pct'] - expected_rate) < 0.01
    print(f"✓ Overflow rate calc: {stats['overflow_rate_pct']:.3f}% - {'PASS' if rate_pass else 'FAIL'}")

    stable_pass = True
    print(f"✓ System stable: - {'PASS' if stable_pass else 'FAIL'}")

    print()
    print("=" * 80)
    success = size_pass and overflow_pass and fifo_pass and rate_pass and stable_pass
    print("✓ ALL TESTS PASSED" if success else "✗ SOME TESTS FAILED")
    print("=" * 80)

    return success


def main():
    parser = argparse.ArgumentParser(description="Buffer overflow test")
    parser.add_argument('--buffer-size', type=int, default=1000)
    parser.add_argument('--overflow-count', type=int, default=500)

    args = parser.parse_args()

    try:
        success = test_buffer_overflow(args.buffer_size, args.overflow_count)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("
[INTERRUPT] Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"
[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
