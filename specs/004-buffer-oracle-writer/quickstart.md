# Quickstart Guide: Thread-Safe Buffer and Oracle DB Writer

**Date**: 2025-11-02
**Feature**: 004-buffer-oracle-writer

This guide shows how to set up, start, and verify the thread-safe buffer and Oracle writer integration with Feature 3's polling engine.

---

## Prerequisites

1. **Feature 3 (Polling Engine)** is running and collecting data
2. **Oracle Database** 12c+ is accessible with network connectivity
3. **Python 3.11+** environment with dependencies installed
4. **Oracle table `TAG_DATA`** is created (see setup below)

---

## Setup

### Step 1: Create Oracle Table

Connect to your Oracle database and run:

```sql
-- Create TAG_DATA table
CREATE TABLE TAG_DATA (
    tag_name        VARCHAR2(100) NOT NULL,
    tag_value       VARCHAR2(255) NOT NULL,
    timestamp       TIMESTAMP(6) NOT NULL,
    quality         VARCHAR2(20) NOT NULL,
    CONSTRAINT pk_tag_data PRIMARY KEY (tag_name, timestamp)
);

-- Create index for time-range queries
CREATE INDEX idx_tag_data_timestamp ON TAG_DATA(timestamp);

-- Optional: Create index for tag name queries
CREATE INDEX idx_tag_data_tag_name ON TAG_DATA(tag_name);

-- Verify table creation
SELECT table_name FROM user_tables WHERE table_name = 'TAG_DATA';
```

**Expected Output**:
```
TABLE_NAME
-----------
TAG_DATA
```

---

### Step 2: Install Python Dependencies

```bash
# Navigate to project root
cd D:\Project\JSOPCUA

# Install python-oracledb (Thin mode - no Instant Client needed)
pip install python-oracledb

# Verify installation
python -c "import oracledb; print(f'python-oracledb version: {oracledb.__version__}')"
```

**Expected Output**:
```
python-oracledb version: 2.0.0 (or higher)
```

---

### Step 3: Configure Environment Variables

Create or update `.env` file in project root:

```bash
# Oracle Database Connection
ORACLE_HOST=oracle.example.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=XEPDB1
ORACLE_USER=scada_user
ORACLE_PASSWORD=your_secure_password

# Buffer Configuration
BUFFER_MAX_SIZE=10000           # Maximum circular buffer capacity (FR-002)
BUFFER_BATCH_SIZE_MAX=500       # Maximum batch size for write (FR-008)
BUFFER_WRITE_INTERVAL_SEC=0.5   # Write interval in seconds (FR-009)
BUFFER_BATCH_THRESHOLD=500      # Trigger write when buffer reaches this size

# Retry Configuration
ORACLE_RETRY_MAX=3              # Maximum retry attempts
ORACLE_RETRY_BASE_DELAY=1.0     # Base delay for exponential backoff (seconds)

# Backup Configuration
BACKUP_DIR=./backup             # Directory for CSV backup files

# Connection Pool
ORACLE_POOL_MIN=2               # Minimum pool connections
ORACLE_POOL_MAX=5               # Maximum pool connections
ORACLE_POOL_TIMEOUT=10          # Connection timeout (seconds)
```

---

### Step 4: Verify Oracle Connection

Test Oracle connectivity before starting the full system:

```bash
python backend/src/scripts/test_oracle_connection.py
```

**Expected Output**:
```
[INFO] Connecting to Oracle: oracle.example.com:1521/XEPDB1
[INFO] Connection successful
[INFO] Oracle version: Oracle Database 19c Enterprise Edition Release 19.0.0.0.0
[INFO] Testing insert...
[INFO] Insert successful: 1 row(s) affected
[INFO] Testing query...
[INFO] Query result: timestamp=2025-11-02 14:30:45.123456, plc_code=TEST, tag_address=D999, tag_value=12345.0, quality=GOOD
[INFO] Cleaning up test data...
[INFO] Oracle connection test completed successfully
```

---

## Starting the System

### Scenario 1: Start Buffer and Writer with Running Polling Engine

Assumes Feature 3 polling engine is already running and populating DataQueue.

```bash
# Terminal 1: Start polling engine (if not already running)
python backend/src/scripts/start_polling_engine.py

# Terminal 2: Start buffer consumer and Oracle writer
python backend/src/scripts/start_buffer_writer.py
```

