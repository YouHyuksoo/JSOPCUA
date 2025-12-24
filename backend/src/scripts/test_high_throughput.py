"""
High-Throughput Performance Test

Simulates 1,000+ tag values per second to verify:
- Write latency < 2 seconds
- Buffer utilization < 80%
- No buffer overflow under normal load
- Throughput metrics accuracy

Usage:
    python backend/src/scripts/test_high_throughput.py [--duration SECONDS] [--rate VALUES_PER_SEC]
"""

import sys
import os
import time
import threading
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_src))

from buffer.circular_buffer import CircularBuffer
from buffer.models import BufferedTagValue
from oracle_writer.metrics import RollingMetrics
from oracle_writer.writer import OracleWriter
from oracle_writer.connection_pool import OracleConnectionPool
from oracle_writer.backup import CSVBackup
from oracle_writer.config import load_config_from_env, load_buffer_config_from_env

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class HighThroughputSimulator:
    """
    Simulates high-throughput data generation for performance testing

    Generates tag values at a specified rate to stress-test the buffer and writer.
    """

    def __init__(
        self,
        circular_buffer: CircularBuffer,
        target_rate: int = 1000,
        duration_seconds: int = 60
    ):
        """
        Initialize simulator

        Args:
            circular_buffer: CircularBuffer to write to
            target_rate: Target values per second (default: 1000)
            duration_seconds: Test duration in seconds (default: 60)
        """
        self.circular_buffer = circular_buffer
        self.target_rate = target_rate
        self.duration_seconds = duration_seconds

        self.stop_event = threading.Event()
        self._thread = None

        self.generated_count = 0
        self.overflow_detected = 0

    def start(self):
        """Start the simulator thread"""
        print(f"[SIMULATOR] Starting high-throughput simulator (rate={self.target_rate}/s, duration={self.duration_seconds}s)")
        self.stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="Simulator", daemon=False)
        self._thread.start()

    def stop(self):
        """Stop the simulator thread"""
        print("[SIMULATOR] Stopping simulator...")
        self.stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    def _run(self):
        """
        Main simulator loop

        Generates tag values at the target rate using precise timing.
        """
        start_time = time.time()
        end_time = start_time + self.duration_seconds

        # Calculate sleep interval to achieve target rate
        interval = 1.0 / self.target_rate

        next_generation_time = start_time

        while not self.stop_event.is_set() and time.time() < end_time:
            current_time = time.time()

            if current_time >= next_generation_time:
                # Generate a tag value
                tag_value = self._generate_tag_value()

                # Add to buffer
                success = self.circular_buffer.put(tag_value)

                if not success:
                    self.overflow_detected += 1

                self.generated_count += 1

                # Schedule next generation
                next_generation_time += interval

            # Sleep briefly to avoid busy-waiting
            sleep_time = min(0.001, max(0, next_generation_time - time.time()))
            time.sleep(sleep_time)

        elapsed = time.time() - start_time
        actual_rate = self.generated_count / elapsed if elapsed > 0 else 0

        print(f"[SIMULATOR] Stopped. Generated {self.generated_count} values in {elapsed:.1f}s (actual rate: {actual_rate:.1f}/s)")

        if self.overflow_detected > 0:
            print(f"[SIMULATOR] WARNING: {self.overflow_detected} buffer overflows detected")

    def _generate_tag_value(self) -> BufferedTagValue:
        """
        Generate a simulated tag value

        Returns:
            BufferedTagValue with realistic data
        """
        # Cycle through 100 different tags
        tag_id = self.generated_count % 100

        return BufferedTagValue(
            timestamp=datetime.now(),
            plc_code=f"PLC{(tag_id // 10) + 1:02d}",
            tag_address=f"D{100 + tag_id}",
            tag_value=float(tag_id * 100 + (self.generated_count % 10)),
            quality="GOOD"
        )


