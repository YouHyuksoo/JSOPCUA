import { z } from 'zod';

export const machineSchema = z.object({
  machine_code: z.string().min(1, '설비 코드는 필수입니다').max(50, '설비 코드는 50자 이하여야 합니다'),
  machine_name: z.string().min(1, '설비 이름은 필수입니다').max(200, '설비 이름은 200자 이하여야 합니다'),
  enabled: z.boolean(),
  location: z.string().max(100, '위치는 100자 이하여야 합니다').optional(),
});

export type MachineFormData = z.infer<typeof machineSchema>;
