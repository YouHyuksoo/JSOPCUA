export interface PLC {
  id: number;
  plc_code: string;
  plc_name: string;
  plc_spec?: string;
  plc_type?: string;
  ip_address: string;
  port: number;
  protocol: string;
  network_no: number;
  station_no: number;
  connection_timeout: number;
  is_active: boolean;
  // MELSEC 설정
  driver_version?: string;
  message_format?: string;
  series?: string;
  // SSL/TLS 설정
  ssl_root_cert?: string;
  ssl_version?: string;
  ssl_password?: string;
  ssl_private_key?: string;
  ssl_certificate?: string;
  // 네트워크 설정
  local_address?: string;
  network_type?: string;
  // 소켓 설정
  keep_alive?: boolean;
  linger_time?: number;
  // 일반 설정
  description?: string;
  scan_time?: number;
  // 장치 설정
  charset?: string;
  text_endian?: string;
  // 장치 블락 설정
  unit_size?: string;
  block_size?: number;
  created_at: string;
  updated_at: string;
}

export interface CreatePLCRequest {
  plc_code: string;
  plc_name: string;
  plc_spec?: string;
  plc_type?: string;
  ip_address: string;
  port: number;
  protocol?: string;
  network_no?: number;
  station_no?: number;
  connection_timeout?: number;
  is_active?: boolean;
  // MELSEC 설정
  driver_version?: string;
  message_format?: string;
  series?: string;
  // SSL/TLS 설정
  ssl_root_cert?: string;
  ssl_version?: string;
  ssl_password?: string;
  ssl_private_key?: string;
  ssl_certificate?: string;
  // 네트워크 설정
  local_address?: string;
  network_type?: string;
  // 소켓 설정
  keep_alive?: boolean;
  linger_time?: number;
  // 일반 설정
  description?: string;
  scan_time?: number;
  // 장치 설정
  charset?: string;
  text_endian?: string;
  // 장치 블락 설정
  unit_size?: string;
  block_size?: number;
}

export interface PLCTestResponse {
  status: string;
  response_time_ms?: number | null;
  test_value_d100?: number | null;
  test_value_w100?: number | null;
  test_value_m100?: number | null;
  error?: string | null;
}
