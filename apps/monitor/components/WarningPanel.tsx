"use client";

export function WarningPanel() {
  return (
    <div
      style={{
        backgroundColor: "#000000",
        padding: "8px",
        border: "1px solid #374151",
      }}
    >
      <table
        style={{
          width: "100%",
          fontSize: "12px",
          borderCollapse: "collapse",
        }}
      >
        <tbody>
          {/* 경고 */}
          <tr style={{ borderBottom: "1px solid #374151" }}>
            <td
              style={{
                padding: "4px 8px",
                fontWeight: 500,
                color: "#FBBF24",
                width: "80px",
                border: "1px solid #4B5563",
              }}
            >
              경고
            </td>
            <td
              style={{
                padding: "4px 8px",
                color: "#6B7280",
                border: "1px solid #4B5563",
              }}
            >
              -
            </td>
          </tr>

          {/* 안전 */}
          <tr style={{ borderBottom: "1px solid #374151" }}>
            <td
              style={{
                padding: "4px 8px",
                fontWeight: 500,
                color: "#F87171",
                width: "80px",
                border: "1px solid #4B5563",
              }}
            >
              안전
            </td>
            <td
              style={{
                padding: "4px 8px",
                color: "#6B7280",
                border: "1px solid #4B5563",
              }}
            >
              -
            </td>
          </tr>

          {/* 정지 */}
          <tr>
            <td
              style={{
                padding: "4px 8px",
                fontWeight: 500,
                color: "#9CA3AF",
                width: "80px",
                border: "1px solid #4B5563",
              }}
            >
              정지
            </td>
            <td
              style={{
                padding: "4px 8px",
                color: "#6B7280",
                border: "1px solid #4B5563",
              }}
            >
              -
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
