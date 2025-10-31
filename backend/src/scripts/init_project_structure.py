"""
프로젝트 디렉토리 구조 자동 생성 스크립트
User Story 1: 프로젝트 디렉토리 구조 생성

실행: python src/scripts/init_project_structure.py
"""
import os
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_directory_structure():
    """프로젝트 디렉토리 구조 생성"""

    # 프로젝트 루트 경로 (backend의 상위 디렉토리)
    project_root = Path(__file__).parent.parent.parent.parent

    # 생성할 디렉토리 목록
    directories = [
        # Backend directories
        "backend/src/database",
        "backend/src/scripts",
        "backend/config",
        "backend/logs",
        "backend/tests",

        # Frontend Admin directories
        "frontend-admin/app",
        "frontend-admin/components/ui",
        "frontend-admin/lib",
        "frontend-admin/public",

        # Frontend Monitor directories
        "frontend-monitor/app",
        "frontend-monitor/components/ui",
        "frontend-monitor/lib",
        "frontend-monitor/public",
    ]

    created_count = 0
    existing_count = 0

    for directory in directories:
        dir_path = project_root / directory
        if dir_path.exists():
            logger.info(f"✓ Directory already exists: {directory}")
            existing_count += 1
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Created directory: {directory}")
            created_count += 1

    # __init__.py 파일 생성
    init_files = [
        "backend/src/__init__.py",
        "backend/src/database/__init__.py",
        "backend/src/scripts/__init__.py",
    ]

    init_created = 0
    init_existing = 0

    for init_file in init_files:
        file_path = project_root / init_file
        if file_path.exists():
            logger.info(f"✓ File already exists: {init_file}")
            init_existing += 1
        else:
            file_path.write_text(f'"""{Path(init_file).parent.name} package"""\n')
            logger.info(f"✓ Created file: {init_file}")
            init_created += 1

    # 요약 출력
    logger.info("\n" + "=" * 60)
    logger.info("Project Structure Initialization Complete")
    logger.info("=" * 60)
    logger.info(f"Directories - Created: {created_count}, Existing: {existing_count}")
    logger.info(f"Init files - Created: {init_created}, Existing: {init_existing}")
    logger.info("=" * 60)

    return created_count + existing_count == len(directories)


def verify_directory_structure():
    """디렉토리 구조 검증"""

    project_root = Path(__file__).parent.parent.parent.parent

    required_backend_dirs = [
        "backend/src/database",
        "backend/src/scripts",
        "backend/config",
        "backend/logs",
        "backend/tests",
    ]

    required_admin_dirs = [
        "frontend-admin/app",
        "frontend-admin/components/ui",
        "frontend-admin/lib",
        "frontend-admin/public",
    ]

    required_monitor_dirs = [
        "frontend-monitor/app",
        "frontend-monitor/components/ui",
        "frontend-monitor/lib",
        "frontend-monitor/public",
    ]

    all_required = required_backend_dirs + required_admin_dirs + required_monitor_dirs

    logger.info("\n" + "=" * 60)
    logger.info("Verifying Directory Structure")
    logger.info("=" * 60)

    all_exist = True

    for directory in all_required:
        dir_path = project_root / directory
        if dir_path.exists() and dir_path.is_dir():
            logger.info(f"✓ {directory}")
        else:
            logger.error(f"✗ {directory} - NOT FOUND")
            all_exist = False

    logger.info("=" * 60)
    if all_exist:
        logger.info("✓ All required directories exist")
    else:
        logger.error("✗ Some directories are missing")
    logger.info("=" * 60)

    return all_exist


if __name__ == "__main__":
    logger.info("Starting project structure initialization...")

    # 디렉토리 구조 생성
    success = create_directory_structure()

    # 검증
    if success:
        verified = verify_directory_structure()
        if verified:
            logger.info("\n✓ Project structure initialization completed successfully!")
        else:
            logger.error("\n✗ Project structure verification failed!")
    else:
        logger.error("\n✗ Project structure creation failed!")
