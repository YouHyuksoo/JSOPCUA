import Nav from '@/components/nav'
import Link from 'next/link'

export default function Home() {
  return (
    <>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-4">JSScada 관리 시스템</h1>
        <p className="mb-8">PLC 데이터 수집 및 모니터링 시스템</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link href="/lines" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">라인 관리</h2>
            <p className="text-gray-600">생산 라인 CRUD</p>
          </Link>
          <Link href="/processes" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">공정 관리</h2>
            <p className="text-gray-600">공정 CRUD</p>
          </Link>
          <Link href="/plcs" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">PLC 관리</h2>
            <p className="text-gray-600">PLC 연결 정보 관리 및 테스트</p>
          </Link>
          <Link href="/tags" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">태그 관리</h2>
            <p className="text-gray-600">태그 CRUD 및 CSV 업로드</p>
          </Link>
          <Link href="/polling-groups" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">폴링 그룹</h2>
            <p className="text-gray-600">폴링 그룹 설정 및 제어</p>
          </Link>
          <Link href="/dashboard" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">시스템 대시보드</h2>
            <p className="text-gray-600">실시간 시스템 상태 모니터링</p>
          </Link>
          <Link href="/logs" className="p-6 border rounded-lg hover:shadow-md">
            <h2 className="text-xl font-semibold mb-2">로그 조회</h2>
            <p className="text-gray-600">시스템 로그 검색 및 필터링</p>
          </Link>
        </div>
      </div>
    </>
  )
}
