"""
샘플 데이터 자동 생성 스크립트
User Story 5: 데이터베이스 초기 데이터 설정

실행: python src/scripts/create_sample_data.py
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


def create_sample_data():
    """샘플 데이터 생성"""

    db_path = project_root / "data" / "scada.db"

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        logger.error("Please run init_database.py first")
        return False

    manager = SQLiteManager(str(db_path))

    logger.info("Creating sample data...")

    try:
        # 1. 라인 생성
        logger.info("\n1. Creating sample line...")
        manager.execute_update(
            """
            INSERT INTO lines (line_code, line_name, description, is_active)
            VALUES (?, ?, ?, ?)
            """,
            ("LINE01", "TUB 가공 라인", "TUB 제품 가공 라인", True)
        )
        line_results = manager.execute_query("SELECT id FROM lines WHERE line_code = ?", ("LINE01",))
        line_id = line_results[0]['id']
        logger.info(f"✓ Line created: LINE01 (ID: {line_id})")

        # 2. 공정 생성 (2개)
        logger.info("\n2. Creating sample processes...")
        processes = [
            (line_id, "KRCWO12ELOA101", "Upper Loading", "상부 로딩 공정", 1),
            (line_id, "KRCWO12WLDA201", "Welding", "용접 공정", 2),
        ]

        for process_data in processes:
            manager.execute_update(
                """
                INSERT INTO processes (line_id, process_code, process_name, description, sequence_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (*process_data, True)
            )

        process_results = manager.execute_query("SELECT id, process_code, process_name FROM processes ORDER BY id")
        logger.info(f"✓ Created {len(process_results)} processes:")
        for proc in process_results:
            logger.info(f"  - {proc['process_code']}: {proc['process_name']}")

        # 3. PLC 연결 생성 (2개)
        logger.info("\n3. Creating sample PLC connections...")
        plcs = [
            (process_results[0]['id'], "PLC01", "Upper Loading PLC", "192.168.1.10", 5010),
            (process_results[1]['id'], "PLC02", "Welding PLC", "192.168.1.11", 5010),
        ]

        for plc_data in plcs:
            manager.execute_update(
                """
                INSERT INTO plc_connections (process_id, plc_code, plc_name, ip_address, port, protocol, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (*plc_data, "MC_3E_ASCII", True)
            )

        plc_results = manager.execute_query("SELECT id, plc_code, plc_name, ip_address FROM plc_connections ORDER BY id")
        logger.info(f"✓ Created {len(plc_results)} PLC connections:")
        for plc in plc_results:
            logger.info(f"  - {plc['plc_code']}: {plc['plc_name']} ({plc['ip_address']})")

        # 4. 폴링 그룹 생성 (2개)
        logger.info("\n4. Creating sample polling groups...")
        polling_groups = [
            ("FIXED_1000MS", "FIXED", 1000, "1초 고정 주기 폴링"),
            ("HANDSHAKE_HS1", "HANDSHAKE", 500, "핸드셰이크 모드 폴링"),
        ]

        for pg_data in polling_groups:
            manager.execute_update(
                """
                INSERT INTO polling_groups (group_name, polling_mode, polling_interval_ms, description, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (*pg_data, True)
            )

        pg_results = manager.execute_query("SELECT id, group_name, polling_mode FROM polling_groups ORDER BY id")
        logger.info(f"✓ Created {len(pg_results)} polling groups:")
        for pg in pg_results:
            logger.info(f"  - {pg['group_name']}: {pg['polling_mode']}")

        # 5. 태그 생성 (10개)
        logger.info("\n5. Creating sample tags...")

        # PLC01 태그 (5개) - FIXED 모드
        tags_plc01 = [
            (plc_results[0]['id'], pg_results[0]['id'], "D100", "온도센서1", "INT", "°C", 1.0, 0.0, "KRCWO12ELOA101"),
            (plc_results[0]['id'], pg_results[0]['id'], "D101", "압력센서1", "INT", "bar", 0.1, 0.0, "KRCWO12ELOA101"),
            (plc_results[0]['id'], pg_results[0]['id'], "D102", "유량센서1", "INT", "L/min", 1.0, 0.0, "KRCWO12ELOA101"),
            (plc_results[0]['id'], pg_results[0]['id'], "D103", "레벨센서1", "INT", "%", 0.1, 0.0, "KRCWO12ELOA101"),
            (plc_results[0]['id'], pg_results[0]['id'], "D104", "진동센서1", "INT", "mm/s", 0.01, 0.0, "KRCWO12ELOA101"),
        ]

        # PLC02 태그 (5개) - HANDSHAKE 모드
        tags_plc02 = [
            (plc_results[1]['id'], pg_results[1]['id'], "D200", "온도센서2", "INT", "℃", 1.0, 0.0, "KRCWO12WLDA201"),
            (plc_results[1]['id'], pg_results[1]['id'], "D201", "압력센서2", "INT", "bar", 0.1, 0.0, "KRCWO12WLDA201"),
            (plc_results[1]['id'], pg_results[1]['id'], "D202", "유량센서2", "INT", "L/min", 1.0, 0.0, "KRCWO12WLDA201"),
            (plc_results[1]['id'], pg_results[1]['id'], "D203", "레벨센서2", "INT", "%", 0.1, 0.0, "KRCWO12WLDA201"),
            (plc_results[1]['id'], pg_results[1]['id'], "D204", "진동센서2", "INT", "mm/s", 0.01, 0.0, "KRCWO12WLDA201"),
        ]

        all_tags = tags_plc01 + tags_plc02

        for tag_data in all_tags:
            manager.execute_update(
                """
                INSERT INTO tags (
                    plc_id, polling_group_id, tag_address, tag_name,
                    tag_type, unit, scale, offset, machine_code, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*tag_data, True)
            )

        tag_results = manager.execute_query(
            "SELECT id, tag_address, tag_name, unit FROM tags ORDER BY id"
        )
        logger.info(f"✓ Created {len(tag_results)} tags:")
        for tag in tag_results:
            logger.info(f"  - {tag['tag_address']}: {tag['tag_name']} ({tag['unit']})")

        # 6. 검증
        logger.info("\n" + "=" * 60)
        logger.info("Sample Data Verification")
        logger.info("=" * 60)

        line_count = manager.get_table_count("lines")
        process_count = manager.get_table_count("processes")
        plc_count = manager.get_table_count("plc_connections")
        pg_count = manager.get_table_count("polling_groups")
        tag_count = manager.get_table_count("tags")

        logger.info(f"✓ Lines: {line_count} (expected: >= 1)")
        logger.info(f"✓ Processes: {process_count} (expected: >= 2)")
        logger.info(f"✓ PLC Connections: {plc_count} (expected: >= 2)")
        logger.info(f"✓ Polling Groups: {pg_count} (expected: >= 2)")
        logger.info(f"✓ Tags: {tag_count} (expected: >= 10)")

        # 뷰 테스트
        logger.info("\n7. Testing v_tags_with_plc view...")
        view_results = manager.execute_query(
            """
            SELECT tag_name, line_name, process_name, plc_name, group_name
            FROM v_tags_with_plc
            LIMIT 3
            """
        )
        logger.info(f"✓ View query returned {len(view_results)} rows:")
        for row in view_results:
            logger.info(f"  - {row['tag_name']} | {row['line_name']} | {row['process_name']} | {row['plc_name']} | {row['group_name']}")

        logger.info("=" * 60)
        logger.info("✓ Sample data created successfully!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("Starting sample data creation...")

    success = create_sample_data()

    if success:
        logger.info("\n✓ Sample data is ready to use!")
        logger.info("\nYou can now query the database:")
        logger.info("  sqlite3 data/scada.db")
        logger.info("  SELECT * FROM v_tags_with_plc;")
    else:
        logger.error("\n✗ Sample data creation failed!")
