# HRBP Projects — Status & Context

## 1. Leave Email Automation
- **Status:** Built & committed
- **Location:** `LeaveAutomation/`
- **What it does:** Reads emails, parses leave requests, integrates with Lark
- **Files:** `main.py`, `email_parser.py`, `email_reader.py`, `email_responder.py`, `approval_manager.py`, `lark_client.py`

## 2. 51Talk Live Quiz System
- **Status:** Live
- **Repo:** ahmedalsadeqhr/51talk-quiz-live (GitHub Pages)
- **What it does:** Real-time quiz for 600+ concurrent players
- **Stack:** Pure HTML/JS + Supabase (PostgreSQL + Realtime WebSocket)
- **Interfaces:** Player (mobile), Admin (control panel), Presentation (projector)
- **Location:** `Quiz/`

## 3. Attendance & HC Dashboard
- **Status:** Live
- **Repo:** ahmedalsadeqhr/attendance-dashboard
- **What it does:** Streamlit dashboard for fingerprint attendance data, HC metrics, penalty reports
- **Policy doc:** `Policy/Attendance_and_Discipline_Policy_2026.docx`

## 4. iTalent ESS Portal Implementation
- **Status:** Planning complete, pending rollout
- **Plans:** `docs/plans/2026-02-25-italent-implementation-plan.md`, `docs/plans/iTalent-Execution-Rollout-Plan.md`
- **Manager brief:** `docs/plans/iTalent-Manager-Approval-Brief.md`
- **Portal:** 51talk.italent.cn
- **Key decisions confirmed:**
  - Pilot department: CC Team
  - Overtime: Disabled (no overtime policy)
  - Annual leave carryover: Allowed
  - Certificate type: HR Letter only
  - Approval chains: Manual setup later
- **Next step:** Stage 0 configuration (admin access required)

## 5. HR Metrics Dashboard Framework
- **Status:** Framework documented
- **File:** `HR_Metrics_Dashboard.md`, `HR_Metrics_Dashboard.xlsx`
- **Covers:** Recruitment, Onboarding, Retention, Compensation, Performance, L&D

## 6. Probation Review Presentation
- **Status:** Complete
- **See:** `memory/probation-review.md`
