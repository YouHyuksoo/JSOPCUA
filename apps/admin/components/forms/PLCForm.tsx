'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { plcSchema, PLCFormData } from '@/lib/validators/plc';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PLC } from '@/lib/types/plc';
import { Process } from '@/lib/types/process';

interface PLCFormProps {
  defaultValues?: PLC;
  processes: Process[];
  onSubmit: (data: PLCFormData) => void;
  onCancel: () => void;
}

export default function PLCForm({ defaultValues, processes, onSubmit, onCancel }: PLCFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<PLCFormData>({
    resolver: zodResolver(plcSchema),
    defaultValues: defaultValues ? {
      name: defaultValues.name,
      code: defaultValues.code,
      ip_address: defaultValues.ip_address,
      port: defaultValues.port,
      protocol: defaultValues.protocol,
      process_id: defaultValues.process_id,
    } : {
      port: 5000,
      protocol: 'MC3E',
    },
  });

  const processId = watch('process_id');
  const protocol = watch('protocol');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="name">PLC 이름</Label>
        <Input id="name" {...register('name')} />
        {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <Label htmlFor="code">PLC 코드</Label>
        <Input id="code" {...register('code')} />
        {errors.code && <p className="text-sm text-red-500 mt-1">{errors.code.message}</p>}
      </div>

      <div>
        <Label htmlFor="ip_address">IP 주소</Label>
        <Input id="ip_address" {...register('ip_address')} placeholder="192.168.1.10" />
        {errors.ip_address && <p className="text-sm text-red-500 mt-1">{errors.ip_address.message}</p>}
      </div>

      <div>
        <Label htmlFor="port">포트</Label>
        <Input id="port" type="number" {...register('port', { valueAsNumber: true })} />
        {errors.port && <p className="text-sm text-red-500 mt-1">{errors.port.message}</p>}
      </div>

      <div>
        <Label htmlFor="protocol">프로토콜</Label>
        <Select
          value={protocol}
          onValueChange={(value) => setValue('protocol', value as 'MC3E' | 'SLMP')}
        >
          <SelectTrigger>
            <SelectValue placeholder="프로토콜 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="MC3E">MC3E</SelectItem>
            <SelectItem value="SLMP">SLMP</SelectItem>
          </SelectContent>
        </Select>
        {errors.protocol && <p className="text-sm text-red-500 mt-1">{errors.protocol.message}</p>}
      </div>

      <div>
        <Label htmlFor="process_id">공정</Label>
        <Select
          value={processId?.toString()}
          onValueChange={(value) => setValue('process_id', parseInt(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="공정 선택" />
          </SelectTrigger>
          <SelectContent>
            {processes.map((process) => (
              <SelectItem key={process.id} value={process.id.toString()}>
                {process.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.process_id && <p className="text-sm text-red-500 mt-1">{errors.process_id.message}</p>}
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
