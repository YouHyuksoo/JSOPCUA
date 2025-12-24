"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import {
  User,
  Settings,
  LogOut,
  Activity,
  Server,
  CheckCircle2,
  AlertCircle,
  Loader2
} from "lucide-react"
import { Button } from "@/components/ui/button"
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
  const router = useRouter()
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)

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
    const interval = setInterval(fetchStatus, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

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
        </div>

        {/* 중앙: 시스템 상태 */}
        <div className="flex-1 flex justify-center">
          {getStatusBadge()}
        </div>

        {/* 오른쪽: 액션 버튼들 */}
        <div className="flex items-center gap-2">
          {/* 시스템 모니터링 */}
          <Button
            variant="ghost"
            size="icon"
            className="hover:bg-gray-800"
            onClick={() => router.push("/polling-ws")}
            title="시스템 모니터링"
          >
            <Activity className="h-5 w-5 text-gray-400 hover:text-white" />
          </Button>

          {/* 설정 */}
          <Button
            variant="ghost"
            size="icon"
            className="hover:bg-gray-800"
            onClick={() => router.push("/settings")}
            title="설정"
          >
            <Settings className="h-5 w-5 text-gray-400 hover:text-white" />
          </Button>

          {/* 사용자 메뉴 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="hover:bg-gray-800"
              >
                <User className="h-5 w-5 text-gray-400 hover:text-white" />
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
