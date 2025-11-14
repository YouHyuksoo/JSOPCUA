'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { processSchema, ProcessFormData } from '@/lib/validators/process';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Process } from '@/lib/types/process';
import { Machine } from '@/lib/types/machine';

interface ProcessFormProps {
  defaultValues?: Process;
  machines: Machine[];
  onSubmit: (data: ProcessFormData) => void;
  onCancel: () => void;
}

export default function ProcessForm({ defaultValues, machines, onSubmit, onCancel }: ProcessFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ProcessFormData>({
    resolver: zodResolver(processSchema),
    defaultValues: defaultValues ? {
      machine_id: defaultValues.machine_id,
      process_sequence: defaultValues.process_sequence,
      process_code: defaultValues.process_code,
      process_name: defaultValues.process_name,
      equipment_type: defaultValues.equipment_type || '',
      enabled: defaultValues.enabled,
    } : {
      machine_id: 0,
      process_sequence: 1,
      process_code: '',
      process_name: '',
      equipment_type: '',
      enabled: true,
    },
  });

  const machineId = watch('machine_id');
  const enabled = watch('enabled');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <Label htmlFor="machine_id" className="text-gray-300">설비 *</Label>
        <Select
          value={machineId?.toString()}
          onValueChange={(value) => setValue('machine_id', parseInt(value))}
        >
          <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
            <SelectValue placeholder="설비 선택" />
          </SelectTrigger>
          <SelectContent className="bg-gray-800 border-gray-700">
            {machines.map((machine) => (
              <SelectItem key={machine.id} value={machine.id.toString()} className="text-gray-100 focus:bg-gray-700">
                {machine.machine_name} ({machine.machine_code})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.machine_id && <p className="text-sm text-red-400 mt-1">{errors.machine_id.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="process_code" className="text-gray-300">공정 코드 * (14자)</Label>
          <Input
            id="process_code"
            {...register('process_code')}
            disabled={!!defaultValues}
            placeholder="MC001-CNC-0001"
            maxLength={14}
            className="bg-gray-800 border-gray-700 text-gray-100 disabled:opacity-50"
          />
          {errors.process_code && <p className="text-sm text-red-400 mt-1">{errors.process_code.message}</p>}
          {defaultValues && <p className="text-sm text-gray-500 mt-1">공정 코드는 수정할 수 없습니다</p>}
        </div>

        <div>
          <Label htmlFor="process_sequence" className="text-gray-300">공정 순서 *</Label>
          <Input
            id="process_sequence"
            type="number"
            {...register('process_sequence', { valueAsNumber: true })}
            placeholder="1"
            className="bg-gray-800 border-gray-700 text-gray-100"
          />
          {errors.process_sequence && <p className="text-sm text-red-400 mt-1">{errors.process_sequence.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="process_name" className="text-gray-300">공정 이름 *</Label>
          <Input
            id="process_name"
            {...register('process_name')}
            placeholder="CNC 가공"
            className="bg-gray-800 border-gray-700 text-gray-100"
          />
          {errors.process_name && <p className="text-sm text-red-400 mt-1">{errors.process_name.message}</p>}
        </div>

        <div>
          <Label htmlFor="equipment_type" className="text-gray-300">설비 타입</Label>
          <Input
            id="equipment_type"
            {...register('equipment_type')}
            placeholder="CNC"
            className="bg-gray-800 border-gray-700 text-gray-100"
          />
          {errors.equipment_type && <p className="text-sm text-red-400 mt-1">{errors.equipment_type.message}</p>}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="enabled"
          checked={enabled}
          onCheckedChange={(checked) => setValue('enabled', checked as boolean)}
          className="bg-gray-800 border-gray-700"
        />
        <Label htmlFor="enabled" className="text-gray-300 cursor-pointer">활성화</Label>
      </div>

      <div className="flex gap-2 justify-end pt-4">
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
          disabled={isSubmitting}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          {isSubmitting ? '저장 중...' : '저장'}
        </Button>
      </div>
    </form>
  );
}
