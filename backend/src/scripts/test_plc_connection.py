"""
PLC 연결 테스트 스크립트

SQLite DB에서 PLC 연결 정보를 읽어 PLC에 연결하고 단일 태그를 읽는 테스트 스크립트입니다.
"""

import sys
import os

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.sqlite_manager import SQLiteManager
from src.plc.mc3e_client import MC3EClient
from src.plc.exceptions import PLCException


def test_plc_connection(plc_code: str = None, tag_address: str = "D100"):
    """
    PLC 연결 및 태그 읽기 테스트

    Args:
        plc_code: 테스트할 PLC 코드 (None이면 첫 번째 활성 PLC 사용)
        tag_address: 읽을 태그 주소
    """
    db_path = os.path.join(os.path.dirname(__file__), '../../data/scada.db')

    print(f"\n{'='*60}")
    print("PLC Connection Test")
    print(f"{'='*60}\n")

    # SQLite DB에서 PLC 정보 읽기
    db = SQLiteManager(db_path)

    try:
        if plc_code:
            # 특정 PLC 조회
            query = """
                SELECT id, plc_code, plc_name, ip_address, port, protocol,
                       connection_timeout, is_active
                FROM plc_connections
                WHERE plc_code = ? AND is_active = 1
            """
            results = db.execute_query(query, (plc_code,))
        else:
            # 첫 번째 활성 PLC 조회
            query = """
                SELECT id, plc_code, plc_name, ip_address, port, protocol,
                       connection_timeout, is_active
                FROM plc_connections
                WHERE is_active = 1
                LIMIT 1
            """
            results = db.execute_query(query)

        if not results:
            print(f"❌ No active PLC found{f' with code {plc_code}' if plc_code else ''}")
            return False

        plc_info = results[0]

        print(f"📌 PLC Information:")
        print(f"   Code: {plc_info['plc_code']}")
        print(f"   Name: {plc_info['plc_name']}")
        print(f"   Address: {plc_info['ip_address']}:{plc_info['port']}")
        print(f"   Protocol: {plc_info['protocol']}")
        print(f"   Timeout: {plc_info['connection_timeout']}s\n")

        # PLC 연결 테스트
        print(f"🔌 Connecting to PLC...")
        client = MC3EClient(
            ip_address=plc_info['ip_address'],
            port=plc_info['port'],
            plc_code=plc_info['plc_code'],
            timeout=plc_info['connection_timeout']
        )

        try:
            # 연결
            client.connect()
            print(f"✅ Connection successful!\n")

            # 태그 읽기
            print(f"📖 Reading tag: {tag_address}")
            value = client.read_single(tag_address)
            print(f"✅ Tag value: {tag_address} = {value}\n")

            print(f"{'='*60}")
            print("✅ Test completed successfully!")
            print(f"{'='*60}\n")

            return True

        except PLCException as e:
            print(f"\n❌ PLC Error: {e}\n")
            print(f"{'='*60}")
            print("❌ Test failed")
            print(f"{'='*60}\n")
            return False

        finally:
            client.disconnect()

    except Exception as e:
        print(f"\n❌ Database Error: {e}\n")
        print(f"{'='*60}")
        print("❌ Test failed")
        print(f"{'='*60}\n")
        return False

    finally:
        db.close()


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Test PLC connection and tag reading')
    parser.add_argument('--plc', type=str, help='PLC code to test (default: first active PLC)')
    parser.add_argument('--tag', type=str, default='D100', help='Tag address to read (default: D100)')

    args = parser.parse_args()

    success = test_plc_connection(plc_code=args.plc, tag_address=args.tag)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
