# Quickstart: Mockup Adaptation

Follow these steps to mount and verify the newly adapted UI mockups.

## 1. Running the Project
The screens are integrated into the existing Vite frontend workspace.
```bash
cd frontend
pnpm install
pnpm run dev
```

## 2. Verification Scenarios

### Scenario 1: Responsiveness check
- Open browser devtools (`F12`).
- Navigate to the `Landing Page` (`/`).
- Toggle between `375px` (Mobile), `768px` (Tablet), and `1440px` (Desktop). The layout must seamlessly wrap and font sizes adjust rhythmically without horizontal scrolling.

### Scenario 2: Student Tablet Simulation
- Navigate to the `Student Journey` route (`/student/journey`).
- Set viewport to `1024x768` (Standard iPad).
- Verify that touch targets for learning tasks are at least `60px` as required by the Constitution.

### Scenario 3: Analytics Focus Drilldown
- Navigate to `Parent Analytics` (`/parent/analytics`).
- Click on any bar chart or focus metric element.
- Expected behavior: A frontend mock interaction (e.g., a modal or expansion panel) handles the click event natively using Vue state.

## 3. Visual Regression
Compare the rendered UI visually side-by-side with the PNG artifacts found in `mockups/stitch_ihsane_parent_dashboard/`. Colors mapped manually via Tailwind config must exactly match hue and softness.
