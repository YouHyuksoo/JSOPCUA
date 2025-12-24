"use client";

type BottomStatusAreaProps = {
  isConnected: boolean;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  error?: string;
  websocketUrl: string;
};

export function BottomStatusArea({
  isConnected,
  reconnectAttempts,
  maxReconnectAttempts,
  error,
  websocketUrl,
}: BottomStatusAreaProps) {
  return (
    <div
      style={{
        height: "32px",
        padding: "0 16px",
        backgroundColor: "#000000",
        borderTop: "1px solid #374151",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        fontSize: "12px",
        color: "#9CA3AF",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: isConnected ? "#10B981" : "#EF4444",
            }}
          />
          <span>{isConnected ? "연결됨" : "연결 끊김"}</span>
        </div>
        {error ? (
          <span style={{ color: "#F87171" }}>⚠️ {error}</span>
        ) : (
          !isConnected &&
          reconnectAttempts > 0 && (
            <span style={{ color: "#FBBF24" }}>
              재연결 시도 중... ({reconnectAttempts}/{maxReconnectAttempts})
            </span>
          )
        )}
      </div>
      <span style={{ color: "#6B7280" }}>WebSocket: {websocketUrl}</span>
    </div>
  );
}
