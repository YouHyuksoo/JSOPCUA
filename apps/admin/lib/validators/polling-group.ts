/**
 * @file apps/admin/lib/validators/polling-group.ts
 * @description
 * 폴링 그룹 폼 데이터 유효성 검사를 위한 Zod 스키마 정의
 *
 * 초보자 가이드:
 * 1. **pollingGroupSchema**: 폴링 그룹 생성/수정 시 입력 데이터 검증
 * 2. **PollingGroupFormData**: 폼 데이터 타입 (스키마에서 자동 추론)
 */
import { z } from 'zod';

/** 동작구분 enum 타입 */
export const GROUP_CATEGORY = ['ALARM', 'OPERATION', 'STATE'] as const;
export type GroupCategory = typeof GROUP_CATEGORY[number];

/**
 * 폴링 그룹 폼 유효성 검사 스키마
 * - name: 필수, 1~100자
 * - description: 선택
 * - polling_interval_ms: 필수, 100~60000ms
 * - group_category: 필수, ALARM/OPERATION/STATE 중 하나
 * - tag_ids: 필수, 최소 1개 이상의 태그 ID 배열
 */
export const pollingGroupSchema = z.object({
  name: z.string().min(1, '폴링 그룹 이름은 필수입니다').max(100, '폴링 그룹 이름은 100자 이하여야 합니다'),
  description: z.string().optional(),
  polling_interval_ms: z.number().int().min(100, '폴링 주기는 100ms 이상이어야 합니다').max(60000, '폴링 주기는 60000ms 이하여야 합니다'),
  /** 동작구분: ALARM(알람/상태), OPERATION(동작), STATE(상태) */
  group_category: z.enum(GROUP_CATEGORY, {
    message: '동작구분은 ALARM, OPERATION, STATE 중 하나여야 합니다'
  }),
  tag_ids: z.array(z.number().int().positive()).min(1, '최소 1개 이상의 태그를 선택해야 합니다'),
});

/** 폴링 그룹 폼 데이터 타입 (스키마에서 추론) */
export type PollingGroupFormData = z.infer<typeof pollingGroupSchema>;
