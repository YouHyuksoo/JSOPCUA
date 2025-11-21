'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  HelpCircle,
  Server,
  Database,
  Network,
  Tags,
  PlayCircle,
  Activity,
  FileText,
  Settings,
  Layout,
  DatabaseZap,
  ChevronDown,
  ChevronRight,
  Cpu,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Info,
  XCircle,
  RefreshCw,
  Plus,
  Edit,
  Trash2,
  Upload,
  Download,
  Play,
  Square,
  Zap,
  Search,
  Filter,
  Save,
  TestTube,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface AccordionItemProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

function AccordionItem({ title, icon, children, defaultOpen = false }: AccordionItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-gray-900 hover:bg-gray-800 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          {icon}
          <span className="text-white font-medium">{title}</span>
        </div>
        {isOpen ? (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        )}
      </button>
      {isOpen && (
        <div className="p-4 bg-gray-950 border-t border-gray-800">
          {children}
        </div>
      )}
    </div>
  );
}

export default function HelpPage() {
  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
          <HelpCircle className="h-8 w-8" />
          도움말
        </h1>
        <p className="text-gray-400 mt-1">JSSCADA 시스템 사용 가이드</p>
      </div>

      {/* 시스템 개요 */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-400" />
            시스템 개요
          </CardTitle>
          <CardDescription>JSSCADA 시스템의 전체 구조와 데이터 흐름</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-300">
            JSSCADA는 PLC(Programmable Logic Controller)에서 데이터를 수집하여 Oracle 데이터베이스에 저장하는
            산업용 데이터 수집 시스템입니다.
          </p>

          {/* 데이터 흐름 다이어그램 */}
          <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
            <h4 className="text-white font-semibold mb-4">데이터 흐름</h4>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              <div className="flex items-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <Cpu className="h-5 w-5 text-blue-400" />
                <span className="text-blue-400 text-sm font-medium">PLC</span>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-500" />
              <div className="flex items-center gap-2 px-3 py-2 bg-green-500/10 border border-green-500/20 rounded-lg">
                <Activity className="h-5 w-5 text-green-400" />
                <span className="text-green-400 text-sm font-medium">폴링 엔진</span>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-500" />
              <div className="flex items-center gap-2 px-3 py-2 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                <Database className="h-5 w-5 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">데이터 버퍼</span>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-500" />
              <div className="flex items-center gap-2 px-3 py-2 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                <DatabaseZap className="h-5 w-5 text-orange-400" />
                <span className="text-orange-400 text-sm font-medium">Oracle DB</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
              <h4 className="text-white font-semibold mb-2">주요 기능</h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                  미쓰비시 PLC (MC 3E 프로토콜) 통신
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                  실시간 데이터 폴링 및 모니터링
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                  Oracle 데이터베이스 자동 저장
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                  설비/태그/폴링그룹 관리
                </li>
              </ul>
            </div>
            <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
              <h4 className="text-white font-semibold mb-2">기술 스택</h4>
              <div className="flex flex-wrap gap-2">
                <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20">Next.js 14</Badge>
                <Badge className="bg-green-500/10 text-green-400 border-green-500/20">FastAPI</Badge>
                <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/20">SQLite</Badge>
                <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/20">Oracle</Badge>
                <Badge className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20">WebSocket</Badge>
                <Badge className="bg-yellow-500/10 text-yellow-400 border-yellow-500/20">pymcprotocol</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 메뉴별 도움말 */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white">메뉴별 기능 안내</CardTitle>
          <CardDescription>각 메뉴의 기능과 사용 방법</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <AccordionItem
            title="설비 (Machines)"
            icon={<Database className="h-5 w-5 text-blue-400" />}
            defaultOpen={true}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>생산 설비를 등록하고 관리합니다. 설비는 태그의 상위 분류 역할을 합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">주요 기능</h5>
                <ul className="space-y-1">
                  <li>• <strong>새 설비 추가:</strong> 설비 이름, 코드, 위치 정보 입력</li>
                  <li>• <strong>Oracle 동기화:</strong> ICOM_MACHINE_MASTER 테이블에서 설비 정보 가져오기</li>
                  <li>• <strong>설비 편집/삭제:</strong> 기존 설비 정보 수정 또는 삭제</li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="공정 (Workstages)"
            icon={<Network className="h-5 w-5 text-purple-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>생산 공정을 정의하고 관리합니다. 공정은 여러 설비를 그룹화합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">주요 기능</h5>
                <ul className="space-y-1">
                  <li>• <strong>공정 추가:</strong> 공정 이름, 설명, 순서 설정</li>
                  <li>• <strong>Oracle 동기화:</strong> Oracle에서 공정 정보 가져오기</li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="PLCs"
            icon={<Server className="h-5 w-5 text-green-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>PLC 연결 정보를 등록하고 관리합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">설정 항목</h5>
                <ul className="space-y-1">
                  <li>• <strong>PLC 코드:</strong> PLC 식별 코드</li>
                  <li>• <strong>IP 주소/포트:</strong> PLC 네트워크 주소 (기본 포트: 5000)</li>
                  <li>• <strong>프로토콜:</strong> MC3E (미쓰비시 3E 프로토콜)</li>
                  <li>• <strong>네트워크 번호/국번:</strong> MC 프로토콜 설정</li>
                  <li>• <strong>연결 테스트:</strong> D100, W100, M100 레지스터 읽기 테스트</li>
                </ul>
              </div>
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <p className="text-yellow-200 text-xs">
                    PLC가 비활성 상태이면 폴링이 실행되지 않습니다. 반드시 활성 상태로 설정하세요.
                  </p>
                </div>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="태그 (Tags)"
            icon={<Tags className="h-5 w-5 text-cyan-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>PLC에서 읽어올 데이터 포인트(태그)를 정의합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">태그 속성</h5>
                <ul className="space-y-1">
                  <li>• <strong>태그 주소:</strong> PLC 메모리 주소 (예: D100, W200, M0)</li>
                  <li>• <strong>태그 이름:</strong> 데이터 식별 이름</li>
                  <li>• <strong>데이터 타입:</strong> WORD, DWORD, BIT, FLOAT 등</li>
                  <li>• <strong>스케일:</strong> 읽은 값에 곱할 배율</li>
                </ul>
              </div>
              <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-blue-200 text-xs">
                    CSV 업로드 기능으로 대량의 태그를 한번에 등록할 수 있습니다.
                  </p>
                </div>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="폴링그룹 (Polling Groups)"
            icon={<PlayCircle className="h-5 w-5 text-yellow-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>태그들을 그룹으로 묶어 동일한 주기로 폴링합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">설정 항목</h5>
                <ul className="space-y-1">
                  <li>• <strong>그룹 이름:</strong> 폴링 그룹 식별 이름</li>
                  <li>• <strong>PLC 연결:</strong> 이 그룹이 사용할 PLC</li>
                  <li>• <strong>폴링 주기:</strong> 데이터 수집 간격 (밀리초)</li>
                  <li>• <strong>폴링 모드:</strong> FIXED(고정 주기) / HANDSHAKE(수동 트리거)</li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="폴링모니터 (Polling Monitor)"
            icon={<Activity className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>폴링 엔진의 실시간 상태를 모니터링하고 제어합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">주요 기능</h5>
                <ul className="space-y-1">
                  <li>• <strong>PLC 확인:</strong> PLC 연결 상태 테스트 (시작 전 필수)</li>
                  <li>• <strong>시작/중지:</strong> 개별 또는 전체 폴링 그룹 제어</li>
                  <li>• <strong>실시간 통계:</strong> 폴링 횟수, 성공률, 평균 시간</li>
                  <li>• <strong>오류 표시:</strong> 마지막 오류 메시지 및 재시도 정보</li>
                </ul>
              </div>
              <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <p className="text-green-200 text-xs">
                    WebSocket을 통해 실시간으로 상태가 업데이트됩니다.
                  </p>
                </div>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="서버데이터 (Oracle Data)"
            icon={<DatabaseZap className="h-5 w-5 text-orange-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>Oracle 데이터베이스에 저장된 데이터를 조회합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">조회 가능한 테이블</h5>
                <ul className="space-y-1">
                  <li>• <strong>XSCADA_OPERATION:</strong> 설비 가동 상태 데이터</li>
                  <li>• <strong>XSCADA_DATATAG_LOG:</strong> 태그 값 변경 로그</li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="모니터레이아웃 (Monitor Layout)"
            icon={<Layout className="h-5 w-5 text-indigo-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>설비 모니터링 화면의 레이아웃을 편집합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">주요 기능</h5>
                <ul className="space-y-1">
                  <li>• <strong>드래그 앤 드롭:</strong> 설비 박스 위치 조정</li>
                  <li>• <strong>좌표 입력:</strong> 정밀한 위치 지정</li>
                  <li>• <strong>저장:</strong> 레이아웃 설정 저장</li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="로그 (Logs)"
            icon={<FileText className="h-5 w-5 text-gray-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>시스템 로그 파일을 조회합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">로그 종류</h5>
                <ul className="space-y-1">
                  <li>• <strong>scada.log:</strong> 메인 시스템 로그</li>
                  <li>• <strong>error.log:</strong> 오류 로그</li>
                  <li>• <strong>polling.log:</strong> 폴링 관련 로그</li>
                  <li>• <strong>plc.log:</strong> PLC 통신 로그</li>
                  <li>• <strong>oracle_writer.log:</strong> Oracle 저장 로그</li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem
            title="시스템설정 (Settings)"
            icon={<Settings className="h-5 w-5 text-gray-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <p>시스템 환경 변수(.env)를 설정합니다.</p>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">설정 항목</h5>
                <ul className="space-y-1">
                  <li>• <strong>데이터베이스:</strong> SQLite 경로</li>
                  <li>• <strong>API 서버:</strong> FastAPI 호스트/포트</li>
                  <li>• <strong>Oracle:</strong> 연결 정보 (호스트, 포트, 서비스명, 계정)</li>
                  <li>• <strong>버퍼:</strong> 데이터 버퍼 크기, 배치 사이즈</li>
                </ul>
              </div>
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <p className="text-yellow-200 text-xs">
                    설정 변경 후 백엔드 서버를 재시작해야 적용됩니다.
                  </p>
                </div>
              </div>
            </div>
          </AccordionItem>
        </CardContent>
      </Card>

      {/* 버튼 기능 설명 */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-400" />
            버튼 기능 설명
          </CardTitle>
          <CardDescription>각 화면에서 사용되는 버튼들의 기능</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 공통 버튼 */}
          <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
            <h4 className="text-white font-semibold mb-3">공통 버튼</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 rounded text-white text-xs">
                  <Plus className="h-3 w-3" />
                  <span>새 항목 추가</span>
                </div>
                <span className="text-gray-400 text-sm">새로운 데이터를 등록합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 rounded text-white text-xs">
                  <Edit className="h-3 w-3" />
                </div>
                <span className="text-gray-400 text-sm">선택한 항목을 편집합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-red-600/20 text-red-400 rounded text-xs">
                  <Trash2 className="h-3 w-3" />
                </div>
                <span className="text-gray-400 text-sm">선택한 항목을 삭제합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 rounded text-white text-xs">
                  <Save className="h-3 w-3" />
                  <span>저장</span>
                </div>
                <span className="text-gray-400 text-sm">변경 사항을 저장합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 rounded text-white text-xs">
                  <RefreshCw className="h-3 w-3" />
                  <span>Oracle 동기화</span>
                </div>
                <span className="text-gray-400 text-sm">Oracle DB에서 데이터를 가져옵니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 rounded text-white text-xs">
                  <Search className="h-3 w-3" />
                </div>
                <span className="text-gray-400 text-sm">목록에서 항목을 검색합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 rounded text-white text-xs">
                  <Filter className="h-3 w-3" />
                </div>
                <span className="text-gray-400 text-sm">조건에 따라 필터링합니다</span>
              </div>
            </div>
          </div>

          {/* PLC 관련 버튼 */}
          <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
            <h4 className="text-white font-semibold mb-3">PLC 관련 버튼</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 rounded text-white text-xs">
                  <TestTube className="h-3 w-3" />
                  <span>연결 테스트</span>
                </div>
                <span className="text-gray-400 text-sm">PLC 통신 연결을 테스트합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 rounded text-white text-xs">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>PLC 확인</span>
                </div>
                <span className="text-gray-400 text-sm">폴링 전 PLC 연결 상태를 확인합니다</span>
              </div>
            </div>
          </div>

          {/* 폴링 제어 버튼 */}
          <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
            <h4 className="text-white font-semibold mb-3">폴링 제어 버튼</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-green-600 rounded text-white text-xs">
                  <Play className="h-3 w-3" />
                  <span>시작</span>
                </div>
                <span className="text-gray-400 text-sm">폴링 그룹을 시작합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-red-600 rounded text-white text-xs">
                  <Square className="h-3 w-3" />
                  <span>중지</span>
                </div>
                <span className="text-gray-400 text-sm">폴링 그룹을 중지합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-green-600 rounded text-white text-xs">
                  <Play className="h-3 w-3" />
                  <span>전체 시작</span>
                </div>
                <span className="text-gray-400 text-sm">모든 폴링 그룹을 시작합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-red-600 rounded text-white text-xs">
                  <Square className="h-3 w-3" />
                  <span>전체 중지</span>
                </div>
                <span className="text-gray-400 text-sm">모든 폴링 그룹을 중지합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 rounded text-white text-xs">
                  <Zap className="h-3 w-3" />
                  <span>수동 트리거</span>
                </div>
                <span className="text-gray-400 text-sm">HANDSHAKE 모드에서 1회 폴링</span>
              </div>
            </div>
          </div>

          {/* 태그 관련 버튼 */}
          <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
            <h4 className="text-white font-semibold mb-3">태그 관련 버튼</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 rounded text-white text-xs">
                  <Upload className="h-3 w-3" />
                  <span>CSV 업로드</span>
                </div>
                <span className="text-gray-400 text-sm">CSV 파일로 태그를 일괄 등록합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 rounded text-white text-xs">
                  <Download className="h-3 w-3" />
                  <span>템플릿 다운로드</span>
                </div>
                <span className="text-gray-400 text-sm">CSV 업로드용 템플릿을 다운로드합니다</span>
              </div>
            </div>
          </div>

          {/* 로그 관련 버튼 */}
          <div className="p-4 bg-gray-950 rounded-lg border border-gray-800">
            <h4 className="text-white font-semibold mb-3">로그 관련 버튼</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 rounded text-white text-xs">
                  <Search className="h-3 w-3" />
                  <span>조회</span>
                </div>
                <span className="text-gray-400 text-sm">선택한 로그 파일을 조회합니다</span>
              </div>
              <div className="flex items-center gap-3 p-2 bg-gray-900 rounded">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-red-600 rounded text-white text-xs">
                  <Trash2 className="h-3 w-3" />
                  <span>로그 삭제</span>
                </div>
                <span className="text-gray-400 text-sm">선택한 로그 파일을 삭제합니다</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 오류 해결 가이드 */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-400" />
            오류 해결 가이드
          </CardTitle>
          <CardDescription>자주 발생하는 오류와 해결 방법</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* PLC 연결 오류 */}
          <AccordionItem
            title="PLC 연결 실패"
            icon={<Server className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">PLC 연결 테스트 실패, 폴링 시작 불가</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">IP 주소/포트 확인</p>
                      <p className="text-gray-400 text-xs">PLC의 IP 주소와 포트(기본 5000)가 올바른지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">네트워크 연결 확인</p>
                      <p className="text-gray-400 text-xs">서버에서 PLC로 ping이 되는지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">방화벽 확인</p>
                      <p className="text-gray-400 text-xs">서버와 PLC 간 방화벽에서 해당 포트가 열려있는지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">4.</span>
                    <div>
                      <p className="text-white">PLC 설정 확인</p>
                      <p className="text-gray-400 text-xs">PLC의 이더넷 통신 설정(MC 프로토콜)이 활성화되어 있는지 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          {/* Oracle 연결 오류 */}
          <AccordionItem
            title="Oracle 연결 실패"
            icon={<DatabaseZap className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">Oracle 연결 테스트 실패, 데이터 동기화 불가</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">연결 정보 확인</p>
                      <p className="text-gray-400 text-xs">호스트, 포트, 서비스명이 올바른지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">계정 정보 확인</p>
                      <p className="text-gray-400 text-xs">사용자명과 비밀번호가 올바른지 확인하세요 (대소문자 구분).</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">네트워크 확인</p>
                      <p className="text-gray-400 text-xs">Oracle 서버(기본 1521 포트)에 접근 가능한지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">4.</span>
                    <div>
                      <p className="text-white">Oracle 서비스 상태</p>
                      <p className="text-gray-400 text-xs">Oracle 데이터베이스 서비스가 실행 중인지 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          {/* 폴링 시작 불가 */}
          <AccordionItem
            title="폴링 시작 버튼이 비활성화됨"
            icon={<PlayCircle className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">폴링 모니터에서 시작 버튼이 회색으로 비활성화됨</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">PLC 확인 버튼 클릭</p>
                      <p className="text-gray-400 text-xs">"PLC 확인" 버튼을 눌러 PLC 연결 상태를 먼저 확인해야 합니다.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">PLC 활성 상태 확인</p>
                      <p className="text-gray-400 text-xs">PLCs 메뉴에서 해당 PLC가 "활성" 상태인지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">태그 할당 확인</p>
                      <p className="text-gray-400 text-xs">폴링 그룹에 활성 태그가 할당되어 있는지 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          {/* API 연결 오류 */}
          <AccordionItem
            title="API 서버 연결 실패"
            icon={<Server className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">페이지 로딩 실패, "Failed to fetch" 오류, 데이터 조회 불가</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">백엔드 서버 상태 확인</p>
                      <p className="text-gray-400 text-xs">FastAPI 백엔드 서버가 실행 중인지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">API 포트 확인</p>
                      <p className="text-gray-400 text-xs">백엔드 서버가 올바른 포트(기본 8000)에서 실행 중인지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">CORS 설정 확인</p>
                      <p className="text-gray-400 text-xs">시스템설정에서 CORS Origins에 프론트엔드 주소가 포함되어 있는지 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          {/* WebSocket 연결 오류 */}
          <AccordionItem
            title="WebSocket 연결 끊김"
            icon={<Activity className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">폴링 모니터에서 "WS 끊김" 표시, 실시간 업데이트 안됨</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">재연결 버튼 클릭</p>
                      <p className="text-gray-400 text-xs">"재연결" 링크를 클릭하여 WebSocket 연결을 다시 시도하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">페이지 새로고침</p>
                      <p className="text-gray-400 text-xs">브라우저에서 페이지를 새로고침하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">백엔드 서버 확인</p>
                      <p className="text-gray-400 text-xs">백엔드 서버가 정상 실행 중인지 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          {/* CSV 업로드 오류 */}
          <AccordionItem
            title="CSV 업로드 실패"
            icon={<Upload className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">CSV 파일 업로드 시 오류 발생, 필수 컬럼 누락 경고</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">템플릿 사용</p>
                      <p className="text-gray-400 text-xs">"템플릿 다운로드" 버튼으로 올바른 형식의 템플릿을 다운로드하여 사용하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">필수 컬럼 확인</p>
                      <p className="text-gray-400 text-xs">PLC_CODE, MACHINE_CODE, TAG_ADDRESS, TAG_NAME 컬럼이 있는지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">인코딩 확인</p>
                      <p className="text-gray-400 text-xs">CSV 파일이 UTF-8 인코딩인지 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>

          {/* 폴링 오류 */}
          <AccordionItem
            title="폴링 중 오류 발생"
            icon={<AlertTriangle className="h-5 w-5 text-red-400" />}
          >
            <div className="space-y-3 text-gray-300 text-sm">
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-300 font-medium">증상</p>
                <p className="text-red-200 text-xs mt-1">폴링 모니터에 빨간색 오류 메시지 표시, 연속 실패 카운트 증가</p>
              </div>
              <div className="p-3 bg-gray-900 rounded-lg">
                <h5 className="text-white font-medium mb-2">원인 및 해결 방법</h5>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">1.</span>
                    <div>
                      <p className="text-white">오류 메시지 확인</p>
                      <p className="text-gray-400 text-xs">폴링 모니터의 "마지막 오류" 메시지를 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">2.</span>
                    <div>
                      <p className="text-white">PLC 상태 확인</p>
                      <p className="text-gray-400 text-xs">PLC가 정상 동작 중인지, 네트워크가 연결되어 있는지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">3.</span>
                    <div>
                      <p className="text-white">태그 주소 확인</p>
                      <p className="text-gray-400 text-xs">등록된 태그 주소가 PLC에 존재하는지 확인하세요.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">4.</span>
                    <div>
                      <p className="text-white">로그 확인</p>
                      <p className="text-gray-400 text-xs">로그 메뉴에서 polling.log, plc.log를 확인하세요.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </AccordionItem>
        </CardContent>
      </Card>

      {/* 빠른 시작 가이드 */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-400" />
            빠른 시작 가이드
          </CardTitle>
          <CardDescription>처음 사용하시는 분을 위한 단계별 안내</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-4 items-start">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-sm flex-shrink-0">
                1
              </div>
              <div>
                <h4 className="text-white font-medium">시스템 설정 확인</h4>
                <p className="text-gray-400 text-sm">시스템설정 메뉴에서 Oracle 연결 정보를 입력하고 연결 테스트를 수행합니다.</p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-sm flex-shrink-0">
                2
              </div>
              <div>
                <h4 className="text-white font-medium">PLC 등록</h4>
                <p className="text-gray-400 text-sm">PLCs 메뉴에서 PLC를 등록하고 연결 테스트로 통신을 확인합니다.</p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-sm flex-shrink-0">
                3
              </div>
              <div>
                <h4 className="text-white font-medium">설비 및 태그 등록</h4>
                <p className="text-gray-400 text-sm">설비와 태그를 등록하거나 Oracle에서 동기화합니다.</p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-sm flex-shrink-0">
                4
              </div>
              <div>
                <h4 className="text-white font-medium">폴링그룹 설정</h4>
                <p className="text-gray-400 text-sm">폴링그룹을 생성하고 태그들을 할당합니다.</p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white font-bold text-sm flex-shrink-0">
                5
              </div>
              <div>
                <h4 className="text-white font-medium">폴링 시작</h4>
                <p className="text-gray-400 text-sm">폴링모니터에서 PLC 연결을 확인하고 폴링을 시작합니다.</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 문의 */}
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="pt-6">
          <div className="text-center text-gray-400 text-sm">
            <p>추가 문의사항이 있으시면 시스템 관리자에게 연락하세요.</p>
            <p className="mt-2 text-xs text-gray-500">JSSCADA Admin v1.0</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
