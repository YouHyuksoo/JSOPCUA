'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { pollingGroupSchema, PollingGroupFormData, GroupCategory } from '@/lib/validators/polling-group';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PollingGroup } from '@/lib/types/polling-group';
import { Tag } from '@/lib/types/tag';
import { useState, useMemo, useEffect } from 'react';
import { Search, X, Filter, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import TablePagination from '@/components/TablePagination';

interface PollingGroupFormProps {
  defaultValues?: PollingGroup;
  tags: Tag[];
  initialTagIds?: number[];
  onSubmit: (data: PollingGroupFormData) => void;
  onCancel: () => void;
}

export default function PollingGroupForm({ defaultValues, tags, initialTagIds = [], onSubmit, onCancel }: PollingGroupFormProps) {
  const [selectedTags, setSelectedTags] = useState<number[]>(initialTagIds);
  const [searchQuery, setSearchQuery] = useState('');
  const [dataTypeFilter, setDataTypeFilter] = useState<string>('all');
  const [plcFilter, setPlcFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<PollingGroupFormData>({
    resolver: zodResolver(pollingGroupSchema),
    defaultValues: defaultValues ? {
      name: defaultValues.name,
      description: defaultValues.description || '',
      polling_interval_ms: defaultValues.polling_interval,
      group_category: (defaultValues.group_category || 'OPERATION') as GroupCategory,
      tag_ids: initialTagIds,
    } : {
      name: '',
      polling_interval_ms: 1000,
      group_category: 'OPERATION' as GroupCategory,
      tag_ids: [],
    },
  });

  // 고유한 데이터 타입 및 PLC 코드 추출
  const dataTypes = useMemo(() => {
    const types = new Set(tags.map(tag => tag.data_type));
    return Array.from(types).sort();
  }, [tags]);

  const plcCodes = useMemo(() => {
    const codes = new Set(tags.map(tag => tag.plc_code).filter(Boolean));
    return Array.from(codes).sort();
  }, [tags]);

  // 필터링된 태그 목록
  const filteredTags = useMemo(() => {
    return tags.filter(tag => {
      // 검색어 필터
      const matchesSearch = searchQuery === '' ||
        tag.tag_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tag.tag_address.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (tag.tag_division && tag.tag_division.toLowerCase().includes(searchQuery.toLowerCase()));

      // 데이터 타입 필터
      const matchesDataType = dataTypeFilter === 'all' || tag.data_type === dataTypeFilter;

      // PLC 필터
      const matchesPLC = plcFilter === 'all' || tag.plc_code === plcFilter;

      return matchesSearch && matchesDataType && matchesPLC;
    });
  }, [tags, searchQuery, dataTypeFilter, plcFilter]);

  // 페이지네이션 계산
  const totalPages = Math.ceil(filteredTags.length / itemsPerPage);
  const paginatedTags = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredTags.slice(startIndex, endIndex);
  }, [filteredTags, currentPage, itemsPerPage]);

  // 필터 변경 시 첫 페이지로 리셋
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, dataTypeFilter, plcFilter]);

  // 초기 태그 ID 업데이트
  useEffect(() => {
    if (initialTagIds.length > 0) {
      setSelectedTags(initialTagIds);
      setValue('tag_ids', initialTagIds);
    }
  }, [initialTagIds, setValue]);

  // selectedTags 변경 시 form 값 업데이트
  useEffect(() => {
    setValue('tag_ids', selectedTags);
  }, [selectedTags, setValue]);

  const handleTagToggle = (tagId: number) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  };

  const handleSelectAll = () => {
    const allFilteredIds = filteredTags.map(tag => tag.id);
    setSelectedTags(allFilteredIds);
  };

  const handleDeselectAll = () => {
    setSelectedTags([]);
  };

  const handleRemoveTag = (tagId: number) => {
    setSelectedTags(prev => prev.filter(id => id !== tagId));
  };

  const handleFormSubmit = (data: PollingGroupFormData) => {
    console.log('Form submitted with data:', data);
    onSubmit(data);
  };

  const selectedTagsData = useMemo(() => {
    return tags.filter(tag => selectedTags.includes(tag.id));
  }, [tags, selectedTags]);

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* 상단 버튼 영역 */}
      <div className="flex gap-2 justify-end pb-4 border-b border-gray-700">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          className="bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
        >
          취소
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting || selectedTags.length === 0}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          {isSubmitting ? '저장 중...' : '저장'}
        </Button>
      </div>

      {/* 2단 레이아웃 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 기본 정보 + 선택된 태그 */}
        <div className="lg:col-span-1 space-y-4">
          {/* 기본 정보 카드 */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white text-lg">기본 정보</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <Label htmlFor="name" className="text-gray-300 text-sm">폴링 그룹 이름</Label>
                  <Input
                    id="name"
                    {...register('name')}
                    className="bg-gray-800 border-gray-700 text-white mt-1.5"
                    placeholder="라인1_실시간그룹"
                  />
                  {errors.name && <p className="text-xs text-red-400 mt-1">{errors.name.message}</p>}
                </div>

                <div>
                  <Label htmlFor="description" className="text-gray-300 text-sm">설명 (선택)</Label>
                  <Input
                    id="description"
                    {...register('description')}
                    className="bg-gray-800 border-gray-700 text-white mt-1.5"
                    placeholder="폴링 그룹에 대한 설명을 입력하세요"
                  />
                  {errors.description && <p className="text-xs text-red-400 mt-1">{errors.description.message}</p>}
                </div>

                <div>
                  <Label htmlFor="polling_interval_ms" className="text-gray-300 text-sm">폴링 주기 (ms)</Label>
                  <Input
                    id="polling_interval_ms"
                    type="number"
                    {...register('polling_interval_ms', { valueAsNumber: true })}
                    className="bg-gray-800 border-gray-700 text-white mt-1.5"
                    placeholder="1000"
                  />
                  {errors.polling_interval_ms && (
                    <p className="text-xs text-red-400 mt-1">{errors.polling_interval_ms.message}</p>
                  )}
                </div>

                {/* 동작구분 (group_category) */}
                <div>
                  <Label htmlFor="group_category" className="text-gray-300 text-sm">동작구분</Label>
                  <select
                    id="group_category"
                    {...register('group_category')}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white text-sm mt-1.5 focus:outline-none focus:border-blue-500"
                  >
                    <option value="OPERATION">OPERATION (동작)</option>
                    <option value="STATE">STATE (상태)</option>
                    <option value="ALARM">ALARM (알람)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    선택한 동작구분에 따라 데이터가 저장되는 Oracle 테이블이 결정됩니다
                  </p>
                  {errors.group_category && (
                    <p className="text-xs text-red-400 mt-1">{errors.group_category.message}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 선택된 태그 카드 */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-lg">선택된 태그</CardTitle>
                <Badge variant="secondary" className="bg-blue-600 text-white">
                  {selectedTags.length}개
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {selectedTags.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <span className="text-4xl mb-2 block">📋</span>
                  <p className="text-sm">선택된 태그가 없습니다</p>
                  <p className="text-xs text-red-400 mt-2">⚠️ 최소 1개 이상 선택 필요</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {selectedTagsData.map(tag => (
                    <div
                      key={tag.id}
                      className="flex items-center justify-between bg-gray-800 border border-gray-700 rounded p-2 hover:bg-gray-750 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-white truncate">{tag.tag_name}</span>
                          <Badge variant="outline" className="text-xs border-gray-600 text-gray-300 shrink-0">
                            {tag.tag_address}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                          <span>{tag.data_type}</span>
                          <span>•</span>
                          <span>{tag.plc_code || 'N/A'}</span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag.id)}
                        className="text-gray-400 hover:text-red-400 ml-2 shrink-0"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* 오른쪽: 태그 선택 */}
        <div className="lg:col-span-2">
          <Card className="bg-gray-900 border-gray-800 h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-lg">태그 선택</CardTitle>
                <span className="text-sm text-gray-400">
                  전체 {filteredTags.length}개
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 검색 및 필터 */}
              <div className="space-y-3">
                {/* 검색바 */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="태그명, 주소, 그룹으로 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 bg-gray-800 border-gray-700 text-white"
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      onClick={() => setSearchQuery('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>

                {/* 필터 */}
                <div className="flex gap-3">
                  <div className="flex-1">
                    <select
                      value={dataTypeFilter}
                      onChange={(e) => setDataTypeFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white text-sm"
                    >
                      <option value="all">모든 데이터 타입</option>
                      {dataTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex-1">
                    <select
                      value={plcFilter}
                      onChange={(e) => setPlcFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white text-sm"
                    >
                      <option value="all">모든 PLC</option>
                      {plcCodes.map(code => (
                        <option key={code} value={code}>{code}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* 일괄 선택 버튼 */}
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleSelectAll}
                    className="bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
                  >
                    <CheckCircle2 className="h-4 w-4 mr-1" />
                    전체 선택
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleDeselectAll}
                    className="bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
                  >
                    선택 해제
                  </Button>
                </div>
              </div>

              {/* 태그 목록 */}
              <div className="border border-gray-700 rounded-md bg-gray-800">
                {filteredTags.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Filter className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>검색 결과가 없습니다</p>
                  </div>
                ) : (
                  <>
                    {/* 테이블 헤더 */}
                    <div className="grid grid-cols-12 gap-2 px-4 py-3 bg-gray-800 border-b border-gray-700 text-sm font-medium text-gray-400">
                      <div className="col-span-1"></div>
                      <div className="col-span-3">태그명</div>
                      <div className="col-span-2">주소</div>
                      <div className="col-span-2">설비 코드</div>
                      <div className="col-span-1">타입</div>
                      <div className="col-span-2">PLC</div>
                      <div className="col-span-1">그룹</div>
                    </div>

                    {/* 태그 목록 */}
                    <div className="divide-y divide-gray-700">
                      {paginatedTags.map((tag) => (
                        <div
                          key={tag.id}
                          className={`grid grid-cols-12 gap-2 px-4 py-3 hover:bg-gray-750 transition-colors ${
                            selectedTags.includes(tag.id) ? 'bg-gray-750' : ''
                          }`}
                        >
                          <div className="col-span-1 flex items-center">
                            <Checkbox
                              id={`tag-${tag.id}`}
                              checked={selectedTags.includes(tag.id)}
                              onCheckedChange={() => handleTagToggle(tag.id)}
                            />
                          </div>
                          <label
                            htmlFor={`tag-${tag.id}`}
                            className="col-span-11 grid grid-cols-11 gap-2 cursor-pointer items-center"
                          >
                            <div className="col-span-3">
                              <span className="font-medium text-white text-sm truncate block">{tag.tag_name}</span>
                            </div>
                            <div className="col-span-2">
                              <Badge variant="outline" className="text-xs border-gray-600 text-gray-300">
                                {tag.tag_address}
                              </Badge>
                            </div>
                            <div className="col-span-2">
                              <span className="text-sm text-gray-300 truncate block">{tag.machine_code || '-'}</span>
                            </div>
                            <div className="col-span-1">
                              <span className="text-xs text-gray-300">{tag.data_type}</span>
                            </div>
                            <div className="col-span-2">
                              <span className="text-sm text-gray-300 truncate block">{tag.plc_code || '-'}</span>
                            </div>
                            <div className="col-span-1">
                              <span className="text-xs text-gray-400 truncate block" title={tag.tag_division || '-'}>
                                {tag.tag_division || '-'}
                              </span>
                            </div>
                          </label>
                        </div>
                      ))}
                    </div>

                    {/* 페이지네이션 */}
                    <TablePagination
                      currentPage={currentPage}
                      totalPages={totalPages}
                      totalItems={filteredTags.length}
                      itemsPerPage={itemsPerPage}
                      onPageChange={setCurrentPage}
                    />
                  </>
                )}
              </div>

              {selectedTags.length === 0 && (
                <p className="text-sm text-red-400 flex items-center gap-1">
                  <span>⚠️</span>
                  최소 1개 이상의 태그를 선택해야 합니다
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </form>
  );
}
