'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { tagSchema, TagFormData } from '@/lib/validators/tag';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
      name: defaultValues.name,
      address: defaultValues.address,
      data_type: defaultValues.data_type,
      plc_id: defaultValues.plc_id,
      description: defaultValues.description,
    } : {
      data_type: 'INT',
    },
  });

  const plcId = watch('plc_id');
  const dataType = watch('data_type');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="name">태그 이름</Label>
        <Input id="name" {...register('name')} />
        {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <Label htmlFor="address">주소</Label>
        <Input id="address" {...register('address')} placeholder="D100" />
        {errors.address && <p className="text-sm text-red-500 mt-1">{errors.address.message}</p>}
      </div>

      <div>
        <Label htmlFor="data_type">데이터 타입</Label>
        <Select
          value={dataType}
          onValueChange={(value) => setValue('data_type', value as 'INT' | 'FLOAT' | 'BOOL' | 'STRING')}
        >
          <SelectTrigger>
            <SelectValue placeholder="데이터 타입 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="INT">INT</SelectItem>
            <SelectItem value="FLOAT">FLOAT</SelectItem>
            <SelectItem value="BOOL">BOOL</SelectItem>
            <SelectItem value="STRING">STRING</SelectItem>
          </SelectContent>
        </Select>
        {errors.data_type && <p className="text-sm text-red-500 mt-1">{errors.data_type.message}</p>}
      </div>

      <div>
        <Label htmlFor="plc_id">PLC</Label>
        <Select
          value={plcId?.toString()}
          onValueChange={(value) => setValue('plc_id', parseInt(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="PLC 선택" />
          </SelectTrigger>
          <SelectContent>
            {plcs.map((plc) => (
              <SelectItem key={plc.id} value={plc.id.toString()}>
                {plc.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.plc_id && <p className="text-sm text-red-500 mt-1">{errors.plc_id.message}</p>}
      </div>

      <div>
        <Label htmlFor="description">설명 (선택)</Label>
        <Textarea id="description" {...register('description')} />
        {errors.description && <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>}
      </div>

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? '저장 중...' : '저장'}
        </Button>
      </div>
    </form>
  );
}
