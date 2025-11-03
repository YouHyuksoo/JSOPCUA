'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { processSchema, ProcessFormData } from '@/lib/validators/process';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Process } from '@/lib/types/process';
import { Line } from '@/lib/types/line';

interface ProcessFormProps {
  defaultValues?: Process;
  lines: Line[];
  onSubmit: (data: ProcessFormData) => void;
  onCancel: () => void;
}

export default function ProcessForm({ defaultValues, lines, onSubmit, onCancel }: ProcessFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ProcessFormData>({
    resolver: zodResolver(processSchema),
    defaultValues: defaultValues ? {
      name: defaultValues.name,
      code: defaultValues.code,
      line_id: defaultValues.line_id,
    } : undefined,
  });

  const lineId = watch('line_id');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="name">공정 이름</Label>
        <Input id="name" {...register('name')} />
        {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <Label htmlFor="code">공정 코드</Label>
        <Input id="code" {...register('code')} />
        {errors.code && <p className="text-sm text-red-500 mt-1">{errors.code.message}</p>}
      </div>

      <div>
        <Label htmlFor="line_id">라인</Label>
        <Select
          value={lineId?.toString()}
          onValueChange={(value) => setValue('line_id', parseInt(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="라인 선택" />
          </SelectTrigger>
          <SelectContent>
            {lines.map((line) => (
              <SelectItem key={line.id} value={line.id.toString()}>
                {line.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.line_id && <p className="text-sm text-red-500 mt-1">{errors.line_id.message}</p>}
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
