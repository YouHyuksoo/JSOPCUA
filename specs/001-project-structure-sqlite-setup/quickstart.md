# Quickstart: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정

**Feature**: 001-project-structure-sqlite-setup
**Date**: 2025-10-31

## Prerequisites

- Python 3.11 이상
- Node.js 20 이상
- SQLite 3.40 이상 (보통 Python에 포함됨)

## 5분 빠른 시작

### 1. 프로젝트 디렉토리 생성 (30초)

```bash
# 루트 디렉토리에서 실행
python backend/src/scripts/init_project_structure.py
```

### 2. SQLite 데이터베이스 초기화 (10초)

```bash
cd backend
python src/scripts/init_database.py
```

### 3. 샘플 데이터 삽입 (5초)

```bash
python src/scripts/create_sample_data.py
```

### 4. 검증

```bash
# SQLite 데이터베이스 확인
sqlite3 config/scada.db "SELECT COUNT(*) FROM tags;"
# 출력: 최소 10개 태그 확인

# 테이블 목록 확인
sqlite3 config/scada.db ".tables"
# 출력: lines, processes, plc_connections, tags, polling_groups
```

## 상세 사용법

### CSV에서 태그 가져오기

```bash
# CSV 파일 준비 (UTF-8 인코딩)
# 예: data/tags.csv

# 가져오기 실행
python src/scripts/import_tags_csv.py data/tags.csv

# 결과 확인
sqlite3 config/scada.db "SELECT COUNT(*) FROM tags;"
```

### 데이터베이스 백업

```bash
# 백업 생성
bash scripts/backup_sqlite.sh

# 백업 파일: backups/scada_YYYYMMDD_HHMMSS.db
```

### 데이터베이스 재초기화

```bash
# 주의: 모든 데이터 삭제됨
rm config/scada.db
python src/scripts/init_database.py
```

## 통합 시나리오

### 시나리오 1: 새 라인 추가

```python
import sqlite3

conn = sqlite3.connect('config/scada.db')
cursor = conn.cursor()

# 1. 라인 추가
cursor.execute("""
    INSERT INTO lines (line_code, line_name, location)
    VALUES ('LINE02', '조립 라인', '창원 공장')
""")

# 2. 공정 추가
cursor.execute("""
    INSERT INTO processes (line_id, process_sequence, process_code, process_name, equipment_type)
    VALUES (2, 1, 'KRCWO13ELOA201', 'Assembly Station 1', 'ASM')
""")

conn.commit()
conn.close()
```

### 시나리오 2: 폴링 그룹 생성

```python
# 1. PLC 연결 먼저 확인
cursor.execute("SELECT id FROM plc_connections WHERE plc_code = 'PLC01'")
plc_id = cursor.fetchone()[0]

# 2. 폴링 그룹 생성
cursor.execute("""
    INSERT INTO polling_groups (
        group_name, plc_id, mode, interval_ms,
        trigger_bit_address, trigger_bit_offset
    ) VALUES (
        'Upper Loading - 트리거', ?, 'HANDSHAKE', 500, 'B0110', 0
    )
""", (plc_id,))

group_id = cursor.lastrowid

# 3. 태그를 폴링 그룹에 할당
cursor.execute("""
    UPDATE tags
    SET polling_group_id = ?
    WHERE plc_id = ? AND tag_division = '부하율'
""", (group_id, plc_id))

conn.commit()
```

## 문제 해결

### 문제: Foreign Key 제약 오류

**원인**: Foreign Key 제약이 비활성화됨

**해결**:
```python
conn = sqlite3.connect('config/scada.db')
conn.execute("PRAGMA foreign_keys = ON")
```

### 문제: UTF-8 인코딩 오류

**원인**: CSV 파일이 UTF-8이 아닌 다른 인코딩

**해결**:
```bash
# CSV 파일을 UTF-8로 변환
iconv -f CP949 -t UTF-8 tags_cp949.csv > tags_utf8.csv
```

### 문제: 디스크 공간 부족

**확인**:
```bash
du -sh config/scada.db
```

**해결**: 오래된 데이터 정리 또는 디스크 공간 확보

## 다음 단계

1. `/speckit.tasks` - 작업 분해 (tasks.md 생성)
2. `/speckit.implement` - 구현 실행
3. 백엔드 폴링 엔진 기능 개발 (Feature 2)
