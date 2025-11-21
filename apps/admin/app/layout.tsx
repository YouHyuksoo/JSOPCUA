import './globals.css'
import { Toaster } from '@/components/ui/sonner'
import { Toaster as ShadcnToaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'
import { Sidebar } from '@/components/sidebar'
import { SidebarProvider } from '@/components/sidebar-context'
import { MainContent } from '@/components/main-content'


/**
 * @file apps/admin/app/layout.tsx
 * @description
 * 이 파일은 Next.js 관리자 애플리케이션의 루트 레이아웃을 정의합니다.
 * 전역적인 UI 구조, 테마 프로바이더, 사이드바, 토스터 알림 시스템 등을 설정하여
 * 모든 페이지에 일관된 레이아웃과 기능을 제공합니다.
 *
 * 이 레이아웃은 애플리케이션의 최상위 컴포넌트로서, `children`으로 전달되는
 * 모든 페이지 콘텐츠를 감싸고 필요한 전역 컴포넌트와 컨텍스트를 주입합니다.
 *
 * 초보자 가이드:
 * 1.  **`metadata` 객체**: 애플리케이션의 전역 메타데이터(예: 페이지 제목, 설명)를 정의합니다.
 *     브라우저 탭에 표시되는 제목이나 검색 엔진 최적화(SEO)를 위해 이 부분을 수정할 수 있습니다.
 * 2.  **`RootLayout` 컴포넌트**:
 *     -   `ThemeProvider`: 애플리케이션 전체에 다크/라이트 모드 테마를 제공합니다.
 *     -   `SidebarProvider`: 사이드바의 상태(열림/닫힘)를 관리하는 컨텍스트를 제공합니다.
 *     -   `Sidebar`: 관리자 페이지의 주요 네비게이션을 담당하는 사이드바 컴포넌트입니다.
 *     -   `MainContent`: 실제 페이지 콘텐츠(`children`)가 렌더링되는 영역입니다.
 *     -   `Toaster` 및 `ShadcnToaster`: 사용자에게 알림 메시지를 표시하는 데 사용되는 토스터 컴포넌트입니다.
 *
 * 유지보수 팁:
 * -   **전역 스타일 변경**: `globals.css` 파일을 수정하여 전역 스타일을 변경할 수 있습니다.
 * -   **전역 메타데이터 수정**: `metadata` 객체의 `title` 또는 `description` 속성을 변경합니다.
 * -   **전역 프로바이더 추가/제거**: `RootLayout` 컴포넌트 내에서 `ThemeProvider`나 `SidebarProvider`와 같은
 *     프로바이더 컴포넌트를 추가하거나 제거할 수 있습니다.
 * -   **레이아웃 구조 변경**: `RootLayout` 컴포넌트의 JSX 구조를 수정하여 전체적인 페이지 레이아웃을 변경할 수 있습니다.
 *     예: 헤더, 푸터 등 새로운 전역 컴포넌트 추가.
 */


export const metadata = {
  title: 'JSScada Admin',
  description: 'PLC Data Collection & Monitoring System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="bg-gray-950 text-gray-100">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <SidebarProvider>
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              <MainContent>{children}</MainContent>
            </div>
          </SidebarProvider>
          <Toaster />
          <ShadcnToaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
