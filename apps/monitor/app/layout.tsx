import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "설비 모니터링 - SCADA Monitor",
  description: "17개 설비의 실시간 상태 모니터링 및 알람 조회",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" style={{ backgroundColor: "#000000", height: "100%" }}>
      <body
        style={{
          backgroundColor: "#000000",
          color: "#ffffff",
          height: "100%",
          margin: 0,
          padding: 0,
        }}
      >
        {children}
      </body>
    </html>
  );
}
