'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { machineSchema, MachineFormData } from '@/lib/validators/machine';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Machine } from '@/lib/types/machine';

interface MachineFormProps {
  defaultValues?: Machine;
  onSubmit: (data: MachineFormData) => void;
  onCancel: () => void;
}

export default function MachineForm({ defaultValues, onSubmit, onCancel }: MachineFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<MachineFormData>({
    resolver: zodResolver(machineSchema),
    defaultValues: defaultValues ? {
      machine_code: defaultValues.machine_code,
      machine_name: defaultValues.machine_name,
      location: defaultValues.location || '',
      enabled: defaultValues.enabled,
    } : {
      machine_code: '',
      machine_name: '',
      location: '',
      enabled: true,
    },
  });

  const enabled = watch('enabled');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="machine_code">설비 코드 *</Label>
        <Input
          id="machine_code"
          {...register('machine_code')}
          disabled={!!defaultValues}
          placeholder="예: MC001"
        />
        {errors.machine_code && <p className="text-sm text-red-500 mt-1">{errors.machine_code.message}</p>}
        {defaultValues && <p className="text-sm text-gray-500 mt-1">설비 코드는 수정할 수 없습니다</p>}
      </div>

      <div>
        <Label htmlFor="machine_name">설비 이름 *</Label>
        <Input
          id="machine_name"
          {...register('machine_name')}
          placeholder="예: CNC 가공기 1호"
        />
        {errors.machine_name && <p className="text-sm text-red-500 mt-1">{errors.machine_name.message}</p>}
      </div>

      <div>
        <Label htmlFor="location">위치</Label>
        <Input
          id="location"
          {...register('location')}
          placeholder="예: A동 1층"
        />
        {errors.location && <p className="text-sm text-red-500 mt-1">{errors.location.message}</p>}
      </div>

      <div className="flex items-center space-x-2">
        <Checkbox
          id="enabled"
          checked={enabled}
          onCheckedChange={(checked) => setValue('enabled', checked as boolean)}
        />
        <Label htmlFor="enabled" className="cursor-pointer">활성화</Label>
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
