# Data Model: Ihsane MVP Platform

## 1. Core Users & Roles

**User**
- `id`: UUID (PK)
- `email`: String (Unique, Nullable for Students)
- `hashed_password`: String (Nullable for Students)
- `pin_code_hash`: String (Nullable, 4-6 digits for students)
- `role`: Enum (`STUDENT`, `PARENT`, `EXPERT`)
- `language`: Enum (`AR`, `FR`)
- `parent_id`: UUID (FK to User, only for STUDENTS)

## 2. Curriculum & Content

**Module**
- `id`: UUID (PK)
- `subject`: String (e.g., 'Mathematics')
- `grade_level`: String (e.g., 'السنة 4')
- `domain`: String (e.g., 'Numbers & Operations')
- `competency_id`: String (e.g., 'MATH-4-NUM-01')
- `status`: Enum (`DRAFT`, `PUBLISHED`)

**Question**
- `id`: UUID (PK)
- `module_id`: UUID (FK to Module)
- `content`: JSONB (Text, images, interactive layout)
- `difficulty_level`: Integer (1-10)
- `target_misconception_id`: String (Nullable)
- `estimated_time_sec`: Integer

**KnowledgeAtom** (Micro-learning remediation content)
- `id`: UUID (PK)
- `competency_id`: String (e.g., 'MATH-4-NUM-01')
- `remediation_type`: Enum (`AUDIO_VISUAL`, `SIMULATION`, `MIND_MAP`)
- `content`: JSONB

## 3. Diagnostics & Analytics

**DiagnosticSession**
- `id`: UUID (PK)
- `student_id`: UUID (FK to User)
- `module_id`: UUID (FK to Module)
- `started_at`: Timestamp
- `completed_at`: Timestamp (Nullable)
- `recommended_group`: Enum (`A`, `B`, `C`) (Populated post-completion)

**DiagnosticAnswer**
- `id`: UUID (PK)
- `session_id`: UUID (FK to DiagnosticSession)
- `question_id`: UUID (FK to Question)
- `is_correct`: Boolean
- `response_time_ms`: Integer
- `error_classification`: Enum (`RESOURCE`, `PROCESS`, `INCIDENTAL`, `NONE`)

**CompetencyProfile** (BKT Matrix)
- `id`: UUID (PK)
- `student_id`: UUID (FK to User)
- `competency_id`: String
- `mastery_level`: Enum (`NOT_STARTED`, `ATTEMPTED`, `FAMILIAR`, `PROFICIENT`, `MASTERED`)
- `p_learned`: Float (0.0 to 1.0)
- `last_assessed`: Timestamp

**RemediationPath**
- `id`: UUID (PK)
- `student_id`: UUID (FK to User)
- `competency_id`: String
- `status`: Enum (`IN_PROGRESS`, `FAILED`, `PASSED`)
- `atoms_completed`: Array of UUIDs

## 4. Alerts

**PedagogicalAlert**
- `id`: UUID (PK)
- `student_id`: UUID (FK to User)
- `trigger_type`: Enum (`REPEATED_FAILURE`, `FRUSTRATION`, `PASSPORT_FAILED`, `INACTIVITY`)
- `severity`: Enum (`INFO`, `WARNING`, `CRITICAL`)
- `status`: Enum (`UNREAD`, `READ`, `RESOLVED`)
