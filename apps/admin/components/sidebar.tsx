"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Database,
  Network,
  Server,
  Tags,
  PlayCircle,
  FileText,
  Activity,
} from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "설비 (Machines)", href: "/machines", icon: Database },
  { name: "공정 (Processes)", href: "/processes", icon: Network },
  { name: "PLCs", href: "/plcs", icon: Server },
  { name: "Tags", href: "/tags", icon: Tags },
  { name: "Polling Groups", href: "/polling-groups", icon: PlayCircle },
  { name: "Polling Monitor", href: "/polling-ws", icon: Activity },
  { name: "Logs", href: "/logs", icon: FileText },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col fixed inset-y-0 z-50 bg-gray-900 border-r border-gray-800">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-gray-800 px-6">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Server className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">JSScada</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`)
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-gray-800",
                isActive
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:text-white"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-800 p-4">
        <p className="text-xs text-gray-500 text-center">
          JSScada Admin v1.0
        </p>
      </div>
    </div>
  )
}
