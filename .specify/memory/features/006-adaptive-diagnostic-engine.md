# Feature Brief: Adaptive Diagnostic Engine (F1)

**Priority**: Must Have — Core Value Proposition
**Status**: 🔲 Pending — no spec yet
**Dependencies**: 005-navigation-restructure (needs role-based routing + auth)
**Complexity**: XL (core algorithm, backend-heavy)

## Description
Implements the adaptive diagnostic testing engine — the core pedagogical value of Ihsane. Students take ~10-minute adaptive tests per module (Math or Arabic language). The engine selects questions dynamically based on previous answer correctness using a multi-arm bandit approach. Answers are classified into three error types (Resource, Process, Incidental) with misconception detection identifying *why* the student errs. Output: automatic placement into remediation groups (A/B/C) and a per-student competency profile. Built on scikit-learn with custom Bayesian Knowledge Tracing (BKT).

**Derived from**: product-spec.md §5.1 (F1), Appendix C.1
