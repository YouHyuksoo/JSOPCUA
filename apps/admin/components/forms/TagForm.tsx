'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { tagSchema, TagFormData } from '@/lib/validators/tag';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tag } from '@/lib/types/tag';
import { PLC } from '@/lib/types/plc';

interface TagFormProps {
  defaultValues?: Tag;
  plcs: PLC[];
  onSubmit: (data: TagFormData) => void;
  onCancel: () => void;
}

export default function TagForm({ defaultValues, plcs, onSubmit, onCancel }: TagFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<TagFormData>({
    resolver: zodResolver(tagSchema),
    defaultValues: defaultValues ? {
      name: defaultValues.tag_name,
      address: defaultValues.tag_address,
      category: defaultValues.tag_category || '',
      data_type: defaultValues.data_type as any,
      plc_id: defaultValues.plc_id,
      machine_code: defaultValues.machine_code,
      description: defaultValues.tag_division,
      enabled: defaultValues.enabled,
    } : {
      data_type: 'WORD',
      enabled: true,
    },
  });

  const plcId = watch('plc_id');
  const dataType = watch('data_type');
  const enabled = watch('enabled');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="name" className="text-gray-300">태그 이름 *</Label>
          <Input
            id="name"
            {...register('name')}
            className="bg-gray-800 border-gray-700 text-white"
            placeholder="예: Temperature_Sensor_1"
          />
          {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>}
        </div>

        <div>
          <Label htmlFor="address" className="text-gray-300">주소 *</Label>
          <Input
            id="address"
            {...register('address')}
            placeholder="D100"
            className="bg-gray-800 border-gray-700 text-white"
          />
          {errors.address && <p className="text-sm text-red-500 mt-1">{errors.address.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="category" className="text-gray-300">태그 타입 (선택)</Label>
          <Input
            id="category"
            {...register('category')}
            placeholder="예: 온도, 압력, 유량 등"
            className="bg-gray-800 border-gray-700 text-white"
          />
          {errors.category && <p className="text-sm text-red-500 mt-1">{errors.category.message}</p>}
        </div>

        <div>
          <Label htmlFor="data_type" className="text-gray-300">데이터 타입 *</Label>
          <Select
            value={dataType}
            onValueChange={(value) => setValue('data_type', value as any)}
          >
            <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
              <SelectValue placeholder="데이터 타입 선택" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 border-gray-700">
              <SelectItem value="INT" className="text-white hover:bg-gray-700">INT</SelectItem>
              <SelectItem value="WORD" className="text-white hover:bg-gray-700">WORD</SelectItem>
              <SelectItem value="DWORD" className="text-white hover:bg-gray-700">DWORD</SelectItem>
              <SelectItem value="FLOAT" className="text-white hover:bg-gray-700">FLOAT</SelectItem>
              <SelectItem value="REAL" className="text-white hover:bg-gray-700">REAL</SelectItem>
              <SelectItem value="BOOL" className="text-white hover:bg-gray-700">BOOL</SelectItem>
              <SelectItem value="STRING" className="text-white hover:bg-gray-700">STRING</SelectItem>
            </SelectContent>
          </Select>
          {errors.data_type && <p className="text-sm text-red-500 mt-1">{errors.data_type.message}</p>}
        </div>
      </div>

      <div>
        <Label htmlFor="plc_id" className="text-gray-300">PLC *</Label>
        <Select
          value={plcId?.toString()}
          onValueChange={(value) => setValue('plc_id', parseInt(value))}
        >
          <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
            <SelectValue placeholder="PLC 선택" />
          </SelectTrigger>
          <SelectContent className="bg-gray-800 border-gray-700">
            {plcs.map((plc) => (
              <SelectItem
                key={plc.id}
                value={plc.id.toString()}
                className="text-white hover:bg-gray-700"
              >
                {plc.plc_name} ({plc.plc_code})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.plc_id && <p className="text-sm text-red-500 mt-1">{errors.plc_id.message}</p>}
      </div>

      <div>
        <Label htmlFor="machine_code" className="text-gray-300">설비 코드 *</Label>
        <Input
          id="machine_code"
          {...register('machine_code')}
          className="bg-gray-800 border-gray-700 text-white"
          placeholder="예: EQ001"
        />
        {errors.machine_code && <p className="text-sm text-red-500 mt-1">{errors.machine_code.message}</p>}
      </div>

      <div>
        <Label htmlFor="description" className="text-gray-300">설명 (선택)</Label>
        <Textarea
          id="description"
          {...register('description')}
          className="bg-gray-800 border-gray-700 text-white"
          placeholder="태그에 대한 추가 설명을 입력하세요"
          rows={3}
        />
        {errors.description && <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>}
      </div>

      <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="space-y-0.5">
          <Label htmlFor="enabled" className="text-gray-300 font-medium">
            태그 상태
          </Label>
          <p className="text-sm text-gray-500">
            태그를 활성화하면 폴링이 시작됩니다
          </p>
        </div>
        <Switch
          id="enabled"
          checked={enabled}
          onCheckedChange={(checked) => setValue('enabled', checked)}
          className="data-[state=checked]:bg-green-600"
        />
      </div>

      <div className="flex gap-2 justify-end pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white"
        >
          취소
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          {isSubmitting ? '저장 중...' : '저장'}
        </Button>
      </div>
    </form>
  );
}
