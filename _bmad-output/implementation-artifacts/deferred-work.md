# Deferred Work Ledger

### DW-1: Per-request DashboardAggregator instance scoping renders instance-level _daily_cache transient across HTTP requests

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-8-4-daily-reinforcement-recommendation.md"), 2026-08-03
location: backend/app/api/endpoints/dashboard.py
reason: DashboardAggregator is instantiated per request in backend/app/api/endpoints/dashboard.py, resetting _daily_cache on each request (though underlying calculation remains deterministic).
status: done 2026-08-03
resolution: resolved by sweep bundle dw-dashboard-scoping-and-null-ordering

### DW-2: CompetencyProfile.last_assessed NULL ordering in get_latest_failed_competency query

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-8-4-daily-reinforcement-recommendation.md"), 2026-08-03
location: backend/app/services/competency_service.py
reason: get_latest_failed_competency orders by last_assessed.desc() without explicit NULL handling or filtering, which may sort NULLs first in PostgreSQL.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-dashboard-scoping-and-null-ordering

### DW-3: Analytics endpoints fallback to active tenant context or zero-UUID sentinel when current_user.organization_id is not set

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: backend/app/api/endpoints/analytics.py
reason: GET and POST /heatmap in backend/app/api/endpoints/analytics.py fallback to get_optional_active_organization_id() or zero-UUID sentinel 00000000-0000-0000-0000-000000000000 if user has no org attribute.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-tenant-fallback-unification

### DW-4: AnalyticsService._mastery_to_score evaluates p_learned > 0 rather than explicit non-null checks

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: backend/app/services/analytics_service.py
reason: In backend/app/services/analytics_service.py, if p_learned is 0.0 for a non-NOT_STARTED profile, it falls through to mastery level dictionary defaults.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-endpoint-service-cleanup

### DW-5: Frontend CompetencyHeatmap.vue does not watch props.moduleId for prop changes post-mount

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: frontend/src/components/analytics/CompetencyHeatmap.vue
reason: Component fetches heatmap in onMounted but does not watch props.moduleId when parent dynamically changes module filter.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-frontend-heatmap-and-types

### DW-6: AnalyticsService.get_heatmap derives student display name from email prefix when name is absent

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: backend/app/services/analytics_service.py
reason: AnalyticsService formats student rows as s.email.split("@")[0], exposing email username as fallback display name.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-endpoint-service-cleanup

### DW-7: Unused POST /heatmap HeatmapFilters body parameter is ignored in favor of query module_id

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: backend/app/api/endpoints/analytics.py
reason: POST /heatmap accepts HeatmapFilters body but forwards only organization_id and module_id to AnalyticsService.get_heatmap.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-endpoint-service-cleanup

### DW-8: Frontend analyticsService.ts type definitions contain optional fields mismatching backend required schemas

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: frontend/src/services/analyticsService.ts
reason: HeatmapCell and MetricsResponse interfaces in frontend/src/services/analyticsService.ts mark p_learned and mastery_speed_days as optional.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-frontend-heatmap-and-types

### DW-9: Duplicate static _mastery_to_color and _mastery_to_score functions exist in analytics.py endpoint module

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md"), 2026-08-03
location: backend/app/api/endpoints/analytics.py
reason: backend/app/api/endpoints/analytics.py retains unused module-level helper functions alongside AnalyticsService static methods.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-endpoint-service-cleanup

### DW-10: Legacy inline helper functions _group_by_competency and _group_by_error_type remain unreferenced in backend/app/api/endpoints/analytics.py

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-2-auto-grouping-into-remediation-groups.md"), 2026-08-03
location: backend/app/api/endpoints/analytics.py
reason: POST /api/v1/analytics/auto-group delegates directly to AnalyticsService.auto_group_students, rendering inline grouping functions in analytics.py dead code.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-endpoint-service-cleanup

### DW-11: Analytics remediation-cards endpoint falls back to active tenant context or zero-UUID sentinel when current_user.organization_id is not set

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-4-printable-remediation-cards.md"), 2026-08-03
location: backend/app/api/endpoints/analytics.py
reason: GET /remediation-cards in backend/app/api/endpoints/analytics.py falls back to get_optional_active_organization_id() or zero-UUID sentinel 00000000-0000-0000-0000-000000000000 if User instance lacks organization_id attribute.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-tenant-fallback-unification

### DW-12: AnalyticsService.get_remediation_cards invokes set_active_organization_id without resetting context variable post-request

origin: migrated from legacy ledger ("_bmad-output/implementation-artifacts/spec-9-4-printable-remediation-cards.md"), 2026-08-03
location: backend/app/services/analytics_service.py
reason: In backend/app/services/analytics_service.py line 138, set_active_organization_id is called without storing or resetting the Token returned by ContextVar.set.
status: done 2026-08-03
resolution: resolved by sweep bundle dw-analytics-tenant-fallback-unification

### DW-13: Backend MetricResponse schema returns `mastery_speed` while frontend MetricsResponse interface expects `mastery_speed_days`.

origin: migrated from legacy ledger ("spec-frontend-heatmap-and-types.md"), 2026-08-03
location: backend/app/schemas/analytics.py, frontend/src/services/analyticsService.ts
reason: Backend MetricResponse schema returns `mastery_speed` while frontend MetricsResponse interface expects `mastery_speed_days`. Evidence: `backend/app/schemas/analytics.py` defines `mastery_speed: float` (line 90), whereas `frontend/src/services/analyticsService.ts` defines `mastery_speed_days: number` (line 36).
status: done 2026-08-03
resolution: resolved by sweep bundle dw-dw-metrics-response-field-alignment

- source_spec: `_bmad-output/implementation-artifacts/spec-dw-metrics-response-field-alignment.md`
  summary: Analytics endpoint get_platform_metrics empty profiles path returns mastery_speed_days as null while populated profiles path returns float.
  evidence: backend/app/api/endpoints/analytics.py lines 155-163 omits mastery_speed_days in empty-profile MetricResponse initialization.

- source_spec: `_bmad-output/implementation-artifacts/spec-dw-metrics-response-field-alignment.md`
  summary: Frontend MetricsResponse interface retains legacy fields overall_mastery_rate and at_risk_students_count not returned by backend MetricResponse schema.
  evidence: frontend/src/services/analyticsService.ts retains overall_mastery_rate and at_risk_students_count optional properties whereas backend/app/schemas/analytics.py MetricResponse does not define them.

- source_spec: `_bmad-output/implementation-artifacts/spec-dw-metrics-response-field-alignment.md`
  summary: Lack of HTTP integration test for mastery_speed_days response field on GET /analytics/metrics endpoint.
  evidence: test_metric_response_schema_fields in backend/tests/api/test_rbac_analytics.py validates schema unit model dump but does not test HTTP response payload.


