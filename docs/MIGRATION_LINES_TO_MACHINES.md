# Database Migration: lines → machines

## 마이그레이션 개요

데이터베이스 테이블명과 컬럼명을 비즈니스 도메인에 맞게 변경했습니다.

### 변경 사항

| 변경 전 | 변경 후 | 설명 |
|---------|---------|------|
| `lines` 테이블 | `machines` 테이블 | 생산 라인 → 생산 설비 |
| `line_code` | `machine_code` | 라인 코드 → 설비 코드 |
| `line_name` | `machine_name` | 라인 이름 → 설비 이름 |
| `description` | `location` | 설명 → 위치 |
| `processes.line_id` | `processes.machine_id` | 외래키 컬럼명 변경 |
| `idx_processes_line_id` | `idx_processes_machine_id` | 인덱스명 변경 |

---

## 마이그레이션 실행 내역

### 실행 날짜
- **2025-01-04**

### 실행 스크립트
- `backend/src/scripts/migrate_lines_to_machines.py`

### 백업 파일
- `backend/config/scada_backup_before_migration.db`

### 마이그레이션 단계

1. ✅ **백업 생성**: 원본 데이터베이스 백업
2. ✅ **뷰 삭제**: `v_tags_with_plc` 뷰 삭제 (재생성 예정)
3. ✅ **테이블 리네임**: `lines` → `machines`
4. ✅ **컬럼 리네임** (machines 테이블):
   - `line_code` → `machine_code`
   - `line_name` → `machine_name`
   - `description` → `location`
5. ✅ **컬럼 리네임** (processes 테이블):
   - `line_id` → `machine_id`
6. ✅ **인덱스 업데이트**:
   - `idx_processes_line_id` 삭제
   - `idx_processes_machine_id` 생성
7. ✅ **뷰 재생성**: 새 스키마로 `v_tags_with_plc` 뷰 재생성
8. ✅ **검증**: 테이블, 컬럼, 데이터 무결성 확인

---

## 영향받은 파일

### 1. 데이터베이스 스키마
- ✅ `backend/config/init_scada_db.sql`

### 2. API 라우트
- ✅ `backend/src/api/machines_routes.py` (전체 SQL 쿼리 업데이트)
- ✅ `backend/src/api/processes_routes.py` (외래키 참조 업데이트)

### 3. Validators
- ✅ `backend/src/database/validators.py`
  - `validate_machine_exists()` 함수
  - `validate_machine_code_unique()` 함수

### 4. 마이그레이션 스크립트
- ✅ `backend/src/scripts/migrate_lines_to_machines.py` (신규 생성)

---

## 마이그레이션 검증 결과

### 데이터베이스 검증
```bash
✓ 'machines' table exists
✓ 'machines' columns: id, machine_code, machine_name, location, is_active, created_at, updated_at
✓ 'processes' has 'machine_id' column
✓ 'machines' table has 1 rows (기존 데이터 보존됨)
```

### 뷰 검증
```sql
SELECT machine_code, machine_name, process_code, plc_code
FROM v_tags_with_plc
LIMIT 3;

-- 결과: 정상 작동 (machine_code, machine_name 컬럼 사용)
```

### 외래키 체인 검증
```
machines (id)
  ↓ FK: machine_id
processes (id)
  ↓ FK: process_id
plc_connections (id)
  ↓ FK: plc_id
tags
```

---

## API 엔드포인트 (변경 없음)

마이그레이션은 데이터베이스 내부만 변경했으며, API 엔드포인트는 그대로 유지됩니다:

### Machines API
- `GET /api/machines` - 설비 목록 조회
- `POST /api/machines` - 설비 생성
- `GET /api/machines/{id}` - 설비 조회
- `PUT /api/machines/{id}` - 설비 수정
- `DELETE /api/machines/{id}` - 설비 삭제

### Processes API
- `GET /api/processes?machine_id={id}` - 특정 설비의 공정 조회
- 기타 CRUD 엔드포인트

---

## 롤백 방법

만약 문제가 발생하면 백업 파일로 복원:

```bash
# Windows
copy "backend\config\scada_backup_before_migration.db" "backend\config\scada.db"

# Linux/Mac
cp backend/config/scada_backup_before_migration.db backend/config/scada.db
```

---

## 주의사항

1. **스키마 파일 동기화**: `init_scada_db.sql`이 최신 스키마를 반영합니다
2. **기존 데이터 보존**: 모든 기존 데이터는 그대로 유지됩니다
3. **외래키 제약**: `PRAGMA foreign_keys = ON`이 활성화된 상태에서 마이그레이션됨
4. **API 호환성**: API 엔드포인트와 응답 모델은 변경 없음

---

## 다음 단계

✅ **마이그레이션 완료** - 추가 작업 불필요

모든 API 라우트, validators, 스키마 파일이 업데이트되었으며, 데이터베이스 마이그레이션이 성공적으로 완료되었습니다.
