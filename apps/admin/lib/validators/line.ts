import { z } from 'zod';

export const lineSchema = z.object({
  name: z.string().min(1, '라인 이름은 필수입니다').max(100, '라인 이름은 100자 이하여야 합니다'),
  code: z.string().min(1, '라인 코드는 필수입니다').max(50, '라인 코드는 50자 이하여야 합니다'),
});

export type LineFormData = z.infer<typeof lineSchema>;
