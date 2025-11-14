import { z } from 'zod';

export const processSchema = z.object({
  machine_id: z.number().int().positive('설비를 선택해주세요'),
  process_sequence: z.number().int().positive('공정 순서는 필수입니다'),
  process_code: z.string().min(14, '공정 코드는 14자여야 합니다').max(14, '공정 코드는 14자여야 합니다'),
  process_name: z.string().min(1, '공정 이름은 필수입니다').max(200, '공정 이름은 200자 이하여야 합니다'),
  enabled: z.boolean(),
  equipment_type: z.string().max(100, '설비 타입은 100자 이하여야 합니다').optional(),
});

export type ProcessFormData = z.infer<typeof processSchema>;
