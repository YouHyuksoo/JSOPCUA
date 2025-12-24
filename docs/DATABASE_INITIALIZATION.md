# 데이터베이스 초기화 가이드

## 개요

SCADA 시스템의 SQLite 데이터베이스 초기화 과정에 대한 설명입니다.

---

## 데이터베이스 초기화가 필요한가?

### ❌ 초기화 불필요 (대부분의 경우)

다음 조건을 만족하면 **초기화 불필요**:

```bash
# 1. 데이터베이스 파일 존재 확인
ls backend/config/scada.db
# ✅ 파일 존재

# 2. 테이블 생성 확인
python -c "import sqlite3; conn = sqlite3.connect('backend/config/scada.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([t[0] for t in cursor.fetchall()]); conn.close()"
# ✅ ['processes', 'plc_connections', 'tags', 'polling_groups', 'alarm_masters']
```

**결론:** 테이블이 이미 생성되어 있으면 **초기화 스킵 가능**

### ✅ 초기화 필요

다음 경우에만 초기화 필요:

1. **처음 프로젝트를 clone한 경우**
   - `backend/config/scada.db` 파일이 없음
   - Git에서 DB 파일은 무시됨 (.gitignore)

2. **데이터베이스를 완전히 리셋하고 싶은 경우**
   - 모든 데이터를 삭제하고 깨끗한 상태로 시작
   - 스키마 변경 후 재생성

3. **V1 → V2 스키마 업그레이드**
   - `machines` 테이블 제거
   - `alarm_masters` 테이블 추가
   - 독립적인 마스터 테이블 구조로 변경

---

## 현재 스키마 확인

### 스키마 버전 확인

```bash
cd backend
python -c "import sqlite3; conn = sqlite3.connect('config/scada.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name'); tables = [t[0] for t in cursor.fetchall()]; print('V2 Schema' if 'alarm_masters' in tables and 'machines' not in tables else 'V1 Schema'); print('Tables:', tables); conn.close()"
```

**V2 스키마 특징:**
- ✅ `alarm_masters` 테이블 존재
- ❌ `machines` 테이블 없음 (제거됨)
- `processes`와 `plc_connections`가 독립적

**V1 스키마 특징:**
- ❌ `alarm_masters` 테이블 없음
- ✅ `machines` 테이블 존재
- `machines` → `processes` → `plc_connections` 계층 구조

---

## 데이터베이스 초기화 방법

### 방법 1: 초기화 스크립트 사용 (권장)

```bash
cd backend

# V2 스키마로 초기화
python src/scripts/init_database.py
```

**동작:**
1. 기존 DB 파일 확인
2. 있으면 재생성 여부 확인 (yes/no)
3. V2 스키마 (`init_scada_db_v2.sql`) 실행
4. 테이블 생성 확인
5. 기본 CRUD 테스트 실행

**출력 예시:**
```
Database path: d:\Project\JSOPCUA\backend\config\scada.db
Database already exists: d:\Project\JSOPCUA\backend\config\scada.db
Existing tables: processes, plc_connections, tags, polling_groups, alarm_masters
Do you want to recreate the database? This will DELETE all existing data! (yes/no): no
Database initialization cancelled
```

### 방법 2: 수동 초기화

```bash
cd backend

# 1. 기존 DB 삭제
rm config/scada.db

# 2. SQLite로 스키마 생성
sqlite3 config/scada.db < config/init_scada_db_v2.sql

# 3. 확인
sqlite3 config/scada.db "SELECT name FROM sqlite_master WHERE type='table';"
```

### 방법 3: V1 → V2 마이그레이션

```bash
cd backend

# V1 DB를 V2로 업그레이드
python src/scripts/migrate_to_v2_schema.py
```

**동작:**
1. 기존 V1 데이터 백업
2. V2 스키마 생성
3. 데이터 변환 및 이전
4. 관계 재구성

---

## 초기화 후 확인 사항

### 1. 테이블 생성 확인

```bash
python -c "import sqlite3; conn = sqlite3.connect('backend/config/scada.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name'); print([t[0] for t in cursor.fetchall()]); conn.close()"
```

**예상 출력 (V2):**
```
['alarm_masters', 'plc_connections', 'polling_groups', 'processes', 'sqlite_sequence', 'tags']
```

