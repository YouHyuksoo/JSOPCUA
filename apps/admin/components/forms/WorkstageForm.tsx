"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { workstageSchema, WorkstageFormData } from "@/lib/validators/process";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Workstage } from "@/lib/types/workstage";
import { Machine } from "@/lib/types/machine";

interface WorkstageFormProps {
  defaultValues?: Workstage;
  machines: Machine[];
  onSubmit: (data: WorkstageFormData) => void;
  onCancel: () => void;
}

export default function WorkstageForm({
  defaultValues,
  machines,
  onSubmit,
  onCancel,
}: WorkstageFormProps) {
  // Workstage를 WorkstageFormData로 변환하는 헬퍼 함수
  const convertWorkstageToFormData = (
    workstage: Workstage
  ): WorkstageFormData => {
    const machine = machines.find(
      (m) => m.machine_code === workstage.machine_code
    );
    return {
      machine_id: machine?.id || 0,
      workstage_sequence: workstage.workstage_sequence,
      workstage_code: workstage.workstage_code,
      workstage_name: workstage.workstage_name,
      equipment_type: workstage.equipment_type || "",
      enabled: workstage.enabled,
    };
  };

  const form = useForm<WorkstageFormData>({
    resolver: zodResolver(workstageSchema),
    defaultValues: defaultValues
      ? convertWorkstageToFormData(defaultValues)
      : {
          machine_id: 0,
          workstage_sequence: 1,
          workstage_code: "",
          workstage_name: "",
          equipment_type: "",
          enabled: true,
        },
  });

  const { register, handleSubmit, setValue, watch, formState } = form;
  const { errors, isSubmitting } = formState;

  const machineId = watch("machine_id");
  const enabled = watch("enabled");

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <Label htmlFor="machine_id" className="text-gray-300">
          설비 *
        </Label>
        <Select
          value={machineId?.toString()}
          onValueChange={(value) => setValue("machine_id", parseInt(value))}
        >
          <SelectTrigger className="bg-gray-800 border-gray-700 text-gray-100">
            <SelectValue placeholder="설비 선택" />
          </SelectTrigger>
          <SelectContent className="bg-gray-800 border-gray-700">
            {machines.map((machine) => (
              <SelectItem
                key={machine.id}
                value={machine.id.toString()}
                className="text-gray-100 focus:bg-gray-700"
              >
                {machine.machine_name} ({machine.machine_code})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.machine_id && (
          <p className="text-sm text-red-400 mt-1">
            {errors.machine_id.message}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="workstage_code" className="text-gray-300">
            공정 코드 * (14자)
          </Label>
          <Input
            id="workstage_code"
            {...register("workstage_code")}
            disabled={!!defaultValues}
            placeholder="MC001-CNC-0001"
            maxLength={14}
            className="bg-gray-800 border-gray-700 text-gray-100 disabled:opacity-50"
          />
          {errors.workstage_code && (
            <p className="text-sm text-red-400 mt-1">
              {errors.workstage_code.message}
            </p>
          )}
          {defaultValues && (
            <p className="text-sm text-gray-500 mt-1">
              공정 코드는 수정할 수 없습니다
            </p>
          )}
        </div>

        <div>
          <Label htmlFor="workstage_sequence" className="text-gray-300">
            공정 순서 *
          </Label>
          <Input
            id="workstage_sequence"
            type="number"
            {...register("workstage_sequence", { valueAsNumber: true })}
            placeholder="1"
            className="bg-gray-800 border-gray-700 text-gray-100"
          />
          {errors.workstage_sequence && (
            <p className="text-sm text-red-400 mt-1">
              {errors.workstage_sequence.message}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="workstage_name" className="text-gray-300">
            공정 이름 *
          </Label>
          <Input
            id="workstage_name"
            {...register("workstage_name")}
            placeholder="CNC 가공"
            className="bg-gray-800 border-gray-700 text-gray-100"
          />
          {errors.workstage_name && (
            <p className="text-sm text-red-400 mt-1">
              {errors.workstage_name.message}
            </p>
          )}
        </div>

        <div>
          <Label htmlFor="equipment_type" className="text-gray-300">
            설비 타입
          </Label>
          <Input
            id="equipment_type"
            {...register("equipment_type")}
            placeholder="CNC"
            className="bg-gray-800 border-gray-700 text-gray-100"
          />
          {errors.equipment_type && (
            <p className="text-sm text-red-400 mt-1">
              {errors.equipment_type.message}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="enabled"
          checked={enabled}
          onCheckedChange={(checked) => setValue("enabled", checked as boolean)}
          className="bg-gray-800 border-gray-700"
        />
        <Label htmlFor="enabled" className="text-gray-300 cursor-pointer">
          활성화
        </Label>
      </div>

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
          {isSubmitting ? "저장 중..." : "저장"}
        </Button>
      </div>
    </form>
  );
}
