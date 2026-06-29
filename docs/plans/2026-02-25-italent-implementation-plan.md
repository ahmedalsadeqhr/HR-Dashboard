# iTalent HR System Implementation Plan — 51Talk Egypt

**Goal:** Configure iTalent for 51Talk Egypt's leave management and employee self-service aligned with company policy, attendance dashboard, and existing workflows.

**Architecture:** iTalent (51talk.italent.cn) serves as the system of record for leave requests and approvals. The existing Attendance Dashboard (Streamlit) continues to process raw fingerprint attendance data and generate penalty reports. iTalent bridges the gap by digitizing the leave submission/approval workflow and feeding approved leaves into the Attendance Dashboard's leave sheet.

**Tech Stack:** iTalent (cloud.italent.cn), Streamlit Attendance Dashboard, Excel leave sheets, Email (hr.egy@51talk.com), GlobeMed Egypt (medical insurance)

---

## Phase 1: Leave Types Configuration

> **Goal:** Map 51Talk Egypt's leave policy to iTalent's configured leave types. Fix unnamed placeholders, set correct entitlements.

### Task 1.1 — Audit & Rename Leave Types

**Current State in iTalent:**
| iTalent Name | Status |
|---|---|
| Sick Leave | ✅ Named correctly |
| Unpaid Leave | ✅ Named correctly |
| Annual Leave | ⚠️ Shows 0 days — entitlement not set |
| Miscarriage Leave | ✅ Named correctly |
| Bereavement Leave | ✅ Named correctly |
| Maternity Leave | ✅ Named correctly |
| Paternity Leave | ✅ Named correctly |
| Leave Item 6 | ❌ Unnamed — rename to **Casual Leave** |
| Leave Item 34 | ❌ Unnamed — rename to **Marriage Leave** |

**Action Steps:**
1. Go to Admin → Attendance → Leave Configuration
2. Rename "Leave Item 6" → **Casual Leave**
3. Rename "Leave Item 34" → **Marriage Leave**
4. Fix typo: "Leave Applictaion" → **Leave Application** (appears in 2 menu locations)

---

### Task 1.2 — Set Leave Entitlements Per Policy

Configure each leave type with the following rules from the 51Talk Egypt Employee Handbook:

| Leave Type | Entitlement | Pay | Conditions |
|---|---|---|---|
| **Annual Leave** | 15 days (< 1yr service) / 21 days (≥ 1yr) | Full | **Carryover allowed** (confirmed by management) |
| **Casual Leave** | 7 days/year | Full | Max 2 days per request; counts toward annual leave |
| **Sick Leave** | As needed | 75% salary | Requires stamped sick note from accredited hospital |
| **Maternity Leave** | 120 days | Full | After 1 full year of service; requires birth certificate |
| **Paternity Leave** | 1 day/occurrence (max 3×) | Full | Requires proof |
| **Marriage Leave** | 3 days | Full | Requires proof; extra days from annual balance or unpaid |
| **Bereavement Leave** | 3 days | Full | Parents, spouse, children only; proof required |
| **Miscarriage Leave** | Per Egyptian Labor Law | Full | Medical documentation required |
| **Unpaid Leave** | As approved | 0% | Manager + HR approval required |