**Expected Output (Terminal 2)**:
```
[INFO] Starting Buffer and Oracle Writer...
[INFO] Loading configuration from environment variables
[INFO] Oracle DSN: oracle.example.com:1521/XEPDB1
[INFO] Buffer max size: 100000
[INFO] Batch size range: 100-1000
[INFO] Write interval: 1.0 seconds
[INFO] Creating Oracle connection pool (min=2, max=5)...
[INFO] Oracle connection pool created successfully
[INFO] Starting BufferConsumer thread...
[INFO] BufferConsumer thread started
[INFO] Starting OracleWriter thread...
[INFO] OracleWriter thread started
[INFO] Buffer and Oracle Writer running. Press Ctrl+C to stop.
[INFO] Monitoring: http://localhost:8000/api/buffer/metrics
```

---

### Scenario 2: Integrated Startup Script

Start all components (polling engine + buffer + writer) together:

```bash
python backend/src/scripts/start_all.py
```

**Expected Output**:
```
[INFO] Starting SCADA System...
[INFO] Step 1/3: Initializing polling engine...
[INFO] Polling engine initialized with 3 groups
[INFO] Step 2/3: Starting buffer consumer and Oracle writer...
[INFO] Buffer consumer started
[INFO] Oracle writer started
[INFO] Step 3/3: Starting polling groups...
[INFO] Started polling group: LINE1_PROCESS1 (FIXED, 1000ms)
[INFO] Started polling group: LINE2_PROCESS2 (FIXED, 5000ms)
[INFO] Started polling group: MANUAL_TRIGGER (HANDSHAKE)
[INFO] All systems running. Monitoring available at:
[INFO]   - Polling status: http://localhost:8000/api/polling/status
[INFO]   - Buffer metrics: http://localhost:8000/api/buffer/metrics
[INFO] Press Ctrl+C to stop all systems.
```

---

## Verification

### Check 1: Verify Data in Oracle

Wait 5-10 seconds after starting, then query Oracle:

```sql
-- Check row count
SELECT COUNT(*) AS total_rows FROM tag_values;

-- View recent data
SELECT
    timestamp,
    plc_code,
    tag_address,
    tag_value,
    quality,
    inserted_at
FROM tag_values
WHERE timestamp >= SYSTIMESTAMP - INTERVAL '5' MINUTE
ORDER BY timestamp DESC
FETCH FIRST 10 ROWS ONLY;
```

**Expected Output**:
```
TOTAL_ROWS
----------
      5247

TIMESTAMP                  PLC_CODE  TAG_ADDRESS  TAG_VALUE  QUALITY  INSERTED_AT
-------------------------  --------  -----------  ---------  -------  -------------------------
2025-11-02 14:35:45.123456 PLC01     D100         1234.5     GOOD     2025-11-02 14:35:46.789012
2025-11-02 14:35:45.123456 PLC01     D101         5678.9     GOOD     2025-11-02 14:35:46.789012
2025-11-02 14:35:45.123456 PLC01     D102         9012.3     GOOD     2025-11-02 14:35:46.789012
...
```

**Validation**:
- ✅ `total_rows` increases over time (new data being written)
- ✅ `timestamp` is recent (within last few seconds)
- ✅ `inserted_at` is slightly after `timestamp` (write latency)
- ✅ `quality` is "GOOD" for successful polls

---

### Check 2: Monitor Buffer Metrics API

Query buffer and writer metrics:

```bash
# Using curl
curl http://localhost:8000/api/buffer/metrics

# Using Python
python -c "import requests; print(requests.get('http://localhost:8000/api/buffer/metrics').json())"
```

**Expected Response**:
```json
{
  "buffer": {
    "current_size": 247,
    "max_size": 100000,
    "utilization_pct": 0.247,
    "overflow_count": 0
  },
  "writer": {
    "total_writes": 152,
    "successful_writes": 152,
    "failed_writes": 0,
    "success_rate_pct": 100.0,
    "avg_batch_size": 487.3,
    "avg_write_latency_ms": 342.1,
    "last_write_time": "2025-11-02T14:35:46.123456"
  },
  "backup": {
    "file_count": 0
  }
}
```

**Validation**:
- ✅ `buffer.current_size` fluctuates (data flowing through)
- ✅ `buffer.utilization_pct` < 80% (not approaching overflow)
- ✅ `buffer.overflow_count` = 0 (no data loss)
- ✅ `writer.success_rate_pct` > 99% (high reliability)
- ✅ `writer.avg_write_latency_ms` < 2000 (under 2 second target)
- ✅ `backup.file_count` = 0 (Oracle healthy, no failures)

