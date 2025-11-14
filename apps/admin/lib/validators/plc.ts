import { z } from 'zod';

// IPv4 정규식 패턴
const ipv4Regex = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$/;

export const plcSchema = z.object({
  plc_code: z.string().min(1, 'PLC 코드는 필수입니다').max(50, 'PLC 코드는 50자 이하여야 합니다'),
  plc_name: z.string().min(1, 'PLC 이름은 필수입니다').max(100, 'PLC 이름은 100자 이하여야 합니다'),
  ip_address: z.string().regex(ipv4Regex, '유효한 IPv4 주소를 입력하세요 (예: 192.168.1.1)'),
  port: z.number().int().min(1, '포트는 1 이상이어야 합니다').max(65535, '포트는 65535 이하여야 합니다'),
  protocol: z.string(),
  network_no: z.number().int().min(0, '네트워크 번호는 0 이상이어야 합니다'),
  station_no: z.number().int().min(0, '국번은 0 이상이어야 합니다'),
  connection_timeout: z.number().int().min(1, '타임아웃은 1초 이상이어야 합니다'),
  is_active: z.boolean(),
  plc_spec: z.string().max(200, 'PLC SPEC은 200자 이하여야 합니다').optional(),
  plc_type: z.string().max(20, 'PLC 타입은 20자 이하여야 합니다').optional(),
  // MELSEC 설정
  driver_version: z.string().max(10).optional(),
  message_format: z.string().max(20).optional(),
  series: z.string().max(50).optional(),
  // SSL/TLS 설정
  ssl_root_cert: z.string().optional(),
  ssl_version: z.string().max(20).optional(),
  ssl_password: z.string().max(200).optional(),
  ssl_private_key: z.string().optional(),
  ssl_certificate: z.string().optional(),
  // 네트워크 설정
  local_address: z.string().max(50).optional(),
  network_type: z.string().max(10).optional(),
  // 소켓 설정
  keep_alive: z.boolean().optional(),
  linger_time: z.number().int().optional(),
  // 일반 설정
  description: z.string().optional(),
  scan_time: z.number().int().min(1).optional(),
  // 장치 설정
  charset: z.string().max(20).optional(),
  text_endian: z.string().max(20).optional(),
  // 장치 블락 설정
  unit_size: z.string().max(20).optional(),
  block_size: z.number().int().min(1).optional(),
});

export type PLCFormData = z.infer<typeof plcSchema>;
