# Epic 9 Context: Expert Analytics & Classroom Tools

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Pedagogical experts require decision-support tools to track class progress, address skill gaps, export progress records, and conduct targeted offline interventions. This epic replaces mock analytics implementations with real database-driven endpoints, connects existing engine auto-grouping logic to the API layer, wires report export functionality, and creates print-formatted remediation cards for classroom use.

## Stories

- Story 9.1: Real Competency Heatmap Data
- Story 9.2: Auto-Grouping into Remediation Groups
- Story 9.3: Report Export (PDF/CSV) — Wire Orphaned Exporter
- Story 9.4: Printable Remediation Cards

## Requirements & Constraints

- Competency Heatmap: Display a matrix of students by competencies for the expert's organization. Each cell maps student mastery level to a color: red for NOT_STARTED or ATTEMPTED, yellow for FAMILIAR, and green for PROFICIENT or MASTERED.
- Multi-Tenancy & Data Isolation: All analytics endpoints must strictly filter data by the authenticated expert's active organization ID. Experts can only access records for students within their organization.
- Auto-Grouping: Cluster students automatically by shared competency gaps and error types. The auto-grouping endpoint must delegate clustering directly to domain engine logic rather than reimplementing inline logic.
- Report Export: Provide exports in CSV and PDF formats containing student heatmap data. CSV exports must use stable, machine-parseable headers (student, competency, mastery_level, last_assessed).
- Printable Remediation Cards: Render print-formatted views for individual students or remediation groups. Cards must include student names, failed competencies, error classifications, and recommended remediation atoms. Interactive controls must be hidden or formatted for clean page printing via CSS print stylesheets.

## Technical Decisions

- Backend Endpoints: Expose analytics routes under `/api/v1/analytics/*`:
  - `GET /api/v1/analytics/heatmap?module_id={id}` returns real student matrix data.
  - `POST /api/v1/analytics/auto-group` returns clustered student groups (`[{competency, error_type, students: [...]}]`).
  - `GET /api/v1/analytics/export?format=csv` and `GET /api/v1/analytics/export?format=pdf` return downloadable files.
  - `GET /api/v1/analytics/remediation-cards?student_id={id}` returns print-formatted content.
- Layering & Services: `AnalyticsService` handles business logic and retrieves data through `AnalyticsRepo`. Export requests delegate through `AnalyticsService` to `ReportExporter` (`services/report_exporter.py`).
- Frontend Integration: `analyticsService.ts` replaces hardcoded mock objects with API calls. `CompetencyHeatmap.vue` renders state directly from `analyticsStore`.

## UX & Interaction Patterns

- Heatmap Grid: Matrix layout displaying students along one axis and competencies along the other with status colors.
- Auto-Group Overlay: Display suggested remediation clusters directly over the heatmap interface for immediate context.
- Export & Print Actions: Dedicated buttons in the analytics view for exporting reports and triggering remediation card printing.
- Print Formatting: Remediation cards utilize CSS `@media print` rules for page breaks and clean layout without interactive navigation elements.

## Cross-Story Dependencies

- External Dependencies: Requires Epic 2 (Backend Core & Diagnostic Engine) for competency data and Epic 3 (Remediation Pathways) for knowledge atom mappings and error classifications.
- Internal Dependencies: Stories 9.2, 9.3, and 9.4 build upon the real student competency data pipeline established in Story 9.1.
