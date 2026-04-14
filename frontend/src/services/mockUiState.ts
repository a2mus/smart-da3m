import type { 
  FocusSession, 
  StudentAnalytics, 
  LearningJourney, 
  ParentNotification 
} from '@/models/stitchMockups';

const mockFocusSessions: FocusSession[] = [
  { id: '1', date: '2026-04-10T10:00:00Z', durationMinutes: 45, focusScore: 85, notes: 'Good session' },
  { id: '2', date: '2026-04-11T14:30:00Z', durationMinutes: 30, focusScore: 92 },
  { id: '3', date: '2026-04-12T09:15:00Z', durationMinutes: 50, focusScore: 78, notes: 'Distracted by noise' },
  { id: '4', date: '2026-04-13T16:00:00Z', durationMinutes: 60, focusScore: 95 }
];

export const mockStudentAnalytics: StudentAnalytics = {
  studentId: 'stu_123',
  name: 'Ahmed',
  weeklyFocusAverage: 88,
  totalTimeLearned: 185,
  sessions: mockFocusSessions
};

export const mockLearningJourney: LearningJourney = {
  moduleName: 'Mathematics: Fractions',
  currentProgressPct: 65,
  tasks: [
    { id: 't1', title: 'Introduction to Fractions', type: 'video', state: 'completed', score: 100, coordinates: { x: 10, y: 50 } },
    { id: 't2', title: 'Basic Additions', type: 'quiz', state: 'completed', score: 85, coordinates: { x: 30, y: 30 } },
    { id: 't3', title: 'Equivalent Fractions', type: 'video', state: 'completed', score: 100, coordinates: { x: 50, y: 70 } },
    { id: 't4', title: 'Fraction Matching', type: 'quiz', state: 'in_progress', coordinates: { x: 70, y: 50 } },
    { id: 't5', title: 'Module Boss', type: 'boss_battle', state: 'locked', coordinates: { x: 90, y: 50 } }
  ]
};

export const mockParentNotifications: ParentNotification[] = [
  { id: 'n1', type: 'achievement', severity: 'low', message: 'Ahmed completed "Equivalent Fractions"!', read: false, timestamp: '2026-04-14T09:00:00Z' },
  { id: 'n2', type: 'alert', severity: 'medium', message: 'Focus score dropped during last session.', read: true, timestamp: '2026-04-12T10:30:00Z' },
  { id: 'n3', type: 'system', severity: 'low', message: 'New module available: Geometry Basics', read: false, timestamp: '2026-04-11T14:00:00Z' }
];

export const mockUiState = {
  analytics: mockStudentAnalytics,
  journey: mockLearningJourney,
  notifications: mockParentNotifications
};
