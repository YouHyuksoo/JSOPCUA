"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { 
  Moon, 
  Sun, 
  Search, 
  Bell, 
  User, 
  Settings, 
  LogOut,
  Activity,
  Server,
  CheckCircle2,
  AlertCircle,
  Loader2,
  X
} from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { getSystemStatus, SystemStatus } from "@/lib/api/system"
import { cn } from "@/lib/utils"

export function Header() {
  const { setTheme } = useTheme()
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [showSearch, setShowSearch] = useState(false)
  const [notificationCount] = useState(3)

  // 시스템 상태 폴링
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getSystemStatus()
        setSystemStatus(status)
      } catch (error) {
        console.error("Failed to fetch system status", error)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  // 검색 기능
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      // 검색 로직 구현 (예: 태그, PLC, 기계 검색)
      router.push(`/tags?search=${encodeURIComponent(searchQuery)}`)
      setSearchQuery("")
      setShowSearch(false)
    }
  }

  // 시스템 상태 배지
  const getStatusBadge = () => {
    if (!systemStatus) {
      return (
        <Badge variant="outline" className="bg-gray-800/50 border-gray-700 text-gray-400">
          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          Loading
        </Badge>
      )
    }

    const statusConfig = {
      running: { 
        color: "bg-green-500/10 text-green-500 border-green-500/20", 
        icon: CheckCircle2, 
        text: "Running" 
      },
      stopped: { 
        color: "bg-gray-500/10 text-gray-400 border-gray-500/20", 
        icon: Server, 
        text: "Stopped" 
      },
      starting: { 
        color: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20", 
        icon: Loader2, 
        text: "Starting" 
      },
      stopping: { 
        color: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20", 
        icon: Loader2, 
        text: "Stopping" 
      },
      unavailable: { 
        color: "bg-red-500/10 text-red-500 border-red-500/20", 
        icon: AlertCircle, 
        text: "Unavailable" 
      },
      error: { 
        color: "bg-red-500/10 text-red-500 border-red-500/20", 
        icon: AlertCircle, 
        text: "Error" 
      },
    }

    const config = statusConfig[systemStatus.status] || statusConfig.unavailable
    const Icon = config.icon

    return (
      <Badge className={cn("flex items-center gap-1.5 px-2.5 py-1", config.color)}>
        <Icon 
          className={cn(
            "h-3 w-3", 
            (systemStatus.status === "starting" || systemStatus.status === "stopping") && "animate-spin"
          )} 
        />
        <span className="text-xs font-medium">{config.text}</span>
      </Badge>
    )
  }

  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 bg-gray-950/95 backdrop-blur supports-[backdrop-filter]:bg-gray-950/60">
      <div className="flex h-16 items-center justify-between gap-4 px-6">
        {/* 왼쪽: 로고 및 제목 */}
        <div className="flex items-center gap-6">
          <div>
            <h1 className="text-xl font-bold text-white">JSScada Admin</h1>
            <p className="text-xs text-gray-400 hidden sm:block">PLC Data Collection & Monitoring</p>
          </div>
          
          {/* 시스템 상태 */}
          {getStatusBadge()}
        </div>

        {/* 중앙: 검색 */}
        <div className="flex-1 max-w-md mx-4">
          {showSearch ? (
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="text"
                placeholder="태그, PLC, 기계 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pr-10 bg-gray-900 border-gray-700 text-white placeholder:text-gray-500 focus:border-blue-500"
                autoFocus
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 text-gray-400 hover:text-white"
                onClick={() => {
                  setShowSearch(false)
                  setSearchQuery("")
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </form>
          ) : (
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-gray-400 hover:text-white hover:bg-gray-800/50"
              onClick={() => setShowSearch(true)}
            >
              <Search className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">검색...</span>
              <kbd className="ml-auto hidden lg:inline-flex h-5 select-none items-center gap-1 rounded border border-gray-700 bg-gray-900 px-1.5 font-mono text-[10px] font-medium text-gray-400">
                <span className="text-xs">⌘</span>K
              </kbd>
            </Button>
          )}
        </div>

        {/* 오른쪽: 액션 버튼들 */}
        <div className="flex items-center gap-2">
          {/* 알림 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon" 
                className="relative bg-gray-900/50 border-gray-800 hover:bg-gray-800"
              >
                <Bell className="h-5 w-5 text-gray-400" />
                {notificationCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 flex items-center justify-center text-[10px] font-bold text-white">
                    {notificationCount > 9 ? "9+" : notificationCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 bg-gray-900 border-gray-800">
              <DropdownMenuLabel className="text-white">알림</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-800" />
              <div className="p-4 text-center text-sm text-gray-400">
                새로운 알림이 없습니다
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* 시스템 모니터링 */}
          <Button
            variant="ghost"
            size="icon"
            className="bg-gray-900/50 border-gray-800 hover:bg-gray-800"
            onClick={() => router.push("/polling-ws")}
            title="시스템 모니터링"
          >
            <Activity className="h-5 w-5 text-gray-400" />
          </Button>

          {/* 테마 토글 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon" 
                className="bg-gray-900/50 border-gray-800 hover:bg-gray-800"
              >
                <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-gray-400" />
                <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-gray-400" />
                <span className="sr-only">테마 변경</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-gray-900 border-gray-800">
              <DropdownMenuItem 
                onClick={() => setTheme("light")} 
                className="text-gray-300 hover:bg-gray-800 cursor-pointer"
              >
                <Sun className="h-4 w-4 mr-2" />
                라이트 모드
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => setTheme("dark")} 
                className="text-gray-300 hover:bg-gray-800 cursor-pointer"
              >
                <Moon className="h-4 w-4 mr-2" />
                다크 모드
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => setTheme("system")} 
                className="text-gray-300 hover:bg-gray-800 cursor-pointer"
              >
                <Settings className="h-4 w-4 mr-2" />
                시스템 설정
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* 사용자 메뉴 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon" 
                className="bg-gray-900/50 border-gray-800 hover:bg-gray-800"
              >
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-gray-900 border-gray-800">
              <DropdownMenuLabel className="text-white">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">관리자</p>
                  <p className="text-xs text-gray-400">admin@jsscada.com</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-800" />
              <DropdownMenuItem 
                onClick={() => router.push("/settings")}
                className="text-gray-300 hover:bg-gray-800 cursor-pointer"
              >
                <Settings className="h-4 w-4 mr-2" />
                설정
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => router.push("/dashboard")}
                className="text-gray-300 hover:bg-gray-800 cursor-pointer"
              >
                <Activity className="h-4 w-4 mr-2" />
                대시보드
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-800" />
              <DropdownMenuItem 
                className="text-red-400 hover:bg-gray-800 cursor-pointer"
                onClick={() => {
                  // 로그아웃 로직
                  console.log("로그아웃")
                }}
              >
                <LogOut className="h-4 w-4 mr-2" />
                로그아웃
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
