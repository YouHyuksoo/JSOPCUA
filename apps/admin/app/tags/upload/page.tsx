'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { uploadCSV } from '@/lib/api/tags';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Nav from '@/components/nav';
import { toast } from 'sonner';
import Papa from 'papaparse';

interface CSVRow {
  name: string;
  address: string;
  data_type: string;
  plc_id: string;
  description?: string;
}

export default function UploadTagsPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<CSVRow[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);

    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setPreview(results.data.slice(0, 5) as CSVRow[]);
      },
    });
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('파일을 선택해주세요');
      return;
    }

    setUploading(true);
    try {
      const result = await uploadCSV(file);
      toast.success(`${result.success_count}개 태그가 업로드되었습니다`);
      if (result.failed_count > 0) {
        toast.warning(`${result.failed_count}개 태그 업로드 실패`);
      }
      router.push('/tags');
    } catch (error) {
      toast.error('CSV 업로드 실패');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">태그 CSV 업로드</h1>

        <div className="bg-white rounded-lg shadow p-6 max-w-3xl">
          <Alert className="mb-6">
            <AlertDescription>
              CSV 파일 형식: name, address, data_type, plc_id, description (선택)
              <br />
              예시: Temperature_Sensor_01, D100, FLOAT, 1, Room temperature sensor
            </AlertDescription>
          </Alert>

          <div className="space-y-4">
            <div>
              <Label htmlFor="csv-file">CSV 파일 선택</Label>
              <Input
                id="csv-file"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="mt-1"
              />
            </div>

            {preview.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">미리보기 (처음 5개 행)</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full border">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 border text-left text-xs">Name</th>
                        <th className="px-4 py-2 border text-left text-xs">Address</th>
                        <th className="px-4 py-2 border text-left text-xs">Data Type</th>
                        <th className="px-4 py-2 border text-left text-xs">PLC ID</th>
                        <th className="px-4 py-2 border text-left text-xs">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {preview.map((row, index) => (
                        <tr key={index}>
                          <td className="px-4 py-2 border text-sm">{row.name}</td>
                          <td className="px-4 py-2 border text-sm">{row.address}</td>
                          <td className="px-4 py-2 border text-sm">{row.data_type}</td>
                          <td className="px-4 py-2 border text-sm">{row.plc_id}</td>
                          <td className="px-4 py-2 border text-sm">{row.description || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => router.push('/tags')}>
                취소
              </Button>
              <Button onClick={handleUpload} disabled={!file || uploading}>
                {uploading ? '업로드 중...' : '업로드'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
