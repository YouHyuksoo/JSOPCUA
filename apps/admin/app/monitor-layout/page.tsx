'use client';

import { useEffect, useState, useRef } from 'react';
import { getEquipmentPositions, saveEquipmentPositions, EquipmentPosition, getTagsForMonitor, TagForMonitor } from '@/lib/api/monitor';
import { getWorkstages } from '@/lib/api/workstages';
import { Workstage } from '@/lib/types/workstage';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Save, RotateCcw, Grid3x3 } from 'lucide-react';

interface DraggableBox {
  process_code: string;
  process_name: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  z_index: number;
  isDragging: boolean;
  isResizing: boolean;
  // PLC 태그 매핑
  tag_id?: number | null;
  tag_address?: string | null;
  plc_code?: string | null;
  machine_code?: string | null;
}

export default function MonitorLayoutPage() {
  const [processes, setProcesses] = useState<Workstage[]>([]);
  const [boxes, setBoxes] = useState<DraggableBox[]>([]);
  const [tags, setTags] = useState<TagForMonitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [backgroundImageUrl, setBackgroundImageUrl] = useState('/equipment-layout.png');
  const [selectedBox, setSelectedBox] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragStartPos = useRef<{ x: number; y: number } | null>(null);
  const dragBoxRef = useRef<string | null>(null);
  const resizeStartPos = useRef<{ x: number; y: number; width: number; height: number } | null>(null);
  const resizeBoxRef = useRef<string | null>(null);

  // 공정 목록 조회
  useEffect(() => {
    const fetchProcesses = async () => {
      try {
        const data = await getWorkstages(1, 100);
        setProcesses(data.items);
      } catch (error) {
        toast.error('공정 목록 조회 실패');
      }
    };
    fetchProcesses();
  }, []);

  // 태그 목록 조회
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const tagsList = await getTagsForMonitor();
        setTags(tagsList);
      } catch (error) {
        console.error('태그 목록 조회 실패:', error);
      }
    };
    fetchTags();
  }, []);

  // 위치 정보 조회
  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const positionsData = await getEquipmentPositions('default');
        
        // 공정 목록과 위치 정보를 결합
        const initialBoxes: DraggableBox[] = processes.map((process) => {
          const position = positionsData.positions[process.workstage_code];
          return {
            process_code: process.workstage_code,
            process_name: process.workstage_name,
            position_x: position?.position_x || 0,
            position_y: position?.position_y || 0,
            width: position?.width || 120,
            height: position?.height || 80,
            z_index: position?.z_index || 1,
            isDragging: false,
            isResizing: false,
            tag_id: position?.tag_id || null,
            tag_address: position?.tag_address || null,
            plc_code: position?.plc_code || null,
            machine_code: position?.machine_code || null,
          };
        });
        
        setBoxes(initialBoxes);
        setLoading(false);
      } catch (error) {
        console.error('위치 정보 조회 실패:', error);
        // 위치 정보가 없으면 기본값으로 생성
        const defaultBoxes: DraggableBox[] = processes.map((process, index) => ({
          process_code: process.workstage_code,
          process_name: process.workstage_name,
          position_x: (index % 5) * 140 + 20,
          position_y: Math.floor(index / 5) * 100 + 20,
          width: 120,
          height: 80,
          z_index: 1,
          isDragging: false,
          isResizing: false,
          tag_id: null,
          tag_address: null,
          plc_code: null,
          machine_code: null,
        }));
        setBoxes(defaultBoxes);
        setLoading(false);
      }
    };

    if (processes.length > 0) {
      fetchPositions();
    }
  }, [processes]);

  // 드래그 시작
  const handleMouseDown = (e: React.MouseEvent, processCode: string) => {
    e.preventDefault();
    const box = boxes.find(b => b.process_code === processCode);
    if (!box || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    dragStartPos.current = {
      x: e.clientX - rect.left - box.position_x,
      y: e.clientY - rect.top - box.position_y,
    };
    dragBoxRef.current = processCode;

    setBoxes(prev => prev.map(b =>
      b.process_code === processCode ? { ...b, isDragging: true } : b
    ));
    setSelectedBox(processCode);
  };

  // 드래그 중
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragBoxRef.current || !dragStartPos.current || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const newX = e.clientX - rect.left - dragStartPos.current.x;
      const newY = e.clientY - rect.top - dragStartPos.current.y;

      setBoxes(prev => prev.map(b =>
        b.process_code === dragBoxRef.current!
          ? {
              ...b,
              position_x: Math.max(0, Math.min(newX, rect.width - b.width)),
              position_y: Math.max(0, Math.min(newY, rect.height - b.height)),
            }
          : b
      ));
    };

    const handleMouseUp = () => {
      if (dragBoxRef.current) {
        setBoxes(prev => prev.map(b =>
          b.process_code === dragBoxRef.current! ? { ...b, isDragging: false } : b
        ));
        dragBoxRef.current = null;
        dragStartPos.current = null;
      }
    };

    if (dragBoxRef.current) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [boxes]);

  // 위치 저장
  const handleSave = async () => {
    setSaving(true);
    try {
      const positions: EquipmentPosition[] = boxes.map(box => ({
        process_code: box.process_code,
        position_x: box.position_x,
        position_y: box.position_y,
        width: box.width,
        height: box.height,
        z_index: box.z_index,
        tag_id: box.tag_id || null,
        tag_address: box.tag_address || null,
        plc_code: box.plc_code || null,
        machine_code: box.machine_code || null,
      }));

      await saveEquipmentPositions({
        layout_name: 'default',
        positions,
      });

      toast.success(`${positions.length}개 설비 위치가 저장되었습니다.`);
    } catch (error) {
      toast.error('위치 저장 실패');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  // 리사이즈 시작
  const handleResizeStart = (e: React.MouseEvent, processCode: string) => {
    e.preventDefault();
    e.stopPropagation();
    const box = boxes.find(b => b.process_code === processCode);
    if (!box || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    resizeStartPos.current = {
      x: e.clientX,
      y: e.clientY,
      width: box.width,
      height: box.height,
    };
    resizeBoxRef.current = processCode;

    setBoxes(prev => prev.map(b =>
      b.process_code === processCode ? { ...b, isResizing: true } : b
    ));
  };

  // 리사이즈 중
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!resizeBoxRef.current || !resizeStartPos.current || !containerRef.current) return;

      const deltaX = e.clientX - resizeStartPos.current.x;
      const deltaY = e.clientY - resizeStartPos.current.y;
      const minWidth = 50;
      const minHeight = 50;

      setBoxes(prev => prev.map(b =>
        b.process_code === resizeBoxRef.current!
          ? {
              ...b,
              width: Math.max(minWidth, resizeStartPos.current!.width + deltaX),
              height: Math.max(minHeight, resizeStartPos.current!.height + deltaY),
            }
          : b
      ));
    };

    const handleMouseUp = () => {
      if (resizeBoxRef.current) {
        setBoxes(prev => prev.map(b =>
          b.process_code === resizeBoxRef.current! ? { ...b, isResizing: false } : b
        ));
        resizeBoxRef.current = null;
        resizeStartPos.current = null;
      }
    };

    if (resizeBoxRef.current) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [boxes]);

  // 태그 할당
  const handleTagAssign = (processCode: string, tagId: string) => {
    if (tagId === 'none') {
      setBoxes(prev => prev.map(b =>
        b.process_code === processCode
          ? { ...b, tag_id: null, tag_address: null, plc_code: null, machine_code: null }
          : b
      ));
      return;
    }

    const tag = tags.find(t => t.tag_id.toString() === tagId);
    if (!tag) return;

    setBoxes(prev => prev.map(b =>
      b.process_code === processCode
        ? {
            ...b,
            tag_id: tag.tag_id,
            tag_address: tag.tag_address,
            plc_code: tag.plc_code || null,
            machine_code: tag.machine_code || null,
          }
        : b
    ));
  };

  // 선택된 박스의 좌표 수정
  const updateSelectedBoxPosition = (field: 'position_x' | 'position_y' | 'width' | 'height', value: number) => {
    if (!selectedBox) return;
    setBoxes(prev => prev.map(b =>
      b.process_code === selectedBox
        ? { ...b, [field]: Math.max(0, value) }
        : b
    ));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl text-gray-300">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">모니터 레이아웃 편집</h1>
          <p className="text-gray-400 mt-2">설비 박스 위치를 드래그하여 조정하거나 좌표를 직접 입력하세요.</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleSave}
            disabled={saving}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? '저장 중...' : '저장'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 좌측: 편집 영역 */}
        <div className="lg:col-span-3">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <div className="mb-4">
              <Label htmlFor="bg-image" className="text-gray-300">배경 이미지 URL</Label>
              <Input
                id="bg-image"
                value={backgroundImageUrl}
                onChange={(e) => setBackgroundImageUrl(e.target.value)}
                className="mt-1 bg-gray-800 border-gray-700"
                placeholder="/equipment-layout.png"
              />
            </div>

            {/* 편집 캔버스 */}
            <div
              ref={containerRef}
              className="relative bg-gray-800 rounded-lg overflow-hidden"
              style={{ minHeight: '600px', position: 'relative' }}
            >
              {/* 배경 이미지 */}
              {backgroundImageUrl && (
                <div
                  className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-30"
                  style={{ backgroundImage: `url('${backgroundImageUrl}')` }}
                />
              )}

              {/* 그리드 가이드 (옵션) */}
              <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: `
                  linear-gradient(to right, gray 1px, transparent 1px),
                  linear-gradient(to bottom, gray 1px, transparent 1px)
                `,
                backgroundSize: '20px 20px',
              }} />

              {/* 설비 박스들 */}
              {boxes.map((box) => (
                <div
                  key={box.process_code}
                  className={`absolute cursor-move border-2 rounded-md p-2 bg-blue-500/70 backdrop-blur-sm transition-all ${
                    selectedBox === box.process_code
                      ? 'border-yellow-400 ring-2 ring-yellow-400/50'
                      : 'border-blue-600 hover:border-blue-400'
                  } ${box.isDragging || box.isResizing ? 'opacity-80' : ''}`}
                  style={{
                    left: `${box.position_x}px`,
                    top: `${box.position_y}px`,
                    width: `${box.width}px`,
                    height: `${box.height}px`,
                    zIndex: box.z_index + (selectedBox === box.process_code ? 100 : 0),
                  }}
                  onMouseDown={(e) => handleMouseDown(e, box.process_code)}
                >
                  <div className="text-xs font-bold text-white text-center line-clamp-2">
                    {box.process_name}
                  </div>
                  <div className="text-xs text-white/80 text-center mt-1">
                    {box.process_code}
                  </div>
                  {box.tag_address && (
                    <div className="text-xs text-yellow-300 text-center mt-1">
                      {box.tag_address}
                    </div>
                  )}
                  {/* 리사이즈 핸들 (우하단 모서리) */}
                  {selectedBox === box.process_code && (
                    <div
                      className="absolute bottom-0 right-0 w-4 h-4 bg-yellow-400 border-2 border-yellow-600 cursor-nwse-resize"
                      style={{
                        transform: 'translate(50%, 50%)',
                      }}
                      onMouseDown={(e) => handleResizeStart(e, box.process_code)}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 우측: 선택된 박스 정보 및 편집 */}
        <div className="lg:col-span-1">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-100 mb-4">위치 편집</h2>
            
            {selectedBox ? (
              <div className="space-y-4">
                {(() => {
                  const box = boxes.find(b => b.process_code === selectedBox);
                  if (!box) return null;
                  
                  return (
                    <>
                      <div>
                        <Label className="text-gray-300">설비명</Label>
                        <div className="text-sm text-gray-400 mt-1">{box.process_name}</div>
                        <div className="text-xs text-gray-500 mt-1">{box.process_code}</div>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <Label htmlFor="pos-x" className="text-gray-300">X 좌표</Label>
                          <Input
                            id="pos-x"
                            type="number"
                            value={Math.round(box.position_x)}
                            onChange={(e) => updateSelectedBoxPosition('position_x', parseInt(e.target.value) || 0)}
                            className="mt-1 bg-gray-800 border-gray-700"
                          />
                        </div>
                        <div>
                          <Label htmlFor="pos-y" className="text-gray-300">Y 좌표</Label>
                          <Input
                            id="pos-y"
                            type="number"
                            value={Math.round(box.position_y)}
                            onChange={(e) => updateSelectedBoxPosition('position_y', parseInt(e.target.value) || 0)}
                            className="mt-1 bg-gray-800 border-gray-700"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <Label htmlFor="width" className="text-gray-300">너비</Label>
                          <Input
                            id="width"
                            type="number"
                            value={Math.round(box.width)}
                            onChange={(e) => updateSelectedBoxPosition('width', parseInt(e.target.value) || 0)}
                            className="mt-1 bg-gray-800 border-gray-700"
                          />
                        </div>
                        <div>
                          <Label htmlFor="height" className="text-gray-300">높이</Label>
                          <Input
                            id="height"
                            type="number"
                            value={Math.round(box.height)}
                            onChange={(e) => updateSelectedBoxPosition('height', parseInt(e.target.value) || 0)}
                            className="mt-1 bg-gray-800 border-gray-700"
                          />
                        </div>
                      </div>

                      {/* 태그 할당 */}
                      <div>
                        <Label htmlFor="tag-select" className="text-gray-300">PLC 태그 할당</Label>
                        <Select
                          value={box.tag_id?.toString() || 'none'}
                          onValueChange={(value) => handleTagAssign(box.process_code, value)}
                        >
                          <SelectTrigger id="tag-select" className="mt-1 bg-gray-800 border-gray-700">
                            <SelectValue placeholder="태그 선택" />
                          </SelectTrigger>
                          <SelectContent className="bg-gray-800 border-gray-700 max-h-60">
                            <SelectItem value="none">태그 없음</SelectItem>
                            {tags.map((tag) => (
                              <SelectItem key={tag.tag_id} value={tag.tag_id.toString()}>
                                {tag.tag_name} ({tag.tag_address})
                                {tag.machine_code && ` - ${tag.machine_code}`}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {box.tag_address && (
                          <div className="mt-2 text-xs text-gray-400">
                            <div>주소: {box.tag_address}</div>
                            {box.plc_code && <div>PLC: {box.plc_code}</div>}
                            {box.machine_code && <div>설비: {box.machine_code}</div>}
                          </div>
                        )}
                      </div>

                      <Button
                        onClick={() => setSelectedBox(null)}
                        variant="outline"
                        className="w-full bg-gray-800 border-gray-700"
                      >
                        선택 해제
                      </Button>
                    </>
                  );
                })()}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-8">
                <Grid3x3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>박스를 클릭하여 선택하세요</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

