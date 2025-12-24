import Link from 'next/link'

export default function Nav() {
  return (
    <nav className="border-b bg-white">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">JSScada Admin</Link>
          <div className="flex gap-4">
            <Link href="/lines" className="hover:underline">라인</Link>
            <Link href="/workstages" className="hover:underline">공정</Link>
            <Link href="/plcs" className="hover:underline">PLC</Link>
            <Link href="/tags" className="hover:underline">태그</Link>
            <Link href="/polling-groups" className="hover:underline">폴링그룹</Link>
            <Link href="/dashboard" className="hover:underline">대시보드</Link>
            <Link href="/logs" className="hover:underline">로그</Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
