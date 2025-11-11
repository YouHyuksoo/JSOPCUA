import { z } from 'zod';

// IPv4 정규식 패턴
const ipv4Regex = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$/;

export const plcSchema = z.object({
  name: z.string().min(1, 'PLC 이름은 필수입니다').max(100, 'PLC 이름은 100자 이하여야 합니다'),
  code: z.string().min(1, 'PLC 코드는 필수입니다').max(50, 'PLC 코드는 50자 이하여야 합니다'),
  ip_address: z.string().regex(ipv4Regex, '유효한 IPv4 주소를 입력하세요 (예: 192.168.1.1)'),
  port: z.number().int().min(1, '포트는 1 이상이어야 합니다').max(65535, '포트는 65535 이하여야 합니다'),
  protocol: z.enum(['MC3E', 'SLMP'], { errorMap: () => ({ message: '프로토콜을 선택해주세요' }) }),
  process_id: z.number().int().positive('공정을 선택해주세요'),
});

export type PLCFormData = z.infer<typeof plcSchema>;
