"use client";

import { Equipment } from "@/lib/types/equipment";
import { EquipmentStatusBox } from "./EquipmentStatusBox";

interface EquipmentLayoutProps {
  equipment: Equipment[];
  backgroundImageUrl?: string;
}

export function EquipmentLayout({
  equipment,
  backgroundImageUrl,
}: EquipmentLayoutProps) {
  const equipmentWithPosition = equipment.filter((eq) => eq.position);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        backgroundColor: "#000000",
        minHeight: "500px",
        overflow: "hidden",
      }}
    >
      {/* 배경 이미지 */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "#000000",
        }}
      >
        {backgroundImageUrl && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: `url('${backgroundImageUrl}')`,
              backgroundSize: "contain",
              backgroundPosition: "center center",
              backgroundRepeat: "no-repeat",
              opacity: 0.6,
            }}
          />
        )}
        {!backgroundImageUrl && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div style={{ textAlign: "center", color: "#4B5563" }}>
              <p style={{ fontSize: "14px" }}>배경 이미지 영역</p>
              <p style={{ fontSize: "12px", marginTop: "8px" }}>
                이미지를 불러오면 상태 박스가 표시됩니다
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 설비 상태 박스 오버레이 */}
      {equipmentWithPosition.length > 0 && (
        <div style={{ position: "relative", zIndex: 10 }}>
          {equipmentWithPosition.map((eq) => {
            const pos = eq.position!;
            return (
              <div
                key={eq.equipment_code}
                style={{
                  position: "absolute",
                  left: `${pos.position_x}px`,
                  top: `${pos.position_y}px`,
                  width: pos.width ? `${pos.width}px` : undefined,
                  height: pos.height ? `${pos.height}px` : undefined,
                  zIndex: pos.z_index || 1,
                }}
              >
                <EquipmentStatusBox
                  equipment={eq}
                  className={pos.width || pos.height ? "" : undefined}
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
