import { z } from 'zod';

export const pollingGroupSchema = z.object({
  name: z.string().min(1, '폴링 그룹 이름은 필수입니다').max(100, '폴링 그룹 이름은 100자 이하여야 합니다'),
  polling_interval_ms: z.number().int().min(100, '폴링 주기는 100ms 이상이어야 합니다').max(60000, '폴링 주기는 60000ms 이하여야 합니다'),
  tag_ids: z.array(z.number().int().positive()).min(1, '최소 1개 이상의 태그를 선택해야 합니다'),
});

export type PollingGroupFormData = z.infer<typeof pollingGroupSchema>;
