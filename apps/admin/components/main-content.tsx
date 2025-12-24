"use client"

import { useSidebar } from "./sidebar-context"
import { cn } from "@/lib/utils"
import { Header } from "./header"

interface MainContentProps {
  children: React.ReactNode
}

export function MainContent({ children }: MainContentProps) {
  const { isCollapsed } = useSidebar()

  return (
    <div
      className={cn(
        "flex flex-1 flex-col overflow-hidden transition-all duration-300",
        isCollapsed ? "pl-16" : "pl-64"
      )}
    >
      <Header />
      <main className="flex-1 overflow-y-auto bg-gray-950 p-6">
        {children}
      </main>
    </div>
  )
}
