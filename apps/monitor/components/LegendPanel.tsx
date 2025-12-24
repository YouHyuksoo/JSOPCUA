"use client";

export function LegendPanel() {
  return (
    <div
      style={{
        backgroundColor: "#000000",
        padding: "8px 16px",
        borderBottom: "1px solid #374151",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "24px",
          fontSize: "12px",
        }}
      >
        {/* 설비 상태 */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "20px",
                height: "20px",
                borderRadius: "4px",
                backgroundColor: "#16A34A",
              }}
            ></div>
            <span style={{ color: "#16A34A" }}>가동</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "20px",
                height: "20px",
                borderRadius: "4px",
                backgroundColor: "#FBBF24",
              }}
            ></div>
            <span style={{ color: "#FBBF24" }}>비가동</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "20px",
                height: "20px",
                borderRadius: "4px",
                backgroundColor: "#DC2626",
              }}
            ></div>
            <span style={{ color: "#DC2626" }}>정지</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "20px",
                height: "20px",
                borderRadius: "4px",
                backgroundColor: "#9333EA",
              }}
            ></div>
            <span style={{ color: "#9333EA" }}>설비이상</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "20px",
                height: "20px",
                borderRadius: "4px",
                backgroundColor: "#9CA3AF",
              }}
            ></div>
            <span style={{ color: "#9CA3AF" }}>접속이상</span>
          </div>
        </div>
      </div>
    </div>
  );
}
