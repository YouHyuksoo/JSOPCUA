"""
Alarm Routes for Monitor Web UI

Feature 7: Monitor Web UI - Alarm API endpoints
Provides REST API endpoints for querying alarm data from Oracle DB
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import oracledb

from .models import Alarm, AlarmStatistics, AlarmStatisticsResponse, RecentAlarmsResponse
from .dependencies import get_db


router = APIRouter(prefix="/api/alarms", tags=["alarms"])

# Oracle DB connection settings (will be configured via environment variables)
ORACLE_USER = "your_username"  # TODO: Configure via environment
ORACLE_PASSWORD = "your_password"  # TODO: Configure via environment
ORACLE_DSN = "localhost/orclpdb"  # TODO: Configure via environment


def get_oracle_connection():
    """Get Oracle DB connection using python-oracledb"""
    try:
        connection = oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=ORACLE_DSN
        )
        return connection
    except oracledb.Error as e:
        raise HTTPException(status_code=503, detail=f"Oracle DB connection failed: {str(e)}")


@router.get("/statistics", response_model=AlarmStatisticsResponse)
async def get_alarm_statistics():
    """
    Get alarm statistics for all 17 equipment (알람 합계 및 일반 건수)

    Returns aggregated alarm counts (alarm and general) for each equipment
    from the last 24 hours.
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        # Query to aggregate alarm counts by equipment
        # Assumes ALARMS table exists with columns: ALARM_ID, EQUIPMENT_CODE, ALARM_TYPE, OCCURRED_AT
        # Joins with SQLite processes table to get equipment_name
        query = """
            SELECT
                EQUIPMENT_CODE,
                SUM(CASE WHEN ALARM_TYPE = '알람' THEN 1 ELSE 0 END) as alarm_count,
                SUM(CASE WHEN ALARM_TYPE = '일반' THEN 1 ELSE 0 END) as general_count
            FROM ALARMS
            WHERE OCCURRED_AT >= SYSTIMESTAMP - INTERVAL '24' HOUR
            GROUP BY EQUIPMENT_CODE
            ORDER BY EQUIPMENT_CODE
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Get equipment names from SQLite (assuming processes table has process_code and process_name)
        # For now, we'll use equipment_code as equipment_name if SQLite query fails
        equipment_list: List[AlarmStatistics] = []

        for row in rows:
            equipment_code = row[0]
            alarm_count = row[1]
            general_count = row[2]

            # TODO: Query SQLite for equipment_name by process_code (equipment_code)
            # For now, use equipment_code as placeholder
            equipment_name = equipment_code

            equipment_list.append(AlarmStatistics(
                equipment_code=equipment_code,
                equipment_name=equipment_name,
                alarm_count=alarm_count,
                general_count=general_count
            ))

        cursor.close()
        conn.close()

        return AlarmStatisticsResponse(
            equipment=equipment_list,
            last_updated=datetime.now()
        )

    except oracledb.Error as e:
        raise HTTPException(status_code=503, detail=f"Oracle DB query failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/recent", response_model=RecentAlarmsResponse)
async def get_recent_alarms(limit: int = Query(5, ge=1, le=100)):
    """
    Get recent alarms (최근 알람 목록)

    Returns the most recent alarms ordered by occurred_at descending.
    Default limit is 5.
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        # Query to get recent alarms with equipment name
        query = """
            SELECT
                ALARM_ID,
                EQUIPMENT_CODE,
                ALARM_TYPE,
                ALARM_MESSAGE,
                OCCURRED_AT,
                CREATED_AT
            FROM ALARMS
            ORDER BY OCCURRED_AT DESC
            FETCH FIRST :limit ROWS ONLY
        """

        cursor.execute(query, limit=limit)
        rows = cursor.fetchall()

        alarms: List[Alarm] = []

        for row in rows:
            alarm_id = row[0]
            equipment_code = row[1]
            alarm_type = row[2]
            alarm_message = row[3]
            occurred_at = row[4]
            created_at = row[5]

            # TODO: Query SQLite for equipment_name by process_code (equipment_code)
            equipment_name = equipment_code

            alarms.append(Alarm(
                alarm_id=alarm_id,
                equipment_code=equipment_code,
                equipment_name=equipment_name,
                alarm_type=alarm_type,
                alarm_message=alarm_message,
                occurred_at=occurred_at,
                created_at=created_at
            ))

        cursor.close()
        conn.close()

        return RecentAlarmsResponse(alarms=alarms)

    except oracledb.Error as e:
        raise HTTPException(status_code=503, detail=f"Oracle DB query failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def check_alarm_health():
    """
    Health check endpoint for alarm API

    Verifies Oracle DB connection and returns status.
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "status": "healthy",
            "oracle_connection": "ok",
            "timestamp": datetime.now()
        }

    except oracledb.Error as e:
        raise HTTPException(status_code=503, detail=f"Oracle DB connection failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