---

### Check 3: Verify Continuous Operation

Monitor for 5 minutes to confirm stability:

```bash
# Watch metrics update every 5 seconds
watch -n 5 curl -s http://localhost:8000/api/buffer/metrics | jq .
```

**Expected Behavior**:
- `buffer.current_size`: Fluctuates between 0-1000 (depending on polling rate)
- `writer.total_writes`: Increases steadily (~60 writes per minute at 1-second interval)
- `writer.success_rate_pct`: Remains >99%
- `writer.last_write_time`: Updates every 1-2 seconds

---

## Testing Failure Scenarios

### Test 1: Oracle Database Outage (Backup CSV Creation)

Simulate Oracle failure to verify backup mechanism:

**Step 1: Stop Oracle Database**
```bash
# On Oracle server
sudo systemctl stop oracle-xe
# OR disconnect network to Oracle host
```

**Step 2: Observe System Behavior**
```bash
# Check application logs
tail -f backend/logs/buffer_writer.log
```

**Expected Log Output**:
```
[INFO] Batch write attempt 1/3...
[ERROR] Oracle write failed (attempt 1/3): ORA-12170: TNS:Connect timeout occurred
[INFO] Retrying in 1.0 seconds...
[INFO] Batch write attempt 2/3...
[ERROR] Oracle write failed (attempt 2/3): ORA-12170: TNS:Connect timeout occurred
[INFO] Retrying in 2.0 seconds...
[INFO] Batch write attempt 3/3...
[ERROR] Oracle write failed (attempt 3/3): ORA-12170: TNS:Connect timeout occurred
[INFO] Retrying in 4.0 seconds...
[ERROR] All 3 retries exhausted, saving to CSV backup
[INFO] Saved 523 items to ./backup/backup_20251102_143052.csv
[INFO] Continuing operation...
```

**Step 3: Verify Backup File**
```bash
# Check backup directory
ls -lh ./backup/

# Expected output:
# -rw-r--r-- 1 user user  45K Nov  2 14:30 backup_20251102_143052.csv

# View backup file contents
head ./backup/backup_20251102_143052.csv
```

**Expected CSV Content**:
```csv
timestamp,plc_code,tag_address,tag_value,quality,insertion_attempt_time
2025-11-02T14:30:45.123456,PLC01,D100,1234.5,GOOD,2025-11-02T14:30:52.789012
2025-11-02T14:30:45.123456,PLC01,D101,5678.9,GOOD,2025-11-02T14:30:52.789012
...
```

**Step 4: Check Metrics**
```bash
curl http://localhost:8000/api/buffer/metrics | jq .backup
```

**Expected Response**:
```json
{
  "file_count": 1
}
```

**Step 5: Restore Oracle and Verify Recovery**
```bash
# Restart Oracle
sudo systemctl start oracle-xe
```

**Expected Log Output**:
```
[INFO] Batch write attempt 1/3...
[INFO] Batch written successfully: 498 rows, 0 errors
[INFO] Write completed in 342.5 ms
```

**Validation**:
- ✅ System continues running during Oracle outage (no crash)
- ✅ Failed data saved to CSV backup (zero data loss)
- ✅ Automatic recovery when Oracle restarts (no manual intervention)
- ✅ Backup files created with correct format and timestamp

---

### Test 2: Buffer Overflow Protection

Simulate high load with slow Oracle to trigger buffer overflow:

**Step 1: Slow Down Oracle Writes**
```python
# Temporarily modify writer to add delay
# backend/src/oracle_writer/writer.py
def write_batch(self, batch):
    time.sleep(5)  # Simulate slow Oracle
    # ... rest of write logic
```

**Step 2: Increase Polling Rate**
```bash
# Update polling groups to 100ms intervals (very high rate)
# This will produce ~10,000 values/second
```

**Step 3: Observe Buffer Overflow**
```bash
# Watch buffer metrics
watch -n 1 curl -s http://localhost:8000/api/buffer/metrics | jq .buffer
```

**Expected Response (when buffer fills)**:
```json
{
  "current_size": 100000,
  "max_size": 100000,
  "utilization_pct": 100.0,
  "overflow_count": 8234
}
```

**Expected Log Output**:
```
[WARNING] Buffer overflow: discarded oldest data (overflow_count=1)
[WARNING] Buffer overflow: discarded oldest data (overflow_count=2)
[WARNING] Buffer overflow: discarded oldest data (overflow_count=3)
...
[WARNING] Buffer utilization: 100.0% (100000/100000 items)
```

