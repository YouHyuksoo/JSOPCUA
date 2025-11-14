# ✅ V2 스키마 마이그레이션 완료

## 실행 날짜
- **2025-01-04 23:35**

## 주요 변경사항

### ❌ 삭제된 테이블
1. **`machines` 테이블** - 불필요한 계층 구조 제거

### ✅ 수정된 테이블

#### 1. `plc_connections` (PLC 마스터)
- **변경 전**: `process_id` FK 보유 (공정에 종속)
- **변경 후**: 독립 테이블, FK 제거
- **추가 컬럼**: `network_no`, `station_no` (MC 프로토콜 파라미터)

#### 2. `processes` (공정 마스터)
- **변경 전**: `machine_id` FK 보유 (설비에 종속)
- **변경 후**: 독립 테이블, FK 제거
- **컬럼 변경**: `description` → `location`

#### 3. `tags` (태그 마스터)
- **변경 전**: `plc_id` FK만 보유, `machine_code` VARCHAR
- **변경 후**: `plc_id` + `process_id` FK 보유 (PLC + 공정 연결)
- **핵심 역할**: PLC와 공정을 연결하는 중심 테이블
- **유일키**: `UNIQUE(plc_id, tag_address)` - 같은 주소가 다른 PLC에서 중복 가능

#### 4. `polling_groups` (폴링 그룹)
- **변경 전**: PLC 참조 없음
- **변경 후**: `plc_id` FK 추가 (PLC별 폴링 그룹)

### ✨ 추가된 테이블

#### 5. `alarm_masters` (알람 마스터) - **신규**
```sql
CREATE TABLE alarm_masters (
    id INTEGER PRIMARY KEY,
    plc_id INTEGER NOT NULL,              -- FK to plc_connections
    process_id INTEGER NOT NULL,          -- FK to processes
    alarm_address VARCHAR(50) NOT NULL,   -- "M100", "M101", "M102"
    alarm_code VARCHAR(50) UNIQUE,        -- "ALM_OVERHEAT_01"
    alarm_message VARCHAR(200),           -- "과열 알람 발생"
    severity VARCHAR(20),                 -- "INFO", "WARNING", "ERROR", "CRITICAL"
    action_guide TEXT,                    -- 조치 가이드
    UNIQUE(plc_id, alarm_address)
);
```

---

## 새로운 데이터 관계

```
플랫 구조 (Independent Masters)
=================================

plc_connections           processes
├─ PLC01                 ├─ KRCWO12ELOA101
├─ PLC02                 ├─ KRCWO12WLDA201
└─ PLC03                 └─ KRCWO12PRSA301


연결 테이블 (Connection Tables)
=================================

tags (PLC + 공정 연결)
├─ plc_id → plc_connections.id
├─ process_id → processes.id
└─ tag_address (D100, W200, ...)

alarm_masters (M 주소 알람)
├─ plc_id → plc_connections.id
├─ process_id → processes.id
└─ alarm_address (M100, M101, ...)

polling_groups (PLC별 폴링 설정)
├─ plc_id → plc_connections.id
└─ tags/alarms와 연결
```

---

## 데이터 등록 순서

### 1단계: 독립 마스터 등록
```sql
-- PLC 등록 (3대)
INSERT INTO plc_connections (plc_code, ip_address, ...) VALUES
  ('PLC01', '192.168.1.10', ...),
  ('PLC02', '192.168.1.11', ...),
  ('PLC03', '192.168.1.12', ...);

-- 공정 등록 (30개)
INSERT INTO processes (process_code, process_name, ...) VALUES
  ('KRCWO12ELOA101', '엘레베이터 A', ...),
  ('KRCWO12WLDA201', '용접기 A', ...),
  ...;
```

### 2단계: 폴링 그룹 등록
```sql
-- PLC별 폴링 그룹 생성
INSERT INTO polling_groups (group_name, plc_id, ...) VALUES
  ('그룹1_PLC01_고정', 1, ...),
  ('그룹2_PLC01_핸드셰이크', 1, ...);
```

### 3단계: 태그 등록 (PLC + 공정 연결)
```sql
-- PLC01 + 엘레베이터A 공정의 태그
INSERT INTO tags (plc_id, process_id, tag_address, ...) VALUES
  (1, 1, 'D100', '온도', ...),
  (1, 1, 'D200', '압력', ...);

-- PLC01 + 용접기A 공정의 태그 (같은 D100 주소 사용 가능)
INSERT INTO tags (plc_id, process_id, tag_address, ...) VALUES
  (1, 2, 'D100', '용접 온도', ...);
```

### 4단계: 알람 등록 (M 주소)
```sql
-- PLC01 + 엘레베이터A 공정의 알람
INSERT INTO alarm_masters (plc_id, process_id, alarm_address, ...) VALUES
  (1, 1, 'M100', 'ALM_OVERHEAT_01', '과열 알람', ...),
  (1, 1, 'M101', 'ALM_PRESSURE_01', '압력 이상', ...);
```

---

## 폴링 동작 흐름 (변경됨)

### 이전 (V1):
```
폴링 그룹 로딩
  ↓
plc_connections (process_id FK로 공정 종속)
  ↓
tags (plc_id만 참조)
```

### 현재 (V2):
```
폴링 그룹 로딩 (plc_id 참조)
  ↓
tags 로딩 (plc_id + process_id로 PLC와 공정 모두 참조)
  ↓
alarm_masters 로딩 (plc_id + process_id로 PLC와 공정 모두 참조)
  ↓
PLC 통신 (pymcprotocol)
  - 태그: batchread_wordunits([D100, D200, W100, ...])
  - 알람: batchread_bitunits([M100, M101, M102, ...])
```

---

## 백업 파일
- `scada_backup_v1_20251104_233518.db`

---

## 다음 단계

### 🚧 아직 완료 안 된 작업:

1. **API 모델 업데이트** (`backend/src/api/models.py`)
   - `MachineCreate`, `MachineResponse` 삭제
   - `ProcessCreate` - `machine_id` 제거
   - `TagCreate` - `process_id` 추가
   - `AlarmMasterCreate`, `AlarmMasterResponse` 추가

2. **API 라우트 업데이트**
   - `machines_routes.py` 삭제
   - `processes_routes.py` - `machine_id` 참조 제거
   - `tags_routes.py` - `process_id` 검증 추가
   - `alarm_routes.py` 생성 (신규)

3. **Validators 업데이트** (`backend/src/database/validators.py`)
   - `validate_machine_exists()` 삭제
   - `validate_machine_code_unique()` 삭제

4. **폴링 엔진 업데이트** (`backend/src/polling/polling_engine.py`)
   - 태그 로딩 시 `process_id` JOIN 반영
   - 알람 마스터 로딩 로직 추가

5. **테스트 데이터 생성**
   - PLC 3대 샘플 데이터
   - 공정 30개 샘플 데이터
   - 태그 샘플 데이터
   - 알람 샘플 데이터

---

## 핵심 개념 확인

✅ **PLC는 공정과 독립적** - plc_connections 테이블은 FK 없음
✅ **공정은 독립적** - processes 테이블은 FK 없음
✅ **Tags가 중심 연결 테이블** - plc_id + process_id로 PLC와 공정 연결
✅ **알람 마스터 별도 관리** - alarm_masters 테이블로 M 주소 관리
✅ **유일키: (plc_id, tag_address)** - 같은 주소가 다른 PLC에서 중복 가능
✅ **SQLite 독립 운영** - Oracle DB 참조 없이 자체 마스터 관리

---

**Status:** ✅ 스키마 마이그레이션 완료, API 업데이트 대기 중
