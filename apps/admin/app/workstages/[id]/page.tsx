"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getWorkstage, updateWorkstage } from "@/lib/api/workstages";
import { getMachines } from "@/lib/api/machines";
import { WorkstageFormData } from "@/lib/validators/process";
import { Workstage, CreateWorkstageRequest } from "@/lib/types/workstage";
import { Machine } from "@/lib/types/machine";
import WorkstageForm from "@/components/forms/WorkstageForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { ArrowLeft, Network, Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function EditWorkstagePage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const [workstage, setWorkstage] = useState<Workstage | null>(null);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [workstageData, machinesData] = await Promise.all([
          getWorkstage(id),
          getMachines(1, 100),
        ]);
        setWorkstage(workstageData);
        setMachines(machinesData.items);
      } catch (error) {
        toast.error("데이터 조회 실패");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleSubmit = async (data: WorkstageFormData) => {
    try {
      // WorkstageFormData를 CreateWorkstageRequest로 변환
      const machine = machines.find((m) => m.id === data.machine_id);
      const request: CreateWorkstageRequest = {
        machine_code: machine?.machine_code || null,
        workstage_sequence: data.workstage_sequence,
        workstage_code: data.workstage_code,
        workstage_name: data.workstage_name,
        equipment_type: data.equipment_type || null,
        enabled: data.enabled,
      };
      await updateWorkstage(id, request);
      toast.success("공정이 수정되었습니다");
      router.push("/workstages");
    } catch (error) {
      toast.error("공정 수정 실패");
    }
  };

  const handleCancel = () => {
    router.push("/workstages");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!workstage) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-gray-400 text-lg mb-4">공정을 찾을 수 없습니다</p>
        <Link href="/workstages">
          <Button
            variant="outline"
            className="bg-gray-800 border-gray-700 hover:bg-gray-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            목록으로 돌아가기
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/workstages">
          <Button
            variant="outline"
            size="sm"
            className="bg-gray-800 border-gray-700 hover:bg-gray-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Network className="h-8 w-8" />
            공정 수정
          </h1>
          <p className="text-gray-400 mt-1">
            {workstage.workstage_name} ({workstage.workstage_code})
          </p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-2xl">
        <CardHeader>
          <CardTitle className="text-white">공정 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <WorkstageForm
            defaultValues={workstage}
            machines={machines}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
          />
        </CardContent>
      </Card>
    </div>
  );
}
