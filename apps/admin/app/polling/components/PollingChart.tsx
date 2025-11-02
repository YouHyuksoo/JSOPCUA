'use client';

/**
 * Polling Statistics Chart Component
 *
 * Real-time visualization of polling performance metrics
 */

import { useEffect, useRef } from 'react';
import { GroupStatus } from '@/lib/api/pollingApi';

interface PollingChartProps {
  groups: GroupStatus[];
}

export default function PollingChart({ groups }: PollingChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || groups.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Chart dimensions
    const padding = 40;
    const chartWidth = canvas.width - 2 * padding;
    const chartHeight = canvas.height - 2 * padding;

    // Find max values for scaling
    const maxPolls = Math.max(...groups.map(g => g.total_polls), 1);
    const maxAvgTime = Math.max(...groups.map(g => g.avg_poll_time_ms), 1);

    // Bar width
    const barWidth = chartWidth / (groups.length * 2);
    const spacing = barWidth / 2;

    // Draw axes
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.lineTo(canvas.width - padding, canvas.height - padding);
    ctx.stroke();

    // Draw bars for each group
    groups.forEach((group, index) => {
      const x = padding + index * (barWidth * 2 + spacing);

      // Success rate bar (green)
      const successRate = group.total_polls > 0
        ? (group.success_count / group.total_polls)
        : 0;
      const successHeight = successRate * chartHeight;

      ctx.fillStyle = successRate > 0.9 ? '#10b981' : successRate > 0.7 ? '#f59e0b' : '#ef4444';
      ctx.fillRect(
        x,
        canvas.height - padding - successHeight,
        barWidth,
        successHeight
      );

      // Average time bar (blue) - normalized to max
      const timeRatio = maxAvgTime > 0 ? (group.avg_poll_time_ms / maxAvgTime) : 0;
      const timeHeight = timeRatio * chartHeight;

      ctx.fillStyle = '#3b82f6';
      ctx.fillRect(
        x + barWidth + 5,
        canvas.height - padding - timeHeight,
        barWidth,
        timeHeight
      );

      // Group name label
      ctx.fillStyle = '#374151';
      ctx.font = '12px sans-serif';
      ctx.save();
      ctx.translate(x + barWidth, canvas.height - padding + 10);
      ctx.rotate(-Math.PI / 4);
      ctx.fillText(group.group_name, 0, 0);
      ctx.restore();
    });

    // Legend
    ctx.fillStyle = '#10b981';
    ctx.fillRect(canvas.width - 150, 20, 20, 20);
    ctx.fillStyle = '#374151';
    ctx.font = '14px sans-serif';
    ctx.fillText('Success Rate', canvas.width - 125, 35);

    ctx.fillStyle = '#3b82f6';
    ctx.fillRect(canvas.width - 150, 50, 20, 20);
    ctx.fillStyle = '#374151';
    ctx.fillText('Avg Time (rel)', canvas.width - 125, 65);

    // Y-axis labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('100%', padding - 10, padding + 5);
    ctx.fillText('50%', padding - 10, padding + chartHeight / 2 + 5);
    ctx.fillText('0%', padding - 10, canvas.height - padding + 5);

  }, [groups]);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Performance Overview</h2>
      <canvas
        ref={canvasRef}
        width={800}
        height={400}
        className="w-full"
        style={{ maxHeight: '400px' }}
      />
    </div>
  );
}
