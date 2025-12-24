# Oracle Writer Module

Batch writer for Oracle Database with retry logic, CSV backup, and performance metrics.

## Overview

The Oracle writer module consumes buffered tag values and writes them to Oracle Database in optimized batches. It includes automatic retry with exponential backoff, CSV backup for failed writes, and comprehensive performance tracking.

## Components

- **writer.py**: Main batch writer with retry logic
- **connection_pool.py**: python-oracledb connection pool (min=2, max=5)
- **metrics.py**: Rolling metrics tracker (5-minute window)
- **backup.py**: CSV backup for failed writes
- **config.py**: Configuration from environment variables

## Features

### Batch Writing

Writes are triggered by either condition (whichever occurs first):
- **Time trigger**: Every 0.5 seconds (configurable)
- **Size trigger**: When buffer reaches 500 items (configurable)

### Retry Logic with Exponential Backoff

Failed writes are automatically retried:
- **Retry count**: 3 attempts
- **Delays**: 1s, 2s, 4s (exponential backoff)
- **CSV backup**: After all retries exhausted

### CSV Backup

Failed batches are saved to timestamped CSV files in format: `backup_YYYYMMDD_HHMMSS.csv`

### Rolling Metrics

Performance metrics tracked over 5-minute rolling window:
- Average batch size
- Average write latency (ms)
- Throughput (items/second)
- Write success/failure counts
- Success rate percentage

## Configuration

Environment variables:
```
ORACLE_HOST=oracle.example.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=XEPDB1
ORACLE_USERNAME=scada_user
ORACLE_PASSWORD=your_password
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=5
BUFFER_BATCH_SIZE=500
BUFFER_WRITE_INTERVAL=0.5
ORACLE_RETRY_MAX=3
BACKUP_FILE_PATH=./backup
```

## Performance Targets

- **Throughput**: 1,000+ values/second
- **Write latency**: < 2 seconds average
- **Success rate**: > 99.9%
- **Batch size**: 100-1000 items (default: 500)

## Testing

```bash
# Test Oracle connectivity
python backend/src/scripts/test_oracle_connection.py

# Test high-throughput performance
python backend/src/scripts/test_high_throughput.py --rate 1000 --duration 60
```

## Monitoring

REST API endpoints:
```bash
curl http://localhost:8000/api/buffer/writer/metrics
curl http://localhost:8000/api/buffer/health
```

## See Also

- [Buffer Module](../buffer/README.md)
- [Quickstart Guide](../../../specs/004-buffer-oracle-writer/quickstart.md)