**Step 4: Restore Normal Operation**
```python
# Remove the artificial delay
# Restart the system
```

**Validation**:
- ✅ Buffer size caps at 100,000 items (no unbounded growth)
- ✅ Overflow count increases (oldest data discarded via FIFO)
- ✅ System remains operational (no crash or deadlock)
- ✅ Clear warning logs for operator visibility

---

## Monitoring Dashboard Access (User Story 4)

If Admin UI dashboard is implemented:

```bash
# Open browser to admin dashboard
http://localhost:3000/monitoring/buffer

# Or use API directly
curl http://localhost:8000/api/buffer/metrics
curl http://localhost:8000/api/polling/status
```

**Expected Dashboard Panels**:
1. **Buffer Status**:
   - Current size: 247 / 100,000
   - Utilization: 0.25%
   - Overflow count: 0

2. **Writer Performance**:
   - Total writes: 152
   - Success rate: 100.0%
   - Failed writes: 0
   - Avg batch size: 487 items
   - Avg latency: 342 ms

3. **Backup Files**:
   - File count: 0
   - Total size: 0 MB

---

## Graceful Shutdown

Stop all components cleanly:

```bash
# Send SIGINT (Ctrl+C) to running process
# OR
python backend/src/scripts/stop_all.py
```

**Expected Shutdown Sequence**:
```
[INFO] Shutdown signal received
[INFO] Stopping polling engine...
[INFO] Stopped 3 polling groups
[INFO] Stopping buffer consumer...
[INFO] BufferConsumer thread stopped
[INFO] Flushing remaining buffer data...
[INFO] Buffer contains 247 items, writing final batch...
[INFO] Final batch written: 247 rows
[INFO] Stopping Oracle writer...
[INFO] OracleWriter thread stopped
[INFO] Closing Oracle connection pool...
[INFO] Oracle connection pool closed
[INFO] Final metrics:
[INFO]   Total writes: 152
[INFO]   Success rate: 100.0%
[INFO]   Overflow count: 0
[INFO] Shutdown complete
```

**Validation**:
- ✅ Remaining buffer data is written to Oracle (no data loss)
- ✅ All threads terminate within 5 seconds
- ✅ Oracle connections properly closed
- ✅ Final metrics logged for audit

---

## Troubleshooting

### Issue: "Oracle connection timeout"

**Symptoms**: Logs show `ORA-12170: TNS:Connect timeout`

**Solutions**:
1. Verify Oracle host is reachable: `ping oracle.example.com`
2. Check firewall allows port 1521: `telnet oracle.example.com 1521`
3. Verify Oracle service is running: `sudo systemctl status oracle-xe`
4. Check `.env` credentials are correct

---

### Issue: "Buffer utilization constantly at 100%"

**Symptoms**: `buffer.utilization_pct` = 100%, `overflow_count` increasing

**Solutions**:
1. Reduce polling rate (increase intervals in polling groups)
2. Increase buffer size: `BUFFER_MAX_SIZE=200000`
3. Optimize Oracle write performance (check network latency, add indexes)
4. Scale horizontally (add more Oracle writer threads)

---

### Issue: "Backup files not created during Oracle outage"

**Symptoms**: Oracle is down, but no CSV files in `./backup/`

**Solutions**:
1. Check backup directory exists: `ls -ld ./backup`
2. Verify write permissions: `ls -l ./backup`
3. Check disk space: `df -h`
4. Review logs for error messages: `grep -i "backup" backend/logs/buffer_writer.log`

---

### Issue: "Duplicate key violations in Oracle"

**Symptoms**: Logs show `ORA-00001: unique constraint violated`

**Solutions**:
1. **Expected behavior**: Same tag polled at exact same timestamp (microsecond collision)
2. **Handled gracefully**: executemany() with batcherrors=True logs and skips duplicates
3. **No action needed**: Rest of batch is written successfully
4. **If frequent**: Review polling intervals (may be too fast for timestamp precision)

---

## Next Steps

1. **Scale Testing**: Gradually increase polling groups to 10 concurrent groups
2. **Load Testing**: Test sustained 1,000 values/second for 24 hours (SC-005)
3. **Disaster Recovery**: Practice manual CSV recovery to Oracle
4. **Monitoring**: Set up alerts for buffer utilization >80% and write failures
5. **Partitioning**: Implement Oracle table partitioning for high-volume deployments

---

**End of Quickstart Guide**
