"""
Monitor Routes for Monitor Web UI

Oracle DB에서 설비 목록을 조회하는 API 엔드포인트
설비 박스 위치 정보 관리 API
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field
import oracledb

from src.oracle_writer.config import load_config_from_env
from src.config.logging_config import get_logger
from src.database.sqlite_manager import SQLiteManager
from .dependencies import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/api/monitor", tags=["monitor"])


class EquipmentListItem(BaseModel):
    """설비 목록 항목"""
    machine_code: str
    machine_name: str
    machine_type: Optional[str] = None
    line_code: Optional[str] = None
    plc_code: Optional[str] = None
    use_yn: Optional[str] = None


class EquipmentListResponse(BaseModel):
    """설비 목록 응답"""
    equipment: List[EquipmentListItem]
    total_count: int
    page: int
    page_size: int


class EquipmentPosition(BaseModel):
    """설비 박스 위치 정보"""
    process_code: str
    position_x: float = Field(ge=0, description="X 좌표 (픽셀)")
    position_y: float = Field(ge=0, description="Y 좌표 (픽셀)")
    width: Optional[float] = Field(None, ge=0, description="박스 너비 (픽셀)")
    height: Optional[float] = Field(None, ge=0, description="박스 높이 (픽셀)")
    z_index: Optional[int] = Field(1, description="z-index")
    # PLC 태그 매핑 필드
    tag_id: Optional[int] = Field(None, description="태그 ID (tags 테이블 참조)")
    tag_address: Optional[str] = Field(None, description="태그 주소 (예: 'D100', 'W150')")
    plc_code: Optional[str] = Field(None, description="PLC 코드")
    machine_code: Optional[str] = Field(None, description="설비 코드 (machine_code)")


class EquipmentPositionUpdate(BaseModel):
    """설비 위치 업데이트 요청"""
    layout_name: str = Field(default="default", description="레이아웃 이름")
    positions: List[EquipmentPosition] = Field(description="설비 위치 목록")


class EquipmentPositionsResponse(BaseModel):
    """설비 위치 정보 응답"""
    layout_name: str
    positions: Dict[str, EquipmentPosition] = Field(description="process_code를 키로 하는 위치 정보 딕셔너리")


def get_oracle_connection():
    """Get Oracle DB connection using python-oracledb"""
    try:
        config = load_config_from_env()
        connection = oracledb.connect(
            user=config.username,
            password=config.password,
            dsn=config.get_dsn()
        )
        return connection
    except Exception as e:
        logger.error(f"Oracle DB connection failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Oracle DB connection failed: {str(e)}")


@router.get("/equipment", response_model=EquipmentListResponse)
async def get_equipment_list(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(50, ge=1, le=200, description="페이지당 항목 수"),
    use_yn: Optional[str] = Query(None, description="사용 여부 필터 (Y/N)")
):
    """
    Oracle DB의 ICOM_MACHINE_MASTER 테이블에서 설비 목록 조회
    
    Returns:
        EquipmentListResponse: 설비 목록 및 페이지네이션 정보
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        
        # WHERE 조건 구성
        where_clause = "WHERE 1=1"
        params = {}
        
        if use_yn:
            where_clause += " AND USE_YN = :use_yn"
            params['use_yn'] = use_yn
        
        # 전체 개수 조회
        count_query = f"""
            SELECT COUNT(*) 
            FROM ICOM_MACHINE_MASTER 
            {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # 페이지네이션 계산
        offset = (page - 1) * page_size
        
        # 설비 목록 조회
        query = f"""
            SELECT 
                MACHINE_CODE,
                MACHINE_NAME,
                MACHINE_TYPE,
                LINE_CODE,
                PLC_CODE,
                USE_YN
            FROM ICOM_MACHINE_MASTER
            {where_clause}
            ORDER BY MACHINE_CODE
            OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY
        """
        
        params['offset'] = offset
        params['page_size'] = page_size
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        equipment_list: List[EquipmentListItem] = []
        
        for row in rows:
            equipment_list.append(EquipmentListItem(
                machine_code=row[0] or "",
                machine_name=row[1] or "",
                machine_type=row[2],
                line_code=row[3],
                plc_code=row[4],
                use_yn=row[5]
            ))
        
        cursor.close()
        conn.close()
        
        return EquipmentListResponse(
            equipment=equipment_list,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except oracledb.Error as e:
        logger.error(f"Oracle DB query failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Oracle DB query failed: {str(e)}")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/tags")
async def get_tags_for_monitor(
    machine_code: Optional[str] = Query(None, description="설비 코드 필터"),
    plc_code: Optional[str] = Query(None, description="PLC 코드 필터"),
    db: SQLiteManager = Depends(get_db)
):
    """
    모니터링 페이지에서 사용할 태그 목록 조회
    
    태그 ID, 주소, PLC 코드, 설비 코드를 포함한 간단한 태그 목록을 반환합니다.
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # WHERE 조건 구성
            conditions = ["t.is_active = 1"]
            params = []
            
            if machine_code:
                conditions.append("t.machine_code = ?")
                params.append(machine_code)
            
            if plc_code:
                conditions.append("p.plc_code = ?")
                params.append(plc_code)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            cursor.execute(f"""
                SELECT 
                    t.id as tag_id,
                    t.tag_address,
                    t.tag_name,
                    t.machine_code,
                    p.plc_code,
                    t.tag_type,
                    t.unit,
                    t.description
                FROM tags t
                LEFT JOIN plc_connections p ON t.plc_id = p.id
                {where_clause}
                ORDER BY t.machine_code, t.tag_address
            """, params)
            rows = cursor.fetchall()
            
            tags = []
            for row in rows:
                tags.append({
                    "tag_id": row[0],
                    "tag_address": row[1],
                    "tag_name": row[2],
                    "machine_code": row[3],
                    "plc_code": row[4],
                    "tag_type": row[5],
                    "unit": row[6],
                    "description": row[7] if len(row) > 7 else None
                })
            
            return {"tags": tags}
    except Exception as e:
        logger.error(f"Failed to get tags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/equipment-positions", response_model=EquipmentPositionsResponse)
