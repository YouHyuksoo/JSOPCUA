"use client";

const DUMMY_EQUIPMENT_ALARMS = [
  { time: "10:13", equipment: "8-실런트 도포", message: "비상정지" },
  { time: "10:12", equipment: "7-U/L 쿨링", message: "비상정지" },
  { time: "10:11", equipment: "6-U/L 가열로", message: "비상정지" },
  { time: "10:10", equipment: "5-U/L 댐핑시 공급", message: "비상정지" },
  { time: "10:09", equipment: "4-Lower 브라켓 용접", message: "비상정지" },
];

export function EventLogPanel() {
  // 최신 5개만 표시
  const latestAlarms = DUMMY_EQUIPMENT_ALARMS.slice(0, 5);

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* 설비 정지 (설비알람) */}
      <div
        style={{
          backgroundColor: "#000000",
          display: "flex",
          flexDirection: "column",
          border: "1px solid #374151",
        }}
      >
        <div
          style={{
            padding: "8px",
            borderBottom: "1px solid #374151",
          }}
        >
          <h3
            style={{ fontSize: "14px", fontWeight: "bold", color: "#F87171" }}
          >
            설비 정지 (설비알람)
          </h3>
        </div>

        <div
          style={{
            padding: "8px",
            overflow: "hidden",
            maxHeight: "none",
          }}
        >
          <table
            style={{
              width: "100%",
              fontSize: "12px",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr style={{ borderBottom: "1px solid #4B5563" }}>
                <th
                  style={{
                    textAlign: "left",
                    padding: "4px 8px",
                    fontWeight: 500,
                    color: "#9CA3AF",
                    width: "64px",
                    border: "1px solid #4B5563",
                    borderRight: "1px solid #4B5563",
                  }}
                >
                  시간
                </th>
                <th
                  style={{
                    textAlign: "left",
                    padding: "4px 8px",
                    fontWeight: 500,
                    color: "#9CA3AF",
                    border: "1px solid #4B5563",
                  }}
                >
                  내용
                </th>
              </tr>
            </thead>
            <tbody>
              {latestAlarms.map((alarm, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid #4B5563" }}>
                  <td
                    style={{
                      padding: "4px 8px",
                      color: "#FCA5A5",
                      fontFamily: "monospace",
                      border: "1px solid #4B5563",
                      borderRight: "1px solid #4B5563",
                    }}
                  >
                    {alarm.time}
                  </td>
                  <td
                    style={{
                      padding: "4px 8px",
                      color: "#E5E7EB",
                      border: "1px solid #4B5563",
                    }}
                  >
                    {alarm.equipment} {alarm.message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