**Configuration Checklist:**
- [ ] Annual Leave: Set balance rule (15 days < 1yr / 21 days ≥ 1yr based on join date)
- [ ] Casual Leave: Set max 7 days/year, max 2 days per request
- [ ] Sick Leave: Set pay rate to 75%, require attachment (doctor's note)
- [ ] Maternity Leave: Set 120 days, require 1 year service eligibility
- [ ] Paternity Leave: Set max 3 occurrences/year, 1 day each
- [ ] Marriage Leave: Set 3 days, require attachment
- [ ] Bereavement Leave: Set 3 days, restricted beneficiaries
- [ ] Unpaid Leave: No balance limit, dual approval (manager + HR)

---

## Phase 2: Approval Workflow Configuration

> **Goal:** Map 51Talk Egypt's approval hierarchy to iTalent's workflow engine.

### Task 2.1 — Define Approval Chain Per Leave Type

**Current Approval Process (from Handbook):**
```
Employee → Direct Manager → Higher Management → HR (hr.egy@51talk.com)
```

**iTalent Workflow to Configure:**

| Leave Type | Approval Steps |
|---|---|
| Annual Leave (≤ 3 days) | Step 1: Direct Manager |
| Annual Leave (> 3 days) | Step 1: Direct Manager → Step 2: Director/2nd-line Manager → Step 3: HR |
| Casual Leave | Step 1: Direct Manager |
| Sick Leave | Step 1: Direct Manager → Step 2: HR (for documentation review) |
| Maternity / Miscarriage | Step 1: Direct Manager → Step 2: HR |
| Paternity | Step 1: Direct Manager |
| Marriage Leave | Step 1: Direct Manager → Step 2: HR |
| Bereavement Leave | Step 1: Direct Manager |
| Unpaid Leave | Step 1: Direct Manager → Step 2: Director → Step 3: HR |

**Advance Notice Rules (configure as submission restrictions):**
- Leave < 3 days: Minimum 1 week (7 days) advance notice required
- Leave > 2 days: Minimum 1 month (30 days) advance notice required

**Actions in iTalent:**
1. Go to Admin → Workflow Configuration
2. Create workflow "Leave Standard" — 1 level (Direct Manager)
3. Create workflow "Leave Extended" — 3 levels (Manager → Director → HR)
4. Create workflow "Leave HR Reviewed" — 2 levels (Manager → HR)
5. Assign workflows to each leave type as per table above
6. Configure **Process Delegation** rule: managers on leave must delegate to deputy

---

### Task 2.2 — Configure Batch Approval Settings

iTalent supports **Batch Approval** and **Batch Disagree** — configure these for HR role:

- [ ] Enable batch approval for HR account (hr.egy@51talk.com)
- [ ] Enable Process Delegation for all manager-level roles
- [ ] Set sort order: Receiving Time in Reverse Chronological Order (already default)
- [ ] Set notification: email to manager on new pending request

---

## Phase 3: Attendance Integration

> **Goal:** Connect iTalent leave approvals to the Streamlit Attendance Dashboard.

### Task 3.1 — Align Leave Export Format with Dashboard Input

The Attendance Dashboard accepts leave data in two formats:
1. **Matrix format:** CRM | Date1 | Date2 | ... (columns per date)
2. **Vertical format:** CRM | Date | Leave Type

**Action:** Configure iTalent leave export to match the vertical format:

| Column | iTalent Field | Notes |
|---|---|---|
| CRM | Employee CRM ID | Must match master data |
| Date | Leave Date | One row per day |
| Leave Type | Leave Project name | e.g., Annual Leave, Sick Leave |
| Status | Approved only | Only export approved leaves |

**Export Schedule:**
- Export from iTalent: 21st of each month (aligns with Dashboard payroll period: 21st–20th)
- Import into Dashboard: Before generating monthly penalty report
- File format: Excel (.xlsx)

### Task 3.2 — Leave Code Mapping

Map iTalent leave type names to Dashboard status codes:

| iTalent Leave Type | Dashboard Status Code |
|---|---|
| Annual Leave | AL |
| Casual Leave | CL |
| Sick Leave | SL |
| Unpaid Leave | UL |
| Maternity Leave | ML |
| Paternity Leave | PL |
| Marriage Leave | MAL |
| Bereavement Leave | BL |
| Miscarriage Leave | MCL |

> ⚠️ **Action Required:** Confirm these codes match what is currently used in the Dashboard's leave sheet. Update the Dashboard's leave type recognition logic if codes differ.

---

## Phase 4: Employee Self-Service Configuration

> **Goal:** Enable employees to use iTalent ESS effectively.

### Task 4.1 — Configure ESS Portal for Employees

**Sections to activate and verify:**

| ESS Section | Sub-items | Action |
|---|---|---|
| **My Approval** | Pending, Processed, Applied | ✅ Already configured |
| **My Attendance** | Leave Application, Overtime Application, My Business Trips, Business Trip (Local) | Verify Overtime form fields match policy |
| **Self-Service Application** | Issue Certificate, Personnel Application | Configure certificate types available |
| **Common Functions** | Leave Application, Business Travel shortcuts | ✅ Already visible |

### Task 4.2 — Configure Issue Certificate Types

Under Self-Service Application → Issue Certificate, configure the following certificate types:
- [ ] Employment Certificate (Arabic)
- [ ] Employment Certificate (English)
- [ ] Salary Certificate
- [ ] Experience Certificate (for resigned employees)

### Task 4.3 — Overtime Application Configuration

Configure Overtime Application form fields:
- [ ] Date of overtime
- [ ] Start time / End time
- [ ] Reason/project
- [ ] Approval: Direct Manager only
- [ ] Link to compensation policy (comp-off or paid)

---

## Phase 5: Notification & Communication Setup

> **Goal:** Automate notifications to align with current email-based process.

### Task 5.1 — Email Notification Rules

Configure iTalent to send emails for the following events:

| Event | Recipient | Email |
|---|---|---|
| New leave request submitted | Direct Manager | Manager's email |
| Leave approved | Employee + HR | hr.egy@51talk.com |
| Leave rejected | Employee | Employee email |
| Pending approval reminder (24hrs) | Manager | Manager's email |
| Leave request needs documentation | Employee | Employee email |

### Task 5.2 — HR Notification Setup

- [ ] CC hr.egy@51talk.com on all approved leave notifications
- [ ] Configure Just HR vendor contact: r.kandil@jhr-services.com
- [ ] Configure Migrate vendor contact: hrcrm@migratebusiness.com
- [ ] Set escalation: unapproved requests older than 48hrs escalate to Director

---

## Phase 6: Data Migration & Go-Live

> **Goal:** Import existing employee data and validate before going live.

### Task 6.1 — Employee Master Data Import

Import existing employee master data into iTalent. Required fields:

| Field | Source | iTalent Field |
|---|---|---|
| AC-No / PS ID | Attendance Dashboard master | Employee ID |
| CRM | Dashboard master | CRM |
| Name | Dashboard master | Name |
| Department | Dashboard master | Department |
| Join Date | HR records | Join Date (for annual leave entitlement calc) |
| Vendor | Dashboard master | Vendor (Just HR / Migrate) |
| National ID | HR records | National ID |

### Task 6.2 — Opening Balances

Set opening leave balances for all active employees:
- [ ] Annual Leave: Calculate remaining days based on join date and days used YTD
- [ ] Casual Leave: 7 days minus days used YTD
- [ ] Paternity: Remaining occurrences for current year

### Task 6.3 — Parallel Run (2 weeks)

Run iTalent alongside the existing email-based process for 2 weeks:
- Employees submit leaves in both systems
- HR validates iTalent approvals match email approvals
- Compare iTalent leave export vs manually maintained leave sheet
- Fix any discrepancies before cutover

### Task 6.4 — Go-Live Checklist

- [ ] All leave types named and configured
- [ ] Approval workflows assigned and tested
- [ ] All employees imported with correct balances
- [ ] Email notifications tested end-to-end
- [ ] Leave export format validated with Attendance Dashboard
- [ ] HR and manager training completed
- [ ] "Leave Applictaion" typo fixed in both menu locations
- [ ] Leave Item 6 and Leave Item 34 renamed
- [ ] Annual Leave entitlement rule set (15/21 days based on tenure)
- [ ] Announcement sent to all employees

---

## Phase 7: Ongoing Operations

### Monthly Workflow
```
1st–20th:    Employees submit leaves via iTalent ESS
21st:        HR exports approved leaves from iTalent
21st:        Import leave export into Attendance Dashboard
21st–25th:  Dashboard generates penalty report
30th:        Payroll processed (basic salary)
20th+1:     Commissions processed
```

### HR Tasks in iTalent
- Review Pending approvals daily (My Approval → Pending)
- Process Delegation: Update when managers are on leave
- Monthly: Export leave data for Dashboard
- Quarterly: Audit leave balances for accuracy

---

## Issues Found During Exploration

| # | Issue | Location | Priority |
|---|---|---|---|
| 1 | "Leave Applictaion" typo | My Attendance sidebar + Common Functions | High |
| 2 | "Leave Item 6" unnamed | Leave type dropdown | High |
| 3 | "Leave Item 34" unnamed | Leave type dropdown | High |
| 4 | Annual Leave shows 0 days | Leave entitlement config | High |
| 5 | No Casual Leave configured | Leave types | High |
| 6 | No Marriage Leave configured | Leave types | High |
| 7 | Overtime Application form — fields unknown | My Attendance | Medium |
| 8 | Certificate types not configured | Self-Service Application | Medium |

---

## Decisions Log — All Resolved ✅

| # | Question | Answer | Action |
|---|---|---|---|
| 1 | Approval chain — who are the managers? | To be added manually later | Skip pre-assignment; HR adds approvers per team post-pilot |
| 2 | Overtime policy? | **No overtime** | Disable Overtime Application in ESS |
| 3 | Annual Leave carryover? | **Allow carryover** | Configure iTalent to carry over unused annual leave (no hard cutoff) |
| 4 | Certificate types? | **HR Letter only** | Configure one certificate type in ESS |
| 5 | Pilot department? | **CC Team** | Stage 4 targets CC Team |
| 6 | Casual Leave vs Annual Leave deduction | Casual counts toward annual per handbook | Configure Casual Leave to deduct from Annual Leave balance |

---

*Plan generated: 2026-02-25 | System explored: 51talk.italent.cn | Based on: 51Talk Egypt Employee Handbook + Attendance Dashboard v2.2*
