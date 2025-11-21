"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useSidebar } from "./sidebar-context"
import {
  LayoutDashboard,
  Database,
  Network,
  Server,
  Tags,
  PlayCircle,
  FileText,
  Activity,
  Settings,
  Layout,
  DatabaseZap,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
} from "lucide-react"

/**
 * @file apps/admin/components/sidebar.tsx
 * @description
 * 이 파일은 관리자 페이지의 사이드바(Sidebar) 컴포넌트를 정의합니다.
 * Next.js의 Link 컴포넌트와 `usePathname` 훅을 사용하여 현재 경로에 따라
 * 활성 링크를 시각적으로 표시하며, `lucide-react` 아이콘들을 사용하여
 * 각 메뉴 항목에 시각적인 요소를 추가합니다.
 *
 * 접기/펼치기 기능:
 * - 하단의 토글 버튼을 클릭하면 사이드바가 접히거나 펼쳐집니다.
 * - 접힌 상태에서는 아이콘만 표시되고, 마우스를 올리면 툴팁으로 메뉴 이름이 표시됩니다.
 * - 상태는 localStorage에 저장되어 새로고침 후에도 유지됩니다.
 */

const navigation = [
  { name: "대시보드", href: "/dashboard", icon: LayoutDashboard },
  { name: "설비", href: "/machines", icon: Database },
  { name: "공정", href: "/workstages", icon: Network },
  { name: "PLCs", href: "/plcs", icon: Server },
  { name: "태그", href: "/tags", icon: Tags },
  { name: "폴링그룹", href: "/polling-groups", icon: PlayCircle },
  { name: "폴링모니터", href: "/polling-ws", icon: Activity },
  { name: "서버데이터", href: "/oracle-data", icon: DatabaseZap },
  { name: "모니터레이아웃", href: "/monitor-layout", icon: Layout },
  { name: "로그", href: "/logs", icon: FileText },
  { name: "시스템설정", href: "/settings", icon: Settings },
  { name: "도움말", href: "/help", icon: HelpCircle },
]

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, toggleSidebar } = useSidebar()

  return (
    <div
      className={cn(
        "flex h-full flex-col fixed inset-y-0 z-50 bg-gray-900 border-r border-gray-800 transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-gray-800 px-4">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
            <Server className="h-5 w-5 text-white" />
          </div>
          {!isCollapsed && (
            <span className="text-xl font-bold text-white whitespace-nowrap">JSSCADA</span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2 py-4 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`)
          return (
            <Link
              key={item.name}
              href={item.href}
              title={isCollapsed ? item.name : undefined}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-gray-800",
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:text-white",
                isCollapsed && "justify-center px-2"
              )}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!isCollapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Toggle Button */}
      <div className="border-t border-gray-800 p-2">
        <button
          onClick={toggleSidebar}
          className="flex items-center justify-center w-full h-10 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
          title={isCollapsed ? "사이드바 펼치기" : "사이드바 접기"}
        >
          {isCollapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <>
              <ChevronLeft className="h-5 w-5 mr-2" />
              <span className="text-sm">접기</span>
            </>
          )}
        </button>
      </div>

      {/* Footer */}
      {!isCollapsed && (
        <div className="border-t border-gray-800 p-4">
          <p className="text-xs text-gray-500 text-center">
            JSSCADA Admin 1.0
          </p>
        </div>
      )}
    </div>
  )
}