### 2. 데이터 개수 확인

```bash
python -c "
import sqlite3
conn = sqlite3.connect('backend/config/scada.db')
cursor = conn.cursor()
for table in ['processes', 'plc_connections', 'tags', 'polling_groups', 'alarm_masters']:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'{table}: {count}')
conn.close()
"
```

**초기 상태 (빈 DB):**
```
processes: 0
plc_connections: 0
tags: 0
polling_groups: 0
alarm_masters: 0
```

---

## V2 스키마 구조

### 테이블 목록

| 테이블 | 설명 | 독립성 |
|--------|------|--------|
| `processes` | 공정 마스터 (30여개) | ✅ 독립 |
| `plc_connections` | PLC 연결 정보 (3대) | ✅ 독립 |
| `tags` | 태그 마스터 (PLC + 공정 연결) | ❌ 의존 |
| `polling_groups` | 폴링 그룹 설정 | ✅ 독립 |
| `alarm_masters` | M 주소 알람 정의 | ❌ 의존 |

### 주요 관계

```
processes (독립)
    ↓
tags ← plc_connections (독립)
    ↓
polling_groups (독립)

alarm_masters ← plc_connections
              ← processes
```

**핵심:**
- `processes`와 `plc_connections`가 독립적
- `tags`가 PLC와 공정을 연결하는 중간 테이블
- 같은 주소를 여러 PLC에서 사용 가능 (PLC + 주소 = 유일키)

---

## 데이터 입력 방법

### 방법 1: Admin Web UI (권장)

```bash
# Backend 서버 실행
cd backend
python src/api/main.py

# Admin UI 접속
http://localhost:3000
```

**입력 순서:**
1. Processes (공정) 등록
2. PLC Connections (PLC) 등록
3. Tags (태그) 등록 - PLC + 공정 선택
4. Polling Groups (폴링 그룹) 생성
5. Tags를 Polling Groups에 할당

### 방법 2: CSV 일괄 업로드

```bash
# Admin UI에서 CSV 업로드
# Tags 페이지 → Upload CSV
```

**CSV 형식:**
```csv
plc_code,process_code,tag_address,tag_name,tag_type,unit,scale
PLC01,KRCWO12ELOA101,D100,Temperature,INT,°C,0.1
PLC01,KRCWO12ELOA101,D200,Pressure,INT,kPa,1
```

### 방법 3: 샘플 데이터 생성 (개발용)

```bash
cd backend
python src/scripts/create_sample_data.py
```

---

## 문제 해결

### Q: "Database already exists" 오류

**원인:** DB 파일이 이미 존재

**해결:**
```bash
# Option 1: 기존 DB 사용 (초기화 스킵)
# 이미 테이블이 있으면 그대로 사용

# Option 2: 완전히 재생성
rm backend/config/scada.db
python src/scripts/init_database.py
```

### Q: "no such table: machines" 오류

**원인:** V1 코드를 V2 DB에서 실행

**해결:**
```bash
# V2 스키마에서는 machines 테이블이 없음
# processes 테이블을 직접 사용해야 함

# V1 코드:
# SELECT * FROM machines WHERE machine_code = ?

# V2 코드:
# SELECT * FROM processes WHERE process_code = ?
```

### Q: Foreign Key 오류

**원인:** 참조되는 데이터가 없음

**해결:**
```bash
# 입력 순서 준수:
# 1. processes
# 2. plc_connections
# 3. tags (processes + plc_connections 참조)
# 4. alarm_masters (processes + plc_connections 참조)
```

---

## 관련 파일

- **V2 스키마**: `backend/config/init_scada_db_v2.sql`
- **초기화 스크립트**: `backend/src/scripts/init_database.py`
- **마이그레이션**: `backend/src/scripts/migrate_to_v2_schema.py`
- **DB 매니저**: `backend/src/database/sqlite_manager.py`

---

## 요약

1. **대부분의 경우 초기화 불필요** - DB 파일이 이미 존재
2. **초기화 필요 시** - `python src/scripts/init_database.py`
3. **데이터 입력** - Admin Web UI 사용
4. **V2 스키마 특징** - 독립적인 마스터 테이블

**Status:** ✅ V2 스키마 적용 완료

**최종 업데이트:** 2025-11-05
