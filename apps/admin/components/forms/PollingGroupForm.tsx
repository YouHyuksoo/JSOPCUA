'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { pollingGroupSchema, PollingGroupFormData } from '@/lib/validators/polling-group';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { PollingGroup } from '@/lib/types/polling-group';
import { Tag } from '@/lib/types/tag';
import { useState } from 'react';

interface PollingGroupFormProps {
  defaultValues?: PollingGroup;
  tags: Tag[];
  onSubmit: (data: PollingGroupFormData) => void;
  onCancel: () => void;
}

export default function PollingGroupForm({ defaultValues, tags, onSubmit, onCancel }: PollingGroupFormProps) {
  const [selectedTags, setSelectedTags] = useState<number[]>(defaultValues?.tag_ids || []);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<PollingGroupFormData>({
    resolver: zodResolver(pollingGroupSchema),
    defaultValues: defaultValues ? {
      name: defaultValues.name,
      polling_interval_ms: defaultValues.polling_interval_ms,
      tag_ids: defaultValues.tag_ids,
    } : {
      polling_interval_ms: 1000,
    },
  });

  const handleTagToggle = (tagId: number) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  };

  const handleFormSubmit = (data: PollingGroupFormData) => {
    onSubmit({ ...data, tag_ids: selectedTags });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="name">폴링 그룹 이름</Label>
        <Input id="name" {...register('name')} />
        {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <Label htmlFor="polling_interval_ms">폴링 주기 (ms)</Label>
        <Input
          id="polling_interval_ms"
          type="number"
          {...register('polling_interval_ms', { valueAsNumber: true })}
        />
        {errors.polling_interval_ms && (
          <p className="text-sm text-red-500 mt-1">{errors.polling_interval_ms.message}</p>
        )}
      </div>

      <div>
        <Label>태그 선택</Label>
        <div className="border rounded-md p-4 max-h-64 overflow-y-auto space-y-2">
          {tags.map((tag) => (
            <div key={tag.id} className="flex items-center space-x-2">
              <Checkbox
                id={`tag-${tag.id}`}
                checked={selectedTags.includes(tag.id)}
                onCheckedChange={() => handleTagToggle(tag.id)}
              />
              <label htmlFor={`tag-${tag.id}`} className="text-sm cursor-pointer">
                {tag.name} ({tag.address})
              </label>
            </div>
          ))}
        </div>
        {selectedTags.length === 0 && (
          <p className="text-sm text-red-500 mt-1">최소 1개 이상의 태그를 선택해야 합니다</p>
        )}
      </div>

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? '저장 중...' : '저장'}
        </Button>
      </div>
    </form>
  );
}
