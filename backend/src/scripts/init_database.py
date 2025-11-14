"""
SQLite 데이터베이스 초기화 스크립트
User Story 2: SQLite 데이터베이스 스키마 생성

실행: python src/scripts/init_database.py
"""
import sys
from pathlib import Path
import logging

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.sqlite_manager import SQLiteManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """데이터베이스 초기화 (스키마 생성)"""

    # 데이터베이스 경로
    db_path = project_root / "data" / "scada.db"

    # V2 스키마 사용 (machines 테이블 제거)
    sql_script_path = project_root / "config" / "init_scada_db_v2.sql"

    # V2 스키마가 없으면 기존 스키마 사용
    if not sql_script_path.exists():
        sql_script_path = project_root / "config" / "init_scada_db.sql"
        logger.warning("V2 schema not found, using V1 schema")

    logger.info(f"Database path: {db_path}")
    logger.info(f"SQL script path: {sql_script_path}")

    # SQL 스크립트 파일 확인
    if not sql_script_path.exists():
        logger.error(f"SQL script not found: {sql_script_path}")
        return False

    # SQL 스크립트 읽기
    with open(sql_script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    logger.info("SQL script loaded successfully")

    # 데이터베이스 매니저 생성
    manager = SQLiteManager(str(db_path))

    # 데이터베이스가 이미 존재하는지 확인
    if manager.database_exists():
        logger.warning(f"Database already exists: {db_path}")

        # 테이블 목록 확인
        try:
            table_names = manager.get_table_names()
            if table_names:
                logger.info(f"Existing tables: {', '.join(table_names)}")
        except:
            pass

        response = input("Do you want to recreate the database? This will DELETE all existing data! (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Database initialization cancelled")
            logger.info("If you need to initialize the database, delete the file manually:")
            logger.info(f"  rm {db_path}")
            return False
        else:
            logger.info("Recreating database...")
            db_path.unlink()

    # SQL 스크립트 실행
    try:
        logger.info("Executing SQL script...")
        manager.execute_script(sql_script)
        logger.info("✓ Database schema created successfully")
    except Exception as e:
        logger.error(f"Failed to create database schema: {e}")
        return False

    # 검증: 테이블 목록 확인
    logger.info("\n" + "=" * 60)
    logger.info("Verifying Database Schema")
    logger.info("=" * 60)

    # V2 스키마 테이블 (machines 테이블 제거됨)
    expected_tables = [
        "processes",
        "plc_connections",
        "tags",
        "polling_groups"
    ]

    table_names = manager.get_table_names()
    logger.info(f"Created tables: {', '.join(table_names)}")

    all_tables_exist = True
    for table in expected_tables:
        if table in table_names:
            count = manager.get_table_count(table)
            logger.info(f"✓ Table '{table}' exists (rows: {count})")
        else:
            logger.error(f"✗ Table '{table}' NOT FOUND")
            all_tables_exist = False

    # 뷰 확인
    view_query = """
        SELECT name FROM sqlite_master
        WHERE type='view' AND name='v_tags_with_plc'
    """
    views = manager.execute_query(view_query)
    if views:
        logger.info(f"✓ View 'v_tags_with_plc' exists")
    else:
        logger.error(f"✗ View 'v_tags_with_plc' NOT FOUND")
        all_tables_exist = False

    # 인덱스 확인
    index_query = """
        SELECT name FROM sqlite_master
        WHERE type='index' AND name LIKE 'idx_%'
    """
    indexes = manager.execute_query(index_query)
    logger.info(f"✓ Created {len(indexes)} indexes: {', '.join([idx['name'] for idx in indexes])}")

    # Foreign Key 확인
    with manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()
        logger.info(f"✓ Foreign Keys status: {'ON' if fk_status[0] else 'OFF'}")

    logger.info("=" * 60)

    if all_tables_exist:
        logger.info("✓ Database initialization completed successfully!")
        logger.info(f"✓ Database file: {db_path}")
        return True
    else:
        logger.error("✗ Database initialization failed - missing tables/views")
        return False


def test_database_operations():
    """데이터베이스 기본 작업 테스트"""

    db_path = project_root / "data" / "scada.db"
    manager = SQLiteManager(str(db_path))

    logger.info("\n" + "=" * 60)
    logger.info("Testing Database Operations")
    logger.info("=" * 60)

    try:
        # 테스트 1: 공정 삽입 (V2 - processes 테이블이 독립적)
        logger.info("Test 1: Insert test process...")
        manager.execute_update(
            "INSERT INTO processes (process_code, process_name) VALUES (?, ?)",
            ("TEST01", "Test Process")
        )
        logger.info("✓ Insert successful")

        # 테스트 2: 조회
        logger.info("Test 2: Query test process...")
        results = manager.execute_query(
            "SELECT * FROM processes WHERE process_code = ?",
            ("TEST01",)
        )
        if results:
            logger.info(f"✓ Query successful - Found: {dict(results[0])}")
        else:
            logger.error("✗ Query failed - No results")

        # 테스트 3: 삭제 (테스트 데이터 정리)
        logger.info("Test 3: Delete test process...")
        manager.execute_update(
            "DELETE FROM processes WHERE process_code = ?",
            ("TEST01",)
        )
        logger.info("✓ Delete successful")

        # 테스트 4: 14자리 설비 코드 테스트 (V2)
        logger.info("Test 4: Insert 14-digit process code...")

        # 14자리 설비 코드로 공정 추가 (V2에서는 line_id 불필요)
        manager.execute_update(
            "INSERT INTO processes (process_code, process_name, location) VALUES (?, ?, ?)",
            ("KRCWO12ELOA101", "Test Process", "Test Location")
        )
        logger.info("✓ 14-digit process code inserted successfully")

        # 테스트 5: UTF-8 한글 테스트
        logger.info("Test 5: UTF-8 Korean text test...")
        process_results = manager.execute_query(
            "SELECT process_name FROM processes WHERE process_code = ?",
            ("KRCWO12ELOA101",)
        )
        if process_results:
            logger.info(f"✓ UTF-8 test successful - Retrieved: {process_results[0]['process_name']}")
        else:
            logger.error("✗ UTF-8 test failed")

        # 테스트 데이터 정리
        manager.execute_update("DELETE FROM processes WHERE process_code = ?", ("KRCWO12ELOA101",))

        logger.info("=" * 60)
        logger.info("✓ All database tests passed!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        logger.info("=" * 60)
        return False


if __name__ == "__main__":
    logger.info("Starting database initialization...")

    # 데이터베이스 초기화
    success = init_database()

    # 기본 작업 테스트
    if success:
        test_success = test_database_operations()
        if test_success:
            logger.info("\n✓ Database is ready to use!")
        else:
            logger.error("\n✗ Database tests failed!")
    else:
        logger.error("\n✗ Database initialization failed!")
