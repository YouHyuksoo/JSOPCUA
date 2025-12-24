"use client";

import { EquipmentStatusTable } from "./EquipmentStatusTable";
import { Equipment } from "@/lib/types/equipment";
import { AlarmStatistics } from "@/lib/types/alarm";

type TopAreaProps = {
  equipment: Equipment[];
  alarmStatistics: AlarmStatistics[];
};

export function TopArea({ equipment, alarmStatistics }: TopAreaProps) {
  return (
    <div
      style={{ width: "100%", backgroundColor: "#000000", padding: "8px 16px" }}
    >
      <EquipmentStatusTable
        equipment={equipment}
        alarmStatistics={alarmStatistics}
      />
    </div>
  );
}
