'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { plcSchema, PLCFormData } from '@/lib/validators/plc';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PLC } from '@/lib/types/plc';

interface PLCFormProps {
  defaultValues?: PLC;
  onSubmit: (data: PLCFormData) => void;
  onCancel: () => void;
}

export default function PLCForm({ defaultValues, onSubmit, onCancel }: PLCFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<PLCFormData>({
    resolver: zodResolver(plcSchema),
    defaultValues: defaultValues ? {
      plc_code: defaultValues.plc_code,
      plc_name: defaultValues.plc_name,
      plc_spec: defaultValues.plc_spec || '',
      plc_type: defaultValues.plc_type || '',
      ip_address: defaultValues.ip_address,
      port: defaultValues.port,
      protocol: defaultValues.protocol,
      network_no: defaultValues.network_no,
      station_no: defaultValues.station_no,
      connection_timeout: defaultValues.connection_timeout,
      is_active: defaultValues.is_active,
      driver_version: defaultValues.driver_version || 'V2',
      message_format: defaultValues.message_format || 'Binary',
      series: defaultValues.series || 'Q Series',
      ssl_version: defaultValues.ssl_version || 'None',
      local_address: defaultValues.local_address || '',
      network_type: defaultValues.network_type || 'tcp',
      keep_alive: defaultValues.keep_alive || false,
      linger_time: defaultValues.linger_time ?? -1,
      description: defaultValues.description || '',
      scan_time: defaultValues.scan_time || 1000,
      charset: defaultValues.charset || 'UTF8',
      text_endian: defaultValues.text_endian || 'None',
      unit_size: defaultValues.unit_size || '16Bit',
      block_size: defaultValues.block_size || 64,
    } : {
      port: 5010,
      protocol: 'MC_3E_ASCII',
      network_no: 0,
      station_no: 0,
      connection_timeout: 5,
      is_active: true,
      driver_version: 'V2',
      message_format: 'Binary',
      series: 'Q Series',
      ssl_version: 'None',
      network_type: 'tcp',
      keep_alive: false,
      linger_time: -1,
      scan_time: 1000,
      charset: 'UTF8',
      text_endian: 'None',
      unit_size: '16Bit',
      block_size: 64,
    },
  });

  const protocol = watch('protocol');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-4 gap-4">
        <div>
          <Label htmlFor="plc_code" className="text-gray-300">PLC 코드</Label>
          <Input
            id="plc_code"
            {...register('plc_code')}
            className="bg-gray-800 border-gray-700 text-gray-100"
            placeholder="PLC01"
          />
          {errors.plc_code && <p className="text-sm text-red-400 mt-1">{errors.plc_code.message}</p>}
        </div>
        <div>
          <Label htmlFor="plc_spec" className="text-gray-300">PLC SPEC (선택)</Label>
          <Input
            id="plc_spec"
            {...register('plc_spec')}
            className="bg-gray-800 border-gray-700 text-gray-100"
            placeholder="Q03UDE"
          />
          {errors.plc_spec && <p className="text-sm text-red-400 mt-1">{errors.plc_spec.message}</p>}
        </div>
        <div>
          <Label htmlFor="plc_type" className="text-gray-300">PLC 타입 (선택)</Label>
          <Input
            id="plc_type"
            {...register('plc_type')}
            className="bg-gray-800 border-gray-700 text-gray-100"
            placeholder="MELSEC Q"
          />
          {errors.plc_type && <p className="text-sm text-red-400 mt-1">{errors.plc_type.message}</p>}
        </div>
        <div className="flex items-end">
          <div className="flex items-center gap-2 w-full">
            <input
              id="is_active"
              type="checkbox"
              {...register('is_active')}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
            />
            <Label htmlFor="is_active" className="text-gray-300">활성화</Label>
          </div>
        </div>
      </div>

      {/* MELSEC 설정 섹션 */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-3">MELSEC 설정</h3>
        <div className="grid grid-cols-5 gap-4">
          <div>
            <Label htmlFor="driver_version" className="text-gray-300">Driver Version</Label>
            <Input
              id="driver_version"
              {...register('driver_version')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="V2"
            />
          </div>
          <div>
            <Label htmlFor="message_format" className="text-gray-300">Message Format</Label>
            <Select
              value={watch('message_format') || 'Binary'}
              onValueChange={(value) => setValue('message_format', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="Binary">Binary</SelectItem>
                <SelectItem value="ASCII">ASCII</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="network_no" className="text-gray-300">NetworkNo</Label>
            <Input
              id="network_no"
              type="number"
              {...register('network_no', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
            />
            {errors.network_no && <p className="text-sm text-red-400 mt-1">{errors.network_no.message}</p>}
          </div>
          <div>
            <Label htmlFor="series" className="text-gray-300">Series</Label>
            <Select
              value={watch('series') || 'Q Series'}
              onValueChange={(value) => setValue('series', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="L Series">L Series</SelectItem>
                <SelectItem value="Q Series">Q Series</SelectItem>
                <SelectItem value="iQ-F Series">iQ-F Series</SelectItem>
                <SelectItem value="iQ-R Series">iQ-R Series</SelectItem>
                <SelectItem value="None">None</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="station_no" className="text-gray-300">StationNo</Label>
            <Input
              id="station_no"
              type="number"
              {...register('station_no', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
            />
            {errors.station_no && <p className="text-sm text-red-400 mt-1">{errors.station_no.message}</p>}
          </div>
        </div>
      </div>

      {/* 네트워크 설정 섹션 */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-3">네트워크 설정</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <Label htmlFor="local_address" className="text-gray-300">로컬 주소</Label>
            <Input
              id="local_address"
              {...register('local_address')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="0.0.0.0"
            />
          </div>
          <div>
            <Label htmlFor="ip_address" className="text-gray-300">원격지 주소</Label>
            <Input
              id="ip_address"
              {...register('ip_address')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="192.168.1.10"
            />
            {errors.ip_address && <p className="text-sm text-red-400 mt-1">{errors.ip_address.message}</p>}
          </div>
          <div>
            <Label htmlFor="port" className="text-gray-300">원격지 포트</Label>
            <Input
              id="port"
              type="number"
              {...register('port', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
            />
            {errors.port && <p className="text-sm text-red-400 mt-1">{errors.port.message}</p>}
          </div>
          <div>
            <Label htmlFor="network_type" className="text-gray-300">종류</Label>
            <Select
              value={watch('network_type') || 'tcp'}
              onValueChange={(value) => setValue('network_type', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="tcp">TCP</SelectItem>
                <SelectItem value="udp">UDP</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* 소켓 설정 섹션 */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-3">소켓 설정</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <input
              id="keep_alive"
              type="checkbox"
              {...register('keep_alive')}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500"
            />
            <Label htmlFor="keep_alive" className="text-gray-300">KeepAlive</Label>
          </div>
          <div>
            <Label htmlFor="linger_time" className="text-gray-300">LingerTime</Label>
            <Input
              id="linger_time"
              type="number"
              {...register('linger_time', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="-1"
            />
          </div>
        </div>
      </div>

      {/* 일반 설정 섹션 */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-3">일반 설정</h3>
        <div className="grid grid-cols-5 gap-4">
          <div>
            <Label htmlFor="description" className="text-gray-300">설명</Label>
            <Input
              id="description"
              {...register('description')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="설명 입력"
            />
          </div>
          <div>
            <Label htmlFor="scan_time" className="text-gray-300">스캔 시간 (ms)</Label>
            <Input
              id="scan_time"
              type="number"
              {...register('scan_time', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="1000"
            />
          </div>
          <div>
            <Label htmlFor="plc_name" className="text-gray-300">이름</Label>
            <Input
              id="plc_name"
              {...register('plc_name')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="메인 PLC"
            />
            {errors.plc_name && <p className="text-sm text-red-400 mt-1">{errors.plc_name.message}</p>}
          </div>
          <div>
            <Label htmlFor="connection_timeout" className="text-gray-300">타임 아웃 (ms)</Label>
            <Input
              id="connection_timeout"
              type="number"
              {...register('connection_timeout', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="10000"
            />
            {errors.connection_timeout && <p className="text-sm text-red-400 mt-1">{errors.connection_timeout.message}</p>}
          </div>
          <div>
            <Label htmlFor="protocol" className="text-gray-300">통신 프로토콜</Label>
            <Select
              value={protocol}
              onValueChange={(value) => setValue('protocol', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="프로토콜 선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="MC_3E_ASCII" className="text-gray-100 hover:bg-gray-700">
                  MC_3E_ASCII
                </SelectItem>
                <SelectItem value="MC_3E_BINARY" className="text-gray-100 hover:bg-gray-700">
                  MC_3E_BINARY
                </SelectItem>
                <SelectItem value="MC_4E_ASCII" className="text-gray-100 hover:bg-gray-700">
                  MC_4E_ASCII
                </SelectItem>
                <SelectItem value="MC_4E_BINARY" className="text-gray-100 hover:bg-gray-700">
                  MC_4E_BINARY
                </SelectItem>
                <SelectItem value="MODBUS_TCP" className="text-gray-100 hover:bg-gray-700">
                  MODBUS_TCP
                </SelectItem>
                <SelectItem value="MODBUS_RTU" className="text-gray-100 hover:bg-gray-700">
                  MODBUS_RTU
                </SelectItem>
                <SelectItem value="MODBUS_ASCII" className="text-gray-100 hover:bg-gray-700">
                  MODBUS_ASCII
                </SelectItem>
                <SelectItem value="MELSEC_ETHERNET" className="text-gray-100 hover:bg-gray-700">
                  MELSEC Ethernet
                </SelectItem>
              </SelectContent>
            </Select>
            {errors.protocol && <p className="text-sm text-red-400 mt-1">{errors.protocol.message}</p>}
          </div>
        </div>
      </div>

      {/* 장치 설정 섹션 */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-3">장치 설정</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="charset" className="text-gray-300">문자셋</Label>
            <Select
              value={watch('charset') || 'UTF8'}
              onValueChange={(value) => setValue('charset', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="UTF8">UTF8</SelectItem>
                <SelectItem value="ASCII">ASCII</SelectItem>
                <SelectItem value="EUC-KR">EUC-KR</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="text_endian" className="text-gray-300">텍스트 엔디안</Label>
            <Select
              value={watch('text_endian') || 'None'}
              onValueChange={(value) => setValue('text_endian', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="None">None</SelectItem>
                <SelectItem value="Big">Big Endian</SelectItem>
                <SelectItem value="Little">Little Endian</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* 장치 블락 설정 섹션 */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-lg font-semibold text-gray-200 mb-3">장치 블락 설정</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="unit_size" className="text-gray-300">단위 크기</Label>
            <Select
              value={watch('unit_size') || '16Bit'}
              onValueChange={(value) => setValue('unit_size', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="16Bit">16Bit</SelectItem>
                <SelectItem value="32Bit">32Bit</SelectItem>
                <SelectItem value="8Bit">8Bit</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="block_size" className="text-gray-300">블락 크기</Label>
            <Input
              id="block_size"
              type="number"
              {...register('block_size', { valueAsNumber: true })}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="64"
            />
          </div>
        </div>
      </div>

      {/* SSL/TLS 설정 섹션 (접을 수 있게) */}
      <details className="border-t border-gray-700 pt-4">
        <summary className="text-lg font-semibold text-gray-200 mb-3 cursor-pointer">SSL/TLS 설정 (선택사항)</summary>
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div>
            <Label htmlFor="ssl_version" className="text-gray-300">SSL 버전</Label>
            <Select
              value={watch('ssl_version') || 'None'}
              onValueChange={(value) => setValue('ssl_version', value)}
            >
              <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
                <SelectValue placeholder="선택" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700">
                <SelectItem value="None">None</SelectItem>
                <SelectItem value="TLS1.2">TLS 1.2</SelectItem>
                <SelectItem value="TLS1.3">TLS 1.3</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="ssl_password" className="text-gray-300">SSL 비밀번호</Label>
            <Input
              id="ssl_password"
              type="password"
              {...register('ssl_password')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="비밀번호 입력"
            />
          </div>
          <div>
            <Label htmlFor="ssl_root_cert" className="text-gray-300">SSL 루트 인증서</Label>
            <Input
              id="ssl_root_cert"
              {...register('ssl_root_cert')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="인증서 경로 또는 내용"
            />
          </div>
          <div>
            <Label htmlFor="ssl_certificate" className="text-gray-300">SSL 인증서</Label>
            <Input
              id="ssl_certificate"
              {...register('ssl_certificate')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="인증서 경로 또는 내용"
            />
          </div>
          <div className="col-span-2">
            <Label htmlFor="ssl_private_key" className="text-gray-300">SSL 비밀키</Label>
            <Input
              id="ssl_private_key"
              {...register('ssl_private_key')}
              className="bg-gray-800 border-gray-700 text-gray-100"
              placeholder="비밀키 경로 또는 내용"
            />
          </div>
        </div>
      </details>

      <div className="flex gap-2 justify-end pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          className="bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
        >
          취소
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          {isSubmitting ? '저장 중...' : '저장'}
        </Button>
      </div>
    </form>
  );
}
