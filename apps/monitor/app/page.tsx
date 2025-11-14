"use client";

import { Equipment } from "@/lib/types/equipment";
import { AlarmStatistics } from "@/lib/types/alarm";
import { getEquipmentColor } from "@/lib/utils";
import { getEquipmentPositions } from "@/lib/api/positions";
import { getAlarmStatistics } from "@/lib/api/alarms";
import { useEffect, useState } from "react";
import { TopArea } from "@/components/TopArea";
import { MiddleLeftArea } from "@/components/MiddleLeftArea";
import { MiddleRightArea } from "@/components/MiddleRightArea";
import { BottomStatusArea } from "@/components/BottomStatusArea";
import { LegendPanel } from "@/components/LegendPanel";
import { WarningPanel } from "@/components/WarningPanel";

const WEBSOCKET_URL =
  process.env.NEXT_PUBLIC_WEBSOCKET_URL || "ws://localhost:8000/ws/monitor";
const BACKGROUND_IMAGE_URL =
  process.env.NEXT_PUBLIC_EQUIPMENT_LAYOUT_IMAGE || "/equipment-layout.png";
const ALARM_REFRESH_INTERVAL = 10000;

// 더미 설비 데이터 (17개)
const DUMMY_EQUIPMENT: Equipment[] = [
  {
    equipment_code: "EQ001",
    equipment_name: "1-Upper 로딩",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ002",
    equipment_name: "2-Lower 로딩",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ003",
    equipment_name: "3-Upper 브라켓 용접",
    status: "idle",
    color: "yellow",
    tags: { status_tag: 2, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ004",
    equipment_name: "4-Lower 브라켓 용접",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ005",
    equipment_name: "5-U/L 댐핑시 공급",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ006",
    equipment_name: "6-U/L 가열로",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ007",
    equipment_name: "7-U/L 쿨링",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ008",
    equipment_name: "8-실런트 도포",
    status: "error",
    color: "red",
    tags: { status_tag: 0, error_tag: 1, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ009",
    equipment_name: "9-센터 로딩",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ010",
    equipment_name: "10-센터 댐핑시 공급",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ011",
    equipment_name: "11-센터 가열로",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ012",
    equipment_name: "12-센터 쿨링",
    status: "idle",
    color: "yellow",
    tags: { status_tag: 2, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ013",
    equipment_name: "13-U 밴딩",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ014",
    equipment_name: "14-Tub 브라켓 용접",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ015",
    equipment_name: "15-Tub 가조립",
    status: "stopped",
    color: "purple",
    tags: { status_tag: 0, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ016",
    equipment_name: "16-Shuttle #1",
    status: "running",
    color: "green",
    tags: { status_tag: 1, error_tag: 0, connection: true },
    last_updated: new Date(),
  },
  {
    equipment_code: "EQ017",
    equipment_name: "17-시밍 #1",
    status: "disconnected",
    color: "gray",
    tags: { status_tag: 0, error_tag: 0, connection: false },
    last_updated: new Date(),
  },
];

export default function MonitorPage() {
  // WebSocket 통신은 나중에 활성화
  // const { isConnected, equipment: rawEquipment, reconnectAttempts, error } = useWebSocket({...});

  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [positionsMap, setPositionsMap] = useState<Record<string, any>>({});
  const [alarmStatistics, setAlarmStatistics] = useState<AlarmStatistics[]>([]);

  // 더미 데이터로 초기화
  useEffect(() => {
    const processedEquipment = DUMMY_EQUIPMENT.map((eq) => ({
      ...eq,
      color: getEquipmentColor(eq),
    }));
    setEquipment(processedEquipment);
  }, []);

  useEffect(() => {
    const loadPositions = async () => {
      try {
        const positionsData = await getEquipmentPositions("default");
        setPositionsMap(positionsData.positions);
      } catch (error) {
        console.error("Failed to load equipment positions:", error);
        // 에러가 나도 계속 진행
      }
    };
    loadPositions();
  }, []);

  useEffect(() => {
    const fetchAlarmStats = async () => {
      try {
        const data = await getAlarmStatistics();
        setAlarmStatistics(data.equipment);
      } catch (error) {
        console.error("Failed to load alarm statistics:", error);
        // 에러가 나도 더미 데이터 사용
      }
    };
    fetchAlarmStats();
    const interval = setInterval(fetchAlarmStats, ALARM_REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  // 위치 정보 매핑
  useEffect(() => {
    if (Object.keys(positionsMap).length > 0) {
      const processedEquipment = equipment.map((eq) => {
        // process_code로 위치 정보 찾기 (equipment_code가 아닌 process_code 사용)
        const position = Object.values(positionsMap).find(
          (pos: any) =>
            pos.process_code === eq.equipment_code ||
            pos.machine_code === eq.equipment_code
        ) as any;

        return {
          ...eq,
          position: position
            ? {
                process_code: position.process_code,
                position_x: position.position_x,
                position_y: position.position_y,
                width: position.width,
                height: position.height,
                z_index: position.z_index,
                tag_id: position.tag_id || null,
                tag_address: position.tag_address || null,
                plc_code: position.plc_code || null,
                machine_code: position.machine_code || null,
              }
            : undefined,
        };
      });
      setEquipment(processedEquipment);
    }
  }, [positionsMap]);

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        backgroundColor: "#000000",
        color: "#ffffff",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* 상단영역 */}
      <div style={{ flexShrink: 0, backgroundColor: "#000000" }}>
        <TopArea equipment={equipment} alarmStatistics={alarmStatistics} />
      </div>

      {/* Legend 영역 - 중단 위쪽 */}
      <div style={{ flexShrink: 0, backgroundColor: "#000000" }}>
        <LegendPanel />
      </div>

      {/* 중단영역 */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "row",
          gap: "16px",
          padding: "16px",
          backgroundColor: "#000000",
          minHeight: 0,
          overflow: "hidden",
        }}
      >
        {/* 중단좌측영역 - 설비상태이미지 */}
        <div
          style={{
            flex: 1,
            backgroundColor: "#000000",
            border: "1px solid #374151",
            minHeight: 0,
            overflow: "hidden",
          }}
        >
          <MiddleLeftArea
            equipment={equipment}
            backgroundImageUrl={BACKGROUND_IMAGE_URL}
          />
        </div>

        {/* 중단우측영역 */}
        <div
          style={{
            width: "320px",
            backgroundColor: "#000000",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            minHeight: 0,
            overflow: "hidden",
          }}
        >
          <MiddleRightArea />
        </div>
      </div>

      {/* 하단상태영역 */}
      <div
        style={{
          flexShrink: 0,
          backgroundColor: "#000000",
          borderTop: "1px solid #374151",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <WarningPanel />
        <BottomStatusArea
          isConnected={false}
          reconnectAttempts={0}
          maxReconnectAttempts={5}
          error={undefined}
          websocketUrl={WEBSOCKET_URL}
        />
      </div>
    </div>
  );
}
