'use client';

/**
 * Queue Monitor Component
 *
 * Real-time visualization of data queue status
 */

import { QueueStatus } from '@/lib/api/pollingApi';

interface QueueMonitorProps {
  queue: QueueStatus;
}

export default function QueueMonitor({ queue }: QueueMonitorProps) {
  const usagePercent = (queue.queue_size / queue.queue_maxsize) * 100;
  const isWarning = usagePercent > 70;
  const isDanger = usagePercent > 90;

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Data Queue Status</h2>

      {/* Queue usage bar */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm text-gray-600">Queue Usage</span>
          <span className={`text-sm font-medium ${
            isDanger ? 'text-red-600' : isWarning ? 'text-yellow-600' : 'text-green-600'
          }`}>
            {usagePercent.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all duration-300 ${
              isDanger ? 'bg-red-600' : isWarning ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(usagePercent, 100)}%` }}
          />
        </div>
      </div>

      {/* Queue statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Current Size</div>
          <div className="text-2xl font-bold">{queue.queue_size}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Max Size</div>
          <div className="text-2xl font-bold">{queue.queue_maxsize}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <div className="text-sm text-gray-600">Available</div>
          <div className="text-2xl font-bold">
            {queue.queue_maxsize - queue.queue_size}
          </div>
        </div>
      </div>

      {/* Warning message */}
      {queue.queue_is_full && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          <strong>Warning:</strong> Queue is full! Data may be lost.
        </div>
      )}
      {isWarning && !queue.queue_is_full && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          <strong>Warning:</strong> Queue usage is high. Consider optimizing data consumers.
        </div>
      )}
    </div>
  );
}
