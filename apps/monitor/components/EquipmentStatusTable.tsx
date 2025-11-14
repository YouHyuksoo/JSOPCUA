"use client";

interface EquipmentStatusTableProps {
  equipment: any[];
  alarmStatistics: any[];
}

// 17개 설비 정보 (PDF 기준)
const EQUIPMENT_LIST = [
  { num: 1, name: "Upper\n로딩", fullName: "1-Upper 로딩" },
  { num: 2, name: "Lower\n로딩", fullName: "2-Lower 로딩" },
  { num: 3, name: "Upper\n브라켓\n용접", fullName: "3-Upper 브라켓 용접" },
  { num: 4, name: "Lower\n브라켓\n용접", fullName: "4-Lower 브라켓 용접" },
  { num: 5, name: "U/L\n댐핑시\n공급", fullName: "5-U/L 댐핑시 공급" },
  { num: 6, name: "U/L\n가열로", fullName: "6-U/L 가열로" },
  { num: 7, name: "U/L\n쿨링", fullName: "7-U/L 쿨링" },
  { num: 8, name: "실런트\n도포", fullName: "8-실런트 도포" },
  { num: 9, name: "센터\n로딩", fullName: "9-센터 로딩" },
  { num: 10, name: "센터\n댐핑시\n공급", fullName: "10-센터 댐핑시 공급" },
  { num: 11, name: "센터\n가열로", fullName: "11-센터 가열로" },
  { num: 12, name: "센터\n쿨링", fullName: "12-센터 쿨링" },
  { num: 13, name: "U\n밴딩", fullName: "13-U 밴딩" },
  { num: 14, name: "Tub\n브라켓\n용접", fullName: "14-Tub 브라켓 용접" },
  { num: 15, name: "Tub\n가조립", fullName: "15-Tub 가조립" },
  { num: 16, name: "Shuttle\n#1", fullName: "16-Shuttle #1" },
  { num: 17, name: "시밍\n#1", fullName: "17-시밍 #1" },
];

// 더미 데이터 생성 함수 (고정값 사용 - hydration 오류 방지)
const DUMMY_CYCLE_TIMES = [
  "14.2",
  "14.5",
  "13.9",
  "14.1",
  "14.3",
  "13.8",
  "14.6",
  "14.0",
  "13.7",
  "14.4",
  "14.9",
  "13.6",
  "14.8",
  "14.2",
  "13.9",
  "14.5",
  "14.7",
];

const generateDummyData = (num: number) => {
  // 8번 설비는 알람 1개 (PDF 이미지 기준)
  const alarmCount = num === 8 ? 1 : 0;
  const generalCount = num === 8 ? 1 : 0;

  // C/Time 값 (고정값 사용)
  const cycleTime = DUMMY_CYCLE_TIMES[num - 1] || "14.0";

  return {
    alarmCount,
    generalCount,
    cycleTime,
    stopRate: "0.0%",
  };
};

