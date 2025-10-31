#!/bin/bash
# SQLite 데이터베이스 백업 스크립트
# 실행: bash scripts/backup_sqlite.sh

# 백업 디렉토리
BACKUP_DIR="./backups"
DB_FILE="./config/scada.db"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 타임스탬프 생성
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scada_backup_$TIMESTAMP.db"

# 데이터베이스 파일 존재 확인
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file not found: $DB_FILE"
    exit 1
fi

# 백업 실행
echo "Backing up database..."
echo "Source: $DB_FILE"
echo "Destination: $BACKUP_FILE"

sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

if [ $? -eq 0 ]; then
    echo "✓ Backup completed successfully!"
    echo "Backup file: $BACKUP_FILE"

    # 파일 크기 확인
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup size: $SIZE"

    # 오래된 백업 정리 (30일 이상)
    echo ""
    echo "Cleaning up old backups (older than 30 days)..."
    find "$BACKUP_DIR" -name "scada_backup_*.db" -type f -mtime +30 -delete

    # 남은 백업 개수
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/scada_backup_*.db 2>/dev/null | wc -l)
    echo "Total backups: $BACKUP_COUNT"
else
    echo "✗ Backup failed!"
    exit 1
fi
