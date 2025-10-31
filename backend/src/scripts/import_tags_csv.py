"""
CSV 파일에서 태그 일괄 등록
User Story 4: CSV 일괄 태그 등록 기능

실행: python src/scripts/import_tags_csv.py <csv_file_path>

CSV 형식:
PLC_CODE,TAG_ADDRESS,TAG_NAME,UNIT,SCALE,MACHINE_CODE
PLC01,D100,온도센서1,°C,1.0,KRCWO12ELOA101
PLC01,D101,압력센서1,bar,0.1,KRCWO12ELOA101
"""
import sys
import csv
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.sqlite_manager import SQLiteManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TagCSVImporter:
    """CSV 파일에서 태그 일괄 가져오기"""

    def __init__(self, db_path: str):
        """
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.manager = SQLiteManager(db_path)
        self.batch_size = 500  # 배치 크기 (500개씩 처리)

    def validate_csv_headers(self, headers: List[str]) -> bool:
        """
        CSV 헤더 검증

        Args:
            headers: CSV 헤더 목록

        Returns:
            bool: 유효성 여부
        """
        required_headers = [
            'PLC_CODE',
            'TAG_ADDRESS',
            'TAG_NAME',
            'UNIT',
            'SCALE',
            'MACHINE_CODE'
        ]

        for header in required_headers:
            if header not in headers:
                logger.error(f"Missing required header: {header}")
                return False

        return True

    def get_plc_id_by_code(self, plc_code: str) -> int:
        """
        PLC 코드로 PLC ID 조회

        Args:
            plc_code: PLC 코드

        Returns:
            int: PLC ID (없으면 0)
        """
        results = self.manager.execute_query(
            "SELECT id FROM plc_connections WHERE plc_code = ?",
            (plc_code,)
        )
        if results:
            return results[0]['id']
        else:
            logger.warning(f"PLC not found: {plc_code}")
            return 0

    def import_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """
        CSV 파일에서 태그 가져오기

        Args:
            csv_file_path: CSV 파일 경로

        Returns:
            Dict: 가져오기 결과 통계
                {
                    'total': 전체 행 수,
                    'success': 성공 수,
                    'failed': 실패 수,
                    'skipped': 건너뛴 수,
                    'errors': 에러 목록
                }
        """
        csv_path = Path(csv_file_path)

        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_file_path}")
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'skipped': 0,
                'errors': [f"File not found: {csv_file_path}"]
            }

        logger.info(f"Reading CSV file: {csv_file_path}")

        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        # PLC 코드 → PLC ID 캐시
        plc_cache = {}

        batch = []
        batch_count = 0

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # 헤더 검증
                if not self.validate_csv_headers(reader.fieldnames):
                    stats['errors'].append("Invalid CSV headers")
                    return stats

                logger.info(f"CSV headers validated: {reader.fieldnames}")

                for row_num, row in enumerate(reader, start=2):  # 2부터 시작 (헤더가 1번째 줄)
                    stats['total'] += 1

                    try:
                        # 필수 필드 검증
                        plc_code = row.get('PLC_CODE', '').strip()
                        tag_address = row.get('TAG_ADDRESS', '').strip()
                        tag_name = row.get('TAG_NAME', '').strip()

                        if not plc_code or not tag_address or not tag_name:
                            logger.warning(f"Row {row_num}: Missing required fields, skipping")
                            stats['skipped'] += 1
                            continue

                        # PLC ID 조회 (캐시 사용)
                        if plc_code not in plc_cache:
                            plc_id = self.get_plc_id_by_code(plc_code)
                            if plc_id == 0:
                                logger.error(f"Row {row_num}: PLC '{plc_code}' not found, skipping")
                                stats['skipped'] += 1
                                stats['errors'].append(f"Row {row_num}: PLC '{plc_code}' not found")
                                continue
                            plc_cache[plc_code] = plc_id
                        else:
                            plc_id = plc_cache[plc_code]

                        # 태그 데이터 준비
                        unit = row.get('UNIT', '').strip() or None
                        scale = float(row.get('SCALE', 1.0))
                        machine_code = row.get('MACHINE_CODE', '').strip() or None

                        # 배치에 추가
                        batch.append((
                            plc_id,
                            tag_address,
                            tag_name,
                            'INT',  # 기본 타입
                            unit,
                            scale,
                            0.0,  # offset
                            machine_code,
                            True,  # is_active
                        ))

                        # 배치 크기에 도달하면 INSERT 실행
                        if len(batch) >= self.batch_size:
                            self._insert_batch(batch)
                            stats['success'] += len(batch)
                            batch_count += 1
                            logger.info(f"Batch {batch_count} inserted: {len(batch)} tags")
                            batch = []

                    except Exception as e:
                        logger.error(f"Row {row_num}: Error processing row - {e}")
                        stats['failed'] += 1
                        stats['errors'].append(f"Row {row_num}: {str(e)}")

                # 남은 배치 처리
                if batch:
                    self._insert_batch(batch)
                    stats['success'] += len(batch)
                    batch_count += 1
                    logger.info(f"Final batch {batch_count} inserted: {len(batch)} tags")

        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            stats['errors'].append(f"CSV read error: {str(e)}")

        return stats

    def _insert_batch(self, batch: List[tuple]) -> None:
        """
        배치 INSERT 실행

        Args:
            batch: 태그 데이터 배치
        """
        insert_query = """
            INSERT INTO tags (
                plc_id,
                tag_address,
                tag_name,
                tag_type,
                unit,
                scale,
                offset,
                machine_code,
                is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            self.manager.execute_many(insert_query, batch)
        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            raise


def print_import_summary(stats: Dict[str, Any]) -> None:
    """
    가져오기 결과 요약 출력

    Args:
        stats: 가져오기 통계
    """
    logger.info("\n" + "=" * 60)
    logger.info("CSV Import Summary")
    logger.info("=" * 60)
    logger.info(f"Total rows processed: {stats['total']}")
    logger.info(f"✓ Successfully imported: {stats['success']}")
    logger.info(f"⊘ Skipped: {stats['skipped']}")
    logger.info(f"✗ Failed: {stats['failed']}")

    if stats['errors']:
        logger.info("\nErrors:")
        for error in stats['errors'][:10]:  # 최대 10개만 표시
            logger.info(f"  - {error}")
        if len(stats['errors']) > 10:
            logger.info(f"  ... and {len(stats['errors']) - 10} more errors")

    logger.info("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python import_tags_csv.py <csv_file_path>")
        sys.exit(1)

    csv_file = sys.argv[1]
    db_path = project_root / "config" / "scada.db"

    logger.info("Starting CSV import...")
    logger.info(f"CSV file: {csv_file}")
    logger.info(f"Database: {db_path}")

    # CSV 가져오기 실행
    importer = TagCSVImporter(str(db_path))
    start_time = datetime.now()
    stats = importer.import_from_csv(csv_file)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # 결과 출력
    print_import_summary(stats)
    logger.info(f"Import duration: {duration:.2f} seconds")

    if stats['total'] > 0:
        logger.info(f"Average: {stats['total'] / duration:.0f} tags/second")

    if stats['success'] > 0:
        logger.info("\n✓ CSV import completed successfully!")
    elif stats['total'] == 0:
        logger.warning("\n⊘ No rows processed")
    else:
        logger.error("\n✗ CSV import completed with errors")
