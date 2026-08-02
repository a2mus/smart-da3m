# Deferred Work Ledger

- source_spec: `_bmad-output/implementation-artifacts/spec-8-4-daily-reinforcement-recommendation.md`
  summary: Per-request DashboardAggregator instance scoping renders instance-level _daily_cache transient across HTTP requests.
  evidence: DashboardAggregator is instantiated per request in backend/app/api/endpoints/dashboard.py, resetting _daily_cache on each request (though underlying calculation remains deterministic).
- source_spec: `_bmad-output/implementation-artifacts/spec-8-4-daily-reinforcement-recommendation.md`
  summary: CompetencyProfile.last_assessed NULL ordering in get_latest_failed_competency query.
  evidence: get_latest_failed_competency orders by last_assessed.desc() without explicit NULL handling or filtering, which may sort NULLs first in PostgreSQL.
