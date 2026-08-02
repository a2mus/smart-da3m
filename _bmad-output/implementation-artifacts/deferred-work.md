# Deferred Work Ledger

- source_spec: `_bmad-output/implementation-artifacts/spec-8-4-daily-reinforcement-recommendation.md`
  summary: Per-request DashboardAggregator instance scoping renders instance-level _daily_cache transient across HTTP requests.
  evidence: DashboardAggregator is instantiated per request in backend/app/api/endpoints/dashboard.py, resetting _daily_cache on each request (though underlying calculation remains deterministic).
- source_spec: `_bmad-output/implementation-artifacts/spec-8-4-daily-reinforcement-recommendation.md`
  summary: CompetencyProfile.last_assessed NULL ordering in get_latest_failed_competency query.
  evidence: get_latest_failed_competency orders by last_assessed.desc() without explicit NULL handling or filtering, which may sort NULLs first in PostgreSQL.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: Analytics endpoints fallback to active tenant context or zero-UUID sentinel when current_user.organization_id is not set.
  evidence: GET and POST /heatmap in backend/app/api/endpoints/analytics.py fallback to get_optional_active_organization_id() or zero-UUID sentinel 00000000-0000-0000-0000-000000000000 if user has no org attribute.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: AnalyticsService._mastery_to_score evaluates p_learned > 0 rather than explicit non-null checks.
  evidence: In backend/app/services/analytics_service.py, if p_learned is 0.0 for a non-NOT_STARTED profile, it falls through to mastery level dictionary defaults.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: Frontend CompetencyHeatmap.vue does not watch props.moduleId for prop changes post-mount.
  evidence: Component fetches heatmap in onMounted but does not watch props.moduleId when parent dynamically changes module filter.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: AnalyticsService.get_heatmap derives student display name from email prefix when name is absent.
  evidence: AnalyticsService formats student rows as s.email.split("@")[0], exposing email username as fallback display name.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: Unused POST /heatmap HeatmapFilters body parameter is ignored in favor of query module_id.
  evidence: POST /heatmap accepts HeatmapFilters body but forwards only organization_id and module_id to AnalyticsService.get_heatmap.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: Frontend analyticsService.ts type definitions contain optional fields mismatching backend required schemas.
  evidence: HeatmapCell and MetricsResponse interfaces in frontend/src/services/analyticsService.ts mark p_learned and mastery_speed_days as optional.
- source_spec: `_bmad-output/implementation-artifacts/spec-9-1-real-competency-heatmap-data.md`
  summary: Duplicate static _mastery_to_color and _mastery_to_score functions exist in analytics.py endpoint module.
  evidence: backend/app/api/endpoints/analytics.py retains unused module-level helper functions alongside AnalyticsService static methods.