export function EquipmentStatusTable({
  equipment,
  alarmStatistics,
}: EquipmentStatusTableProps) {
  return (
    <div
      style={{
        backgroundColor: "#000000",
        padding: "8px",
        borderBottom: "1px solid #374151",
      }}
    >
      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            fontSize: "12px",
            borderCollapse: "collapse",
          }}
        >
          {/* 헤더: 설비 번호 및 이름 */}
          <thead>
            <tr style={{ borderBottom: "1px solid #4B5563" }}>
              <th
                style={{
                  textAlign: "left",
                  padding: "8px",
                  fontWeight: 500,
                  color: "#D1D5DB",
                  position: "sticky",
                  left: 0,
                  backgroundColor: "#000000",
                  zIndex: 10,
                  width: "96px",
                  border: "1px solid #4B5563",
                  borderRight: "2px solid #6B7280",
                }}
              >
                구분
              </th>
              {EQUIPMENT_LIST.map((eq) => {
                return (
                  <th
                    key={eq.num}
                    style={{
                      textAlign: "center",
                      padding: "8px 4px",
                      fontWeight: 500,
                      color: "#D1D5DB",
                      width: "80px",
                      border: "1px solid #4B5563",
                      backgroundColor:
                        eq.num === 8 ? "rgba(127, 29, 29, 0.3)" : "#1F2937",
                    }}
                  >
                    <div
                      style={{
                        fontWeight: "bold",
                        whiteSpace: "pre-line",
                        lineHeight: "1.25",
                      }}
                    >
                      {eq.name}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>

          <tbody>
            {/* 알람 합계 */}
            <tr style={{ borderBottom: "1px solid #4B5563" }}>
              <td
                style={{
                  padding: "4px 8px",
                  fontWeight: 500,
                  color: "#D1D5DB",
                  position: "sticky",
                  left: 0,
                  backgroundColor: "#000000",
                  zIndex: 10,
                  border: "1px solid #4B5563",
                  borderRight: "2px solid #6B7280",
                }}
              >
                알람 합계
              </td>
              {EQUIPMENT_LIST.map((eq) => {
                const data = generateDummyData(eq.num);
                return (
                  <td
                    key={eq.num}
                    style={{
                      textAlign: "center",
                      padding: "4px",
                      border: "1px solid #4B5563",
                      backgroundColor:
                        eq.num === 8 ? "rgba(127, 29, 29, 0.3)" : "#1F2937",
                    }}
                  >
                    <span
                      style={{
                        color: data.alarmCount > 0 ? "#F87171" : "#9CA3AF",
                        fontWeight: data.alarmCount > 0 ? "bold" : "normal",
                      }}
                    >
                      {data.alarmCount}
                    </span>
                  </td>
                );
              })}
            </tr>

            {/* 이상 감지 섹션 */}
            <tr style={{ borderBottom: "1px solid #4B5563" }}>
              <td
                style={{
                  padding: "4px 8px",
                  fontWeight: 500,
                  color: "#D1D5DB",
                  position: "sticky",
                  left: 0,
                  backgroundColor: "#000000",
                  zIndex: 10,
                  fontSize: "12px",
                  border: "1px solid #4B5563",
                  borderRight: "2px solid #6B7280",
                }}
              >
                이상감지 일반
              </td>
              {EQUIPMENT_LIST.map((eq) => {
                const data = generateDummyData(eq.num);
                return (
                  <td
                    key={eq.num}
                    style={{
                      textAlign: "center",
                      padding: "4px",
                      border: "1px solid #4B5563",
                      backgroundColor:
                        eq.num === 8 ? "rgba(127, 29, 29, 0.3)" : "#1F2937",
                    }}
                  >
                    <span
                      style={{
                        color: data.generalCount > 0 ? "#FBBF24" : "#6B7280",
                        fontWeight: data.generalCount > 0 ? "bold" : "normal",
                      }}
                    >
                      {data.generalCount}
                    </span>
                  </td>
                );
              })}
            </tr>

            {/* C/Time (10초) */}
            <tr style={{ borderBottom: "1px solid #4B5563" }}>
              <td
                style={{
                  padding: "4px 8px",
                  fontWeight: 500,
                  color: "#D1D5DB",
                  position: "sticky",
                  left: 0,
                  backgroundColor: "#000000",
                  zIndex: 10,
                  border: "1px solid #4B5563",
                  borderRight: "2px solid #6B7280",
                }}
              >
                C/Time(10초)
              </td>
              {EQUIPMENT_LIST.map((eq) => {
                const data = generateDummyData(eq.num);
                return (
                  <td
                    key={eq.num}
                    style={{
                      textAlign: "center",
                      padding: "4px",
                      border: "1px solid #4B5563",
                      backgroundColor:
                        eq.num === 8 ? "rgba(127, 29, 29, 0.3)" : "#1F2937",
                    }}
                  >
                    <span style={{ color: "#E5E7EB", fontFamily: "monospace" }}>
                      {data.cycleTime}
                    </span>
                  </td>
                );
              })}
            </tr>

            {/* 정지율(%) */}
            <tr>
              <td
                style={{
                  padding: "4px 8px",
                  fontWeight: 500,
                  color: "#D1D5DB",
                  position: "sticky",
                  left: 0,
                  backgroundColor: "#000000",
                  zIndex: 10,
                  border: "1px solid #4B5563",
                  borderRight: "2px solid #6B7280",
                }}
              >
                정지율(%)
              </td>
              {EQUIPMENT_LIST.map((eq) => {
                const data = generateDummyData(eq.num);
                return (
                  <td
                    key={eq.num}
                    style={{
                      textAlign: "center",
                      padding: "4px",
                      border: "1px solid #4B5563",
                      backgroundColor:
                        eq.num === 8 ? "rgba(127, 29, 29, 0.3)" : "#1F2937",
                    }}
                  >
                    <span style={{ color: "#E5E7EB" }}>{data.stopRate}</span>
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