def run_performance_test(
    target_rate: int = 1000,
    duration: int = 60,
    batch_size: int = 500,
    write_interval: float = 0.5
):
    """
    Run high-throughput performance test

    Args:
        target_rate: Target generation rate (values/second)
        duration: Test duration in seconds
        batch_size: Batch size for Oracle writer
        write_interval: Write interval in seconds
    """
    print("=" * 80)
    print("HIGH-THROUGHPUT PERFORMANCE TEST")
    print("=" * 80)
    print(f"Target rate: {target_rate} values/second")
    print(f"Duration: {duration} seconds")
    print(f"Expected total: {target_rate * duration} values")
    print(f"Batch size: {batch_size}")
    print(f"Write interval: {write_interval}s")
    print("=" * 80)
    print()

    # Load configuration
    try:
        oracle_config = load_config_from_env()
        buffer_config = load_buffer_config_from_env()
    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        print("[ERROR] Please set Oracle environment variables in .env")
        return False

    # Create components
    print("[SETUP] Creating buffer and writer components...")

    circular_buffer = CircularBuffer(maxsize=buffer_config['buffer_max_size'])
    metrics = RollingMetrics(window_seconds=300)  # 5-minute window

    try:
        connection_pool = OracleConnectionPool(oracle_config)
    except Exception as e:
        print(f"[ERROR] Failed to create Oracle connection pool: {e}")
        print("[ERROR] Ensure Oracle database is accessible")
        return False

    csv_backup = CSVBackup(backup_dir=buffer_config['backup_file_path'])

    oracle_writer = OracleWriter(
        circular_buffer=circular_buffer,
        connection_pool=connection_pool,
        metrics=metrics,
        csv_backup=csv_backup,
        batch_size=batch_size,
        write_interval=write_interval
    )

    # Create simulator
    simulator = HighThroughputSimulator(
        circular_buffer=circular_buffer,
        target_rate=target_rate,
        duration_seconds=duration
    )

    print("[SETUP] Components created successfully")
    print()

    # Start components
    print("[START] Starting Oracle writer...")
    oracle_writer.start()
    time.sleep(1.0)  # Wait for writer to initialize

    print("[START] Starting data simulator...")
    simulator.start()

    # Monitor progress
    print()
    print("[MONITOR] Test in progress...")
    print()
    print(f"{'Time (s)':<10} {'Generated':<12} {'Buffer':<10} {'Util %':<10} {'Writes':<10} {'Latency (ms)':<15} {'Throughput/s':<15}")
    print("-" * 100)

    start_time = time.time()
    last_print_time = start_time

    while True:
        current_time = time.time()
        elapsed = current_time - start_time

        if elapsed >= duration:
            break

        # Print stats every 5 seconds
        if current_time - last_print_time >= 5.0:
            buffer_stats = circular_buffer.stats()
            writer_stats = oracle_writer.get_stats()
            metrics_stats = writer_stats['metrics']

            print(f"{elapsed:<10.1f} "
                  f"{simulator.generated_count:<12} "
                  f"{buffer_stats['current_size']:<10} "
                  f"{buffer_stats['utilization_pct']:<10.1f} "
                  f"{metrics_stats['total_successful_writes']:<10} "
                  f"{metrics_stats['avg_write_latency_ms']:<15.1f} "
                  f"{metrics_stats['throughput_items_per_sec']:<15.1f}")

            last_print_time = current_time

        time.sleep(0.5)

    print()
    print("[STOP] Test duration complete, stopping components...")

    # Stop components
    simulator.stop()

    # Wait for buffer to drain
    print("[DRAIN] Waiting for buffer to drain...")
    drain_start = time.time()
    while circular_buffer.size() > 0 and time.time() - drain_start < 30:
        time.sleep(0.5)
        print(f"  Buffer size: {circular_buffer.size()}", end='\r')

    print()

    oracle_writer.stop(timeout=15.0)

    # Final statistics
    print()
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    buffer_stats = circular_buffer.stats()
    writer_stats = oracle_writer.get_stats()
    metrics_stats = writer_stats['metrics']

    print()
    print("Generation Statistics:")
    print(f"  Total generated: {simulator.generated_count}")
    print(f"  Target: {target_rate * duration}")
    print(f"  Actual rate: {simulator.generated_count / duration:.1f} values/s")
    print(f"  Buffer overflows: {simulator.overflow_detected}")

    print()
    print("Buffer Statistics:")
    print(f"  Final size: {buffer_stats['current_size']}")
    print(f"  Max size: {buffer_stats['max_size']}")
    print(f"  Final utilization: {buffer_stats['utilization_pct']:.1f}%")
    print(f"  Overflow count: {buffer_stats['overflow_count']}")
    print(f"  Total added: {buffer_stats['total_added']}")

    print()
    print("Writer Statistics (5-minute window):")
    print(f"  Total writes: {metrics_stats['total_successful_writes']}")
    print(f"  Failed writes: {metrics_stats['total_failed_writes']}")
    print(f"  Success rate: {metrics_stats['success_rate_pct']:.1f}%")
    print(f"  Total items written: {metrics_stats['total_items_written']}")
    print(f"  Avg batch size: {metrics_stats['avg_batch_size']:.1f}")
    print(f"  Avg write latency: {metrics_stats['avg_write_latency_ms']:.1f} ms")
    print(f"  Throughput: {metrics_stats['throughput_items_per_sec']:.1f} items/s")

    print()
    print("=" * 80)
    print("ACCEPTANCE CRITERIA")
    print("=" * 80)

    # Check acceptance criteria
    success = True

    # Criterion 1: Write latency < 2000 ms
    avg_latency = metrics_stats['avg_write_latency_ms']
    latency_pass = avg_latency < 2000
    print(f"✓ Avg write latency < 2000ms: {avg_latency:.1f}ms - {'PASS' if latency_pass else 'FAIL'}")
    success = success and latency_pass

    # Criterion 2: Buffer utilization < 80%
    max_utilization = buffer_stats['utilization_pct']
    utilization_pass = max_utilization < 80
    print(f"✓ Buffer utilization < 80%: {max_utilization:.1f}% - {'PASS' if utilization_pass else 'FAIL'}")
    success = success and utilization_pass

    # Criterion 3: No buffer overflow (or < 1%)
    overflow_rate = (buffer_stats['overflow_count'] / buffer_stats['total_added'] * 100) if buffer_stats['total_added'] > 0 else 0
    overflow_pass = overflow_rate < 1.0
    print(f"✓ Overflow rate < 1%: {overflow_rate:.3f}% - {'PASS' if overflow_pass else 'FAIL'}")
    success = success and overflow_pass

    # Criterion 4: Write success rate > 99%
    success_rate = metrics_stats['success_rate_pct']
    success_rate_pass = success_rate > 99.0
    print(f"✓ Write success rate > 99%: {success_rate:.1f}% - {'PASS' if success_rate_pass else 'FAIL'}")
    success = success and success_rate_pass

    # Criterion 5: Throughput >= target rate
    actual_throughput = metrics_stats['total_items_written'] / duration if duration > 0 else 0
    throughput_pass = actual_throughput >= (target_rate * 0.95)  # Allow 5% tolerance
    print(f"✓ Throughput >= {target_rate * 0.95:.0f}/s: {actual_throughput:.1f}/s - {'PASS' if throughput_pass else 'FAIL'}")
    success = success and throughput_pass

    print()
    print("=" * 80)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 80)

    return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="High-throughput performance test")
    parser.add_argument('--rate', type=int, default=1000, help='Target generation rate (values/second)')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for Oracle writer')
    parser.add_argument('--write-interval', type=float, default=0.5, help='Write interval in seconds')

    args = parser.parse_args()

    try:
        success = run_performance_test(
            target_rate=args.rate,
            duration=args.duration,
            batch_size=args.batch_size,
            write_interval=args.write_interval
        )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
