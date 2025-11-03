import './globals.css'
import { Toaster } from '@/components/ui/sonner'

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
    <html lang="ko">
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  )
}
