# Research: 프로젝트 기본 구조 및 SQLite 데이터베이스 설정

**Feature**: 001-project-structure-sqlite-setup
**Date**: 2025-10-31
**Purpose**: Technical decisions and best practices research

## Research Areas

### 1. SQLite 스키마 설계 Best Practices

**Decision**: Foreign Key 제약을 활성화하고 CASCADE/SET NULL 사용

**Rationale**:
- SQLite는 기본적으로 Foreign Key 제약이 비활성화되어 있음
- `PRAGMA foreign_keys = ON` 명령으로 활성화 필요
- CASCADE 삭제를 사용하여 라인 삭제 시 모든 하위 데이터 자동 정리
- SET NULL을 사용하여 폴링 그룹 삭제 시 태그는 유지하되 연결만 해제

**Alternatives Considered**:
- 애플리케이션 레벨에서 관계 관리: 복잡하고 오류 가능성 높음
- 제약 조건 없이 설계: 데이터 무결성 보장 불가

**Implementation**:
```sql
PRAGMA foreign_keys = ON;

CREATE TABLE processes (
    ...
    FOREIGN KEY (line_id) REFERENCES lines(id) ON DELETE CASCADE
);

CREATE TABLE tags (
    ...
    FOREIGN KEY (polling_group_id) REFERENCES polling_groups(id) ON DELETE SET NULL
);
```

---

### 2. 14자리 설비 코드 체계

**Decision**: VARCHAR(50)으로 process_code 컬럼 정의

**Rationale**:
- 14자리 고정 길이이지만 향후 확장 가능성 고려
- CHAR(14)보다 VARCHAR(50)이 유연성 제공
- 데이터베이스 레벨에서 길이 검증보다 애플리케이션 레벨 검증 권장

**Format**: KRCWO12ELOA101
- KR: 국가 코드 (2자리)
- CWO: 공장 코드 (3자리)
- 12: 라인 번호 (2자리)
- ELO: 설비 타입 (3자리)
- A: 상세 구분 (1자리)
- 101: 설비 번호 (3자리)

**Validation**: Python에서 정규표현식으로 검증

---

### 3. 대량 CSV 가져오기 전략

**Decision**: 배치 INSERT + 트랜잭션 사용

**Rationale**:
- 3,491개 태그를 한 번에 삽입하면 성능 저하
- 트랜잭션으로 묶어서 500-1000개 단위로 커밋
- executemany() 사용으로 성능 최적화

**Implementation Pattern**:
```python
conn = sqlite3.connect('scada.db')
cursor = conn.cursor()

try:
    batch = []
    for row in csv_reader:
        batch.append((row['plc_code'], row['tag_address'], ...))

        if len(batch) >= 500:
            cursor.executemany("INSERT INTO tags (...) VALUES (?, ?, ...)", batch)
            conn.commit()
            batch = []

    if batch:
        cursor.executemany("INSERT INTO tags (...) VALUES (?, ?, ...)", batch)
        conn.commit()

except Exception as e:
    conn.rollback()
    raise
finally:
    conn.close()
```

**Performance**: 3,491개 태그를 5분 이내 삽입 목표

---

### 4. UTF-8 인코딩 처리

**Decision**: Python sqlite3 모듈의 기본 UTF-8 인코딩 사용

**Rationale**:
- Python 3.x의 sqlite3 모듈은 기본적으로 UTF-8 인코딩
- 명시적 인코딩 지정 불필요
- CSV 파일은 UTF-8로 저장 권장

**CSV 읽기**:
```python
with open('tags.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    ...
```

**특수 문자 테스트**:
- 한글: "Upper셔틀#1 유효부하"
- 특수기호: %, °C, ℃
- 모두 정상 저장 및 조회 가능 확인 필요

---

### 5. 인덱스 전략

**Decision**: Foreign Key 컬럼과 자주 조회되는 컬럼에 인덱스 생성

**Rationale**:
- plc_id, process_id, polling_group_id는 JOIN 쿼리에서 자주 사용
- tag_address는 태그 검색 시 사용
- 인덱스로 쿼리 성능 100ms 이내 달성

**Indexes**:
```sql
CREATE INDEX idx_tags_plc ON tags(plc_id);
CREATE INDEX idx_tags_process ON tags(process_id);
CREATE INDEX idx_tags_polling_group ON tags(polling_group_id);
CREATE INDEX idx_tags_address ON tags(tag_address);
CREATE INDEX idx_processes_line ON processes(line_id);
CREATE INDEX idx_plc_connections_process ON plc_connections(process_id);
CREATE INDEX idx_polling_groups_plc ON polling_groups(plc_id);
```

**Trade-off**: 쓰기 성능 약간 감소하지만 읽기 성능 대폭 향상

---

### 6. 프로젝트 디렉토리 초기화 방법

**Decision**: Python 스크립트로 디렉토리 생성 자동화

**Rationale**:
- 수동으로 디렉토리 생성하면 실수 가능성
- os.makedirs(exist_ok=True)로 안전한 디렉토리 생성
- 기본 파일들(README.md, .gitignore 등) 함께 생성

**Implementation**:
```python
import os

def create_project_structure():
    dirs = [
        'backend/src/database',
        'backend/src/scripts',
        'backend/config',
        'backend/logs',
        'backend/tests',
        'frontend-admin/app',
        'frontend-admin/components/ui',
        'frontend-admin/lib',
        'frontend-admin/public',
        'frontend-monitor/app',
        'frontend-monitor/components/ui',
        'frontend-monitor/lib',
        'frontend-monitor/public',
    ]

    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created: {dir_path}")
```

---

### 7. SQLite 파일 위치 및 백업

**Decision**: backend/config/scada.db 위치에 저장, 수동 백업

**Rationale**:
- config/ 디렉토리는 설정 파일의 표준 위치
- .gitignore에 scada.db 추가하여 버전 관리 제외
- 백업은 간단한 파일 복사로 가능

**Backup Script**:
```bash
# backend/scripts/backup_sqlite.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp backend/config/scada.db "backups/scada_$TIMESTAMP.db"
```

**Backup Frequency**: 수동 (향후 자동화 검토)

---

## Technology Stack Summary

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Backend Language | Python | 3.11+ | 스크립트 및 백엔드 로직 |
| Frontend Framework | Next.js | 14+ | 관리/모니터링 웹 UI |
| Database | SQLite | 3.40+ | 로컬 설정 데이터 저장 |
| Backend Testing | pytest | latest | 백엔드 테스트 |
| Frontend Testing | Jest | latest | 프론트엔드 테스트 |
| CSS Framework | Tailwind CSS | latest | UI 스타일링 |
| UI Components | shadcn/ui | latest | 재사용 가능한 컴포넌트 |

---

## Risks and Mitigations

### Risk 1: SQLite 동시 접근 제한
- **Risk**: 여러 프로세스가 동시에 쓰기 시도 시 락킹
- **Mitigation**: 단일 프로세스만 쓰기 수행, 읽기는 동시 접근 가능

### Risk 2: 3,491개 태그 CSV 가져오기 실패
- **Risk**: CSV 파일 형식 오류, 인코딩 문제
- **Mitigation**: 상세한 오류 로깅, 트랜잭션 롤백, 유효성 검증

### Risk 3: 디스크 공간 부족
- **Risk**: SQLite 파일 크기 증가로 디스크 부족
- **Mitigation**: 초기 50MB 이하 유지, 향후 10,000개 태그 기준으로도 충분한 공간

---

## Open Questions

*모든 기술적 결정사항이 명확하므로 추가 조사 필요 없음*

---

## References

- [SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html)
- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
