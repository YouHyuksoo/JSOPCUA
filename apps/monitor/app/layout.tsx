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
    <html lang="ko">
      <body className="antialiased bg-gray-900 text-white">
        {children}
      </body>
    </html>
  );
}
