'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { lineSchema, LineFormData } from '@/lib/validators/line';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Line } from '@/lib/types/line';

interface LineFormProps {
  defaultValues?: Line;
  onSubmit: (data: LineFormData) => void;
  onCancel: () => void;
}

export default function LineForm({ defaultValues, onSubmit, onCancel }: LineFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LineFormData>({
    resolver: zodResolver(lineSchema),
    defaultValues: defaultValues ? {
      name: defaultValues.name,
      code: defaultValues.code,
    } : undefined,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="name">라인 이름</Label>
        <Input id="name" {...register('name')} />
        {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <Label htmlFor="code">라인 코드</Label>
        <Input id="code" {...register('code')} />
        {errors.code && <p className="text-sm text-red-500 mt-1">{errors.code.message}</p>}
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
