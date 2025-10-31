# JSScada Backend

JSScada 시스템의 Python 백엔드 컴포넌트입니다.

## 요구사항

- Python 3.11 이상
- SQLite 3.40 이상 (Python 표준 라이브러리 포함)

## 설치

1. 가상 환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 변경
```

## 데이터베이스 초기화

```bash
# 데이터베이스 스키마 생성
python src/scripts/init_database.py

# 샘플 데이터 생성 (선택사항)
python src/scripts/create_sample_data.py
```

## 프로젝트 구조

```
backend/
├── config/           # 설정 파일 및 SQLite 데이터베이스
│   ├── init_scada_db.sql
│   └── scada.db      # SQLite 데이터베이스 (자동 생성됨)
├── logs/            # 로그 파일
├── src/
│   ├── database/    # 데이터베이스 모델 및 관리
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── sqlite_manager.py
│   └── scripts/     # 유틸리티 스크립트
│       ├── __init__.py
│       ├── init_database.py
│       ├── init_project_structure.py
│       ├── import_tags_csv.py
│       └── create_sample_data.py
├── tests/           # 테스트 코드
├── .env.example     # 환경 변수 템플릿
├── requirements.txt # Python 의존성
└── README.md
```

## 데이터베이스 스키마

### 테이블

1. **lines** - 생산 라인 정보
2. **processes** - 공정 정보 (14자리 설비 코드)
3. **plc_connections** - PLC 연결 정보
4. **tags** - PLC 태그 정보 (최대 3,491개 지원)
5. **polling_groups** - 폴링 그룹 설정 (FIXED/HANDSHAKE 모드)

### SQLite 데이터베이스 쿼리 예제

```bash
# SQLite CLI로 데이터베이스 열기
sqlite3 config/scada.db

# 테이블 목록 확인
.tables

# 스키마 확인
.schema lines

# 데이터 조회
SELECT * FROM lines;
SELECT * FROM processes WHERE line_id = 1;
SELECT * FROM v_tags_with_plc WHERE line_name = 'TUB 가공 라인';

# 종료
.quit
```

## CSV 일괄 태그 등록

```bash
# CSV 파일에서 태그 가져오기
python src/scripts/import_tags_csv.py path/to/tags.csv
```

CSV 파일 형식:
```csv
PLC_CODE,TAG_ADDRESS,TAG_NAME,UNIT,SCALE,MACHINE_CODE
PLC01,D100,온도센서1,°C,1.0,KRCWO12ELOA101
PLC01,D101,압력센서1,bar,0.1,KRCWO12ELOA101
```

## 데이터베이스 백업

```bash
# 백업 스크립트 실행 (Linux/Mac)
bash scripts/backup_sqlite.sh

# 또는 수동 백업
sqlite3 config/scada.db ".backup 'config/scada_backup_$(date +%Y%m%d_%H%M%S).db'"
```

## 개발

### 테스트 실행

```bash
pytest tests/
pytest tests/ -v --cov=src
```

### 코드 스타일

- PEP 8 준수
- Type hints 사용 권장
- Docstring 작성 (Google 스타일)

## 라이선스

Proprietary
