import { z } from 'zod';

export const processSchema = z.object({
  name: z.string().min(1, '공정 이름은 필수입니다').max(100, '공정 이름은 100자 이하여야 합니다'),
  code: z.string().min(1, '공정 코드는 필수입니다').max(50, '공정 코드는 50자 이하여야 합니다'),
  line_id: z.number().int().positive('라인을 선택해주세요'),
});

export type ProcessFormData = z.infer<typeof processSchema>;
