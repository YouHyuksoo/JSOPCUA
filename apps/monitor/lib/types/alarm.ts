// Alarm types for Oracle DB queries

export type AlarmType = '알람' | '일반';

export interface Alarm {
  alarm_id: number;
  equipment_code: string;
  equipment_name: string;
  alarm_type: AlarmType;
  alarm_message: string;
  occurred_at: Date;
  created_at: Date;
}

export interface AlarmStatistics {
  equipment_code: string;
  equipment_name: string;
  alarm_count: number;
  general_count: number;
}
