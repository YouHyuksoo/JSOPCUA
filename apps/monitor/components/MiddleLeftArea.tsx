"use client";

import { EquipmentLayout } from "./EquipmentLayout";
import { Equipment } from "@/lib/types/equipment";

type MiddleLeftAreaProps = {
  equipment: Equipment[];
  backgroundImageUrl?: string;
};

export function MiddleLeftArea({
  equipment,
  backgroundImageUrl,
}: MiddleLeftAreaProps) {
  return (
    <div style={{ width: "100%", height: "100%", backgroundColor: "#000000" }}>
      <EquipmentLayout
        equipment={equipment}
        backgroundImageUrl={backgroundImageUrl}
      />
    </div>
  );
}
