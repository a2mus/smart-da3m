# Feature Brief: Pedagogical Alerts System (F4)

**Priority**: Must Have — Safety Net
**Status**: 🔲 Pending — no spec yet
**Dependencies**: 006-adaptive-diagnostic-engine, 007-remediation-pathways
**Complexity**: M (alert rules engine, notification delivery)

## Description
Implements the pedagogical alert system that ensures no student falls through the cracks. Triggers on: ≥3 consecutive failures on same exercise type, declining response speed (frustration indicator), failed post-remediation validation, or inactivity > N days. Alerts are delivered to parents (simplified notification with recommended action) and experts (detailed diagnostic with intervention strategy). Three severity levels: Info, Warning, Critical. Includes auto-grouping suggestions for experts — students sharing the same error pattern are grouped for collective remediation.

**Derived from**: product-spec.md §5.1 (F4), Appendix C.3