async def get_equipment_positions(
    layout_name: str = Query("default", description="레이아웃 이름"),
    db: SQLiteManager = Depends(get_db)
):
    """
    설비 박스 위치 정보 조회
    
    Returns:
        EquipmentPositionsResponse: 설비별 위치 정보
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    process_code,
                    position_x,
                    position_y,
                    width,
                    height,
                    z_index,
                    tag_id,
                    tag_address,
                    plc_code,
                    machine_code
                FROM equipment_positions
                WHERE layout_name = ?
                ORDER BY z_index, process_code
            """, (layout_name,))
            rows = cursor.fetchall()
            
            positions: Dict[str, EquipmentPosition] = {}
            for row in rows:
                process_code = row[0]
                positions[process_code] = EquipmentPosition(
                    process_code=process_code,
                    position_x=row[1],
                    position_y=row[2],
                    width=row[3],
                    height=row[4],
                    z_index=row[5] if row[5] is not None else 1,
                    tag_id=row[6] if len(row) > 6 and row[6] is not None else None,
                    tag_address=row[7] if len(row) > 7 and row[7] is not None else None,
                    plc_code=row[8] if len(row) > 8 and row[8] is not None else None,
                    machine_code=row[9] if len(row) > 9 and row[9] is not None else None
                )
            
            return EquipmentPositionsResponse(
                layout_name=layout_name,
                positions=positions
            )
    except Exception as e:
        logger.error(f"Failed to get equipment positions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/equipment-positions", status_code=200)
async def save_equipment_positions(
    update: EquipmentPositionUpdate,
    db: SQLiteManager = Depends(get_db)
):
    """
    설비 박스 위치 정보 저장/업데이트
    
    위치 정보가 없으면 생성하고, 있으면 업데이트합니다.
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 각 위치 정보를 저장/업데이트
            for pos in update.positions:
                # 먼저 존재 여부 확인
                cursor.execute("""
                    SELECT id FROM equipment_positions
                    WHERE process_code = ? AND layout_name = ?
                """, (pos.process_code, update.layout_name))
                existing = cursor.fetchone()
                
                if existing:
                    # 업데이트
                    cursor.execute("""
                        UPDATE equipment_positions
                        SET position_x = ?,
                            position_y = ?,
                            width = ?,
                            height = ?,
                            z_index = ?,
                            tag_id = ?,
                            tag_address = ?,
                            plc_code = ?,
                            machine_code = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE process_code = ? AND layout_name = ?
                    """, (
                        pos.position_x,
                        pos.position_y,
                        pos.width,
                        pos.height,
                        pos.z_index or 1,
                        pos.tag_id,
                        pos.tag_address,
                        pos.plc_code,
                        pos.machine_code,
                        pos.process_code,
                        update.layout_name
                    ))
                else:
                    # 생성
                    cursor.execute("""
                        INSERT INTO equipment_positions
                        (process_code, layout_name, position_x, position_y, width, height, z_index, tag_id, tag_address, plc_code, machine_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pos.process_code,
                        update.layout_name,
                        pos.position_x,
                        pos.position_y,
                        pos.width,
                        pos.height,
                        pos.z_index or 1,
                        pos.tag_id,
                        pos.tag_address,
                        pos.plc_code,
                        pos.machine_code
                    ))
            
            conn.commit()
            
            return {
                "message": f"{len(update.positions)}개 설비 위치 정보가 저장되었습니다.",
                "layout_name": update.layout_name,
                "count": len(update.positions)
            }
    except Exception as e:
        logger.error(f"Failed to save equipment positions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

