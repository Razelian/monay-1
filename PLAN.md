# Implementation Plan

## Objective
Integrate the standalone `queuethink Info Tab.html` into `main_dashboard.html` as a third tab (`info-view`), keeping all existing dashboard and analytics tabs fully functional.

## Context Analysis

**Current state of `main_dashboard.html`:**
- Has two working tabs: `live-view` (dashboard) and `analytics-view` (charts/KPIs/insights)
- Tab switching via `switchTab(tabId)` — toggles `style.display` between `flex`/`none`
- Nav buttons: `btn-live`, `btn-analytics`, `btn-info` (desktop) and `btn-live-mobile`, `btn-analytics-mobile` (mobile)
- Button highlighting via `setActiveButton(id, isActive)` — toggles Tailwind classes
- Uses Tailwind CSS via CDN with a custom dark theme

**Current state of `queuethink Info Tab.html`:**
- Standalone page with its own `<html>`, `<head>`, and `<body>`
- Uses raw CSS (not Tailwind) with custom properties (`:root` vars)
- Uses Google Fonts: Oxanium + Inter + Devicon CDN
- Two-panel layout: left panel (project info + features + tech stack) and right panel (team members + footer)
- No JavaScript — static content only

**Key conflict risks:**
| Element | Dashboard | Info Tab | Conflict? |
|---------|-----------|----------|-----------|
| `body` styles | Tailwind + neon background | Radial gradient + custom font | YES — if info CSS applies to body |
| `h1, h2, h3` | Tailwind utilities | Oxanium font-family | YES — if info CSS changes all headings |
| `*` universal | Tailwind preflight | `box-sizing: border-box` | Minor (Tailwind already sets this) |
| Class-based selectors (`.wrap`, `.panel-left` etc.) | None match | 50+ rules | NO — class names are unique, no overlap |

## Proposed Architecture

```
main_dashboard.html
├── <head>
│   ├── Existing: Tailwind CDN, Material Symbols, Inter/Sora fonts, Chart.js
│   └── NEW: Oxanium font link, Devicon CSS CDN
├── <style type="text/tailwindcss"> ← dashboard styles (UNCHANGED)
├── NEW: <style id="info-tab-styles"> ← scoped info tab CSS
├── <body>
│   ├── <main id="live-view"> ← existing dashboard (UNCHANGED)
│   ├── <div id="analytics-view"> ← existing analytics (UNCHANGED)
│   └── NEW: <div id="info-view" style="display:none;"> ← info tab wrapper
│       └── (extracted body HTML from Info Tab)
└── <script>
    ├── Clock functions (UNCHANGED)
    ├── switchTab() ← UPDATED to handle 3 tabs
    ├── setActiveButton() (UNCHANGED)
    └── Analytics render functions (UNCHANGED)
```

**CSS scoping strategy:** The three conflicting global selectors (`body`, `html,body`, `*`) are REMOVED from the imported CSS. All other selectors use unique class names (`.wrap`, `.panel-left`, `.team-scroll`, etc.) that don't exist in the dashboard's Tailwind namespace, so they won't leak. The only scoped rule is `h1,h2,h3,.display` → changed to `#info-view h1, #info-view h2, #info-view h3, #info-view .display` to prevent overriding dashboard heading fonts.

**Font strategy:** Oxanium (the heading font for the info tab) is added to the dashboard's `<head>` via a second Google Fonts link. Inter is already loaded by the dashboard. Devicon CSS is added via a new CDN link.

## Step-by-Step Execution

- [ ] **Step 1:** Add fonts and CDNs to dashboard `<head>`  
  File: `ui/main_dashboard.html`, right after the existing font link (after line 7)  
  Add: `Oxanium` font family link and Devicon CSS CDN link  
  Reason: Info tab requires Oxanium for headings and Devicon for tech stack icons

- [ ] **Step 2:** Add scoped Info Tab CSS  
  File: `ui/main_dashboard.html`, right AFTER the closing `</style>` of the existing dashboard styles (after line ~133)  
  - Copy the entire `<style>` block (lines 11-518) from `queuethink Info Tab.html`  
  - Add `id="info-tab-styles"` to the `<style>` tag  
  - **Remove** the `*{box-sizing:border-box;}` rule (Tailwind already handles this)  
  - **Remove** the `html,body{margin:0;padding:0;}` rule  
  - **Remove** the `body{...}` rule (radial gradient background + font) — the info view is a div, not the body. Its background comes from the parent dashboard's body  
  - **Change** `h1,h2,h3,.display{font-family:'Oxanium',sans-serif;...}` to `#info-view h1,#info-view h2,#info-view h3,#info-view .display{...}`  
  - All other CSS rules are class-based (`.wrap`, `.panel-left`, `.hero-title`, etc.) and safe to copy verbatim

- [ ] **Step 3:** Add the `info-view` tab div  
  File: `ui/main_dashboard.html`, right AFTER the closing `</div>` of the analytics-view div (after line 291)  
  - Add `<div id="info-view" style="display:none;" class="info-scope flex-1 overflow-y-auto">`  
  - Copy lines 520-700 from `queuethink Info Tab.html` (the entire body content inside `<div class="wrap">`) into this new div  
  - Remove the existing `</div><!-- end wrap -->` closing divs from the end of the copied content (they'll close inside the new wrapper)

- [ ] **Step 4:** Update `switchTab()` to handle three tabs  
  File: `ui/main_dashboard.html`, in the `<script>` block (around line 351)  
  - Add `const infoView = document.getElementById('info-view');` alongside the other tab variables  
  - Add hide/show logic for all three tabs (currently only handles two with a simple if/else)  
  - Use a cleaner pattern: hide all three, then show only the selected one  
  - Add `setActiveButton('btn-info', tabId === 'info-view');` for desktop  
  - No mobile Info button exists yet — add one in Step 5

- [ ] **Step 5:** Add mobile nav Info button and wire desktop/mobile Info onclick  
  File: `ui/main_dashboard.html`, in the nav section (around line 311)  
  - Add `<a id="btn-info-mobile" ... onclick="switchTab('info-view')">` in the mobile nav links div  
  - Add `onclick="switchTab('info-view')"` to the existing desktop `btn-info` link (line 299 — currently has `href="#"` with no onclick)

- [ ] **Step 6:** Visual verification checklist  
  - [ ] Click "Main Dashboard" → live view visible, analytics hidden, info hidden  
  - [ ] Click "Advanced Analytics" → analytics visible with KPI cards and chart  
  - [ ] Click "Info" → info view visible with project information + team  
  - [ ] Button highlight: only the active tab button shows red/pink style  
  - [ ] All three tabs scroll correctly  
  - [ ] Dashboard video feed still works in live view  
  - [ ] No CSS leakage between tabs (headings in dashboard still use Sora/Inter, headings in info tab use Oxanium)  
  - [ ] No horizontal scrollbar on the info tab at standard window width (1280px)
