import { z } from 'zod';

export const tagSchema = z.object({
  name: z.string().min(1, '태그 이름은 필수입니다').max(100, '태그 이름은 100자 이하여야 합니다'),
  address: z.string().min(1, '주소는 필수입니다').max(50, '주소는 50자 이하여야 합니다'),
  category: z.string().max(50, '태그 타입은 50자 이하여야 합니다').optional(),
  data_type: z.enum(['INT', 'FLOAT', 'BOOL', 'STRING', 'WORD', 'DWORD', 'REAL']),
  plc_id: z.number().int().positive('PLC를 선택해주세요'),
  description: z.string().max(255, '설명은 255자 이하여야 합니다').optional(),
  enabled: z.boolean().default(true),
});

export type TagFormData = z.infer<typeof tagSchema>;
