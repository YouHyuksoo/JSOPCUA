"""
Test polling group creation directly
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.api.models import PollingGroupCreate

# Test data
test_data = {
    "name": "Test Group",
    "polling_interval": 1000,
    "is_active": True,
    "plc_id": 1,
    "tag_ids": [1, 2, 3]
}

try:
    group = PollingGroupCreate(**test_data)
    print(f"✓ Model validation passed!")
    print(f"  group_name: {group.group_name}")
    print(f"  interval_ms: {group.interval_ms}")
    print(f"  enabled: {group.enabled}")
    print(f"  plc_id: {group.plc_id}")
    print(f"  tag_ids: {group.tag_ids}")
except Exception as e:
    print(f"✗ Model validation failed: {e}")
    import traceback
    traceback.print_exc()
