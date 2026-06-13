# Specification: Ihsane Parent Dashboard Adaptation

## 1. Feature Overview
Adapt the requested Stitch mockups into fully functional frontend screens for the web app, encompassing their interactions, actions, and overall user journeys. The adaptation covers four core screens:
1. Analytics View - Student Focus
2. Student Dashboard & Journey
3. Ihsane Landing Page
4. Parent Dashboard - Refined Typography & Rhythm

## 2. Success Criteria
* **Accuracy:** HTML/Vue components exactly mirror the Stitch designs visually (colors, typography, layouts).
* **Interactivity:** All proposed actions (buttons, navigations, toggles) have functioning frontend states.
* **Responsiveness:** Screens adapt gracefully across Desktop, Tablet, and Mobile breakpoints.
* **Performance:** Screens render in under 1 second without layout shifts.

## 3. User Scenarios
* **Scenario 1 - Parent views analytics:** A parent accesses the "Analytics View" to check their child's focus metrics and progress.
* **Scenario 2 - Student accesses dashboard:** A student navigates through the "Student Dashboard & Journey" to view upcoming modules and learning map.
* **Scenario 3 - Perspective user visits landing page:** A visitor reads the "Ihsane Landing Page" to understand the platform's value proposition.
* **Scenario 4 - Parent views refined dashboard:** A parent navigates the global "Parent Dashboard" to review notifications, settings, and general rhythm.

## 4. Functional Requirements
* **FR1:** Implement the "Ihsane Landing Page" with routing to authentication/dashboards.
* **FR2:** Implement the "Parent Dashboard" and "Analytics View", integrating dynamic data placeholders.
* **FR3:** Implement the "Student Dashboard & Journey" with interactive journey maps.
* **FR4:** Implement state management (e.g., Pinia or local Vue refs) to handle page interactions (modals, dropdowns, tab switching).

## 5. Entities & Data
* **User (Parent/Student)**
* **Analytics Metrics** (Focus scores, progress percentages, session time)
* **Journey Tasks** (Modules, lessons, milestones)

## 6. Assumptions & Scope
* **Assumptions:** Assets (images, fonts, icons) from the Stitch project can be downloaded or extracted. Backend API integration is handled separately (mock data will be used for UI development). No backend logic changes are expected in this branch.
* **Out of Scope:** Complete backend and API integration, live database mutations.

## 7. Clarifications
* **Resolved (Stitch Mockups):** The user has manually provided the exact Stitch mockups as a `.zip` archive, bypassing the MCP plugin. The mockups have been extracted to local directory.
