# Inner API Contracts

## Authentication
- `POST /api/v1/auth/login/parent` -> Access/Refresh Tokens
- `POST /api/v1/auth/login/expert` -> Access/Refresh Tokens
- `POST /api/v1/auth/login/student` -> (Requires `pin_code` and `parent_id` context) -> Access/Refresh Tokens

## Student Diagnostic Engine
- `POST /api/v1/diagnostic/start` (Body: `module_id`) -> Returns config & first `question_id`
- `POST /api/v1/diagnostic/answer` (Body: `session_id`, `question_id`, `answer`, `time_ms`) -> Returns next question or `session_complete` flag.
- `GET /api/v1/diagnostic/results/{session_id}` -> Returns mastery placement and recommended `remediation_group`.

## Remediation Engine
- `GET /api/v1/remediation/pathway/{competency_id}` -> Returns ordered sequence of `KnowledgeAtom`s.
- `POST /api/v1/remediation/passport/evaluate` -> Returns boolean mastery & updates `CompetencyProfile`.

## Parent Dashboard
- `GET /api/v1/dashboard/parent/overview` -> Radar chart aggregates, smart qualitative messages.
- `GET /api/v1/dashboard/parent/alerts` -> Unread pedagogical alerts.

## Expert Back-Office
- `POST /api/v1/content/modules` -> Creates curriculum scaffolding.
- `POST /api/v1/content/questions` -> Bulk insert JSON array of tagged questions.
- `GET /api/v1/analytics/heatmap` -> Returns multi-dimensional matrix of student × competency mastery.
