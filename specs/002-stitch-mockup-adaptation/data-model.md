# Frontend Data Models (Mock Phase)

Since this is a UI implementation task strictly utilizing frontend-mocked data (as per Section 6 of Spec), these interfaces will represent the Vue state required to render the screens correctly.

## 1. Analytics & Focus Metrics

```typescript
export interface FocusSession {
  id: string;
  date: string; // ISO format
  durationMinutes: number;
  focusScore: number; // 0 to 100
  notes?: string;
}

export interface StudentAnalytics {
  studentId: string;
  name: string;
  weeklyFocusAverage: number;
  totalTimeLearned: number;
  sessions: FocusSession[];
}
```

## 2. Journey Map Progress

```typescript
export type TaskState = 'locked' | 'in_progress' | 'completed' | 'remedial';

export interface JourneyTask {
  id: string;
  title: string;
  type: 'video' | 'quiz' | 'boss_battle';
  state: TaskState;
  score?: number;
  coordinates?: { x: number; y: number }; // For visual SVGs map placement
}

export interface LearningJourney {
  moduleName: string;
  currentProgressPct: number;
  tasks: JourneyTask[];
}
```

## 3. Parent Notifications

```typescript
export interface ParentNotification {
  id: string;
  type: 'alert' | 'achievement' | 'system';
  severity: 'low' | 'medium' | 'high';
  message: string;
  read: boolean;
  timestamp: string;
}
```
