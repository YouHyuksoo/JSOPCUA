"use client";

import { EventLogPanel } from "./EventLogPanel";

export function MiddleRightArea() {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#000000",
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        minHeight: 0,
        overflow: "hidden",
      }}
    >
      <div style={{ flex: 1, minHeight: "200px", overflow: "hidden" }}>
        <EventLogPanel />
      </div>
    </div>
  );
}
