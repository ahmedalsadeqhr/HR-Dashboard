# iTalent Execution & Rollout Plan — 51Talk Egypt

**Version:** 1.0
**Date:** February 25, 2026
**Owner:** Ahmed Elsadek — HRBP

---

## Overview

This document defines the step-by-step execution plan for transitioning 51Talk Egypt from the current email-based leave management process to the iTalent HR system. It covers the pilot trial, employee migration, training, cutover, and ongoing operations.

---

## Management Decisions — Confirmed ✅

| Decision | Answer | Impact on Plan |
|---|---|---|
| Pilot department | **CC Team** | Stage 4 targets CC Team |
| Approval chain setup | **Add manually later** | Skip workflow pre-assignment; managers added post-pilot |
| Overtime policy | **No overtime** | Overtime Application will be hidden/disabled in ESS |
| Annual Leave carryover | **Allow carryover** | iTalent configured to carry over unused annual leave |
| Issue Certificate types | **HR Letter only** | Only one certificate type configured in ESS |

---

## Guiding Principles

1. **No big bang** — Pilot first, fix issues, then expand
2. **No data loss** — All historical leave balances imported before go-live
3. **No disruption** — Parallel run ensures employees are never left without a process
4. **No surprises** — Employees and managers trained before they see the system

---

## Timeline Overview

```
Week 1         Week 2         Week 3         Week 4         Week 5-6       Month 2+
|--------------|--------------|--------------|--------------|--------------|---------->
  Configure      Integrate      Pilot Dept    Evaluate &     Full Company   Operations
  & Setup        & Notify       Go-Live       Fix Gaps       Rollout
```

---

## Stage 0: Prerequisites (Before Any Configuration)

**Owner:** HRBP + IT/System Admin
**Duration:** 2–3 days

### Checklist
- [ ] Confirm iTalent admin access (ability to configure leave types, workflows, users)
- [ ] Export current employee master data from Attendance Dashboard
- [ ] Collect org chart / reporting lines for all teams
- [ ] Get answer on 5 open questions from manager (see Manager Brief)
- [ ] Pilot department confirmed: **CC Team** ✅
- [ ] Get list of all manager email addresses for approval chain setup
- [ ] Backup current leave sheet used in Attendance Dashboard

### Deliverables
- [ ] Admin credentials confirmed
- [ ] Employee master data Excel file ready
- [ ] Org chart with reporting lines documented
- [ ] Pilot department confirmed and pilot manager briefed

---

## Stage 1: System Configuration (Week 1)

**Owner:** HRBP
**Duration:** 5 days

### 1A — Fix Leave Types (Day 1–2)

| Action | In iTalent | Expected Result |
|---|---|---|
| Rename "Leave Item 6" | Admin → Attendance → Leave Config | Name becomes "Casual Leave" |
| Rename "Leave Item 34" | Admin → Attendance → Leave Config | Name becomes "Marriage Leave" |
| Fix "Leave Applictaion" typo | Admin → Menu Config (2 locations) | Correct spelling in sidebar |
| Set Annual Leave entitlement | Leave Config → Annual Leave → Balance Rule | 15 days (<1yr) / 21 days (≥1yr) |
| Set Casual Leave rules | Leave Config → Casual Leave | Max 7 days/year, max 2 days/request |
| Set Sick Leave pay rate | Leave Config → Sick Leave | 75% salary, attachment required |
| Set Maternity Leave | Leave Config → Maternity | 120 days, 1yr service required |
| Set Paternity Leave | Leave Config → Paternity | 3 occurrences max, 1 day each |
| Set Marriage Leave | Leave Config → Marriage | 3 days, attachment required |
| Set Bereavement Leave | Leave Config → Bereavement | 3 days, parents/spouse/children only |
| Set Unpaid Leave | Leave Config → Unpaid | No limit, dual approval |

**Verification:** Open Leave Application form → click "Leave Project" dropdown → confirm all 9 types appear with correct names

---

### 1B — Configure Approval Workflows (Day 2–3)

Create these 3 workflow templates:

**Workflow A: "Single Approval" (Manager only)**
- Used for: Casual Leave, Paternity Leave, Bereavement Leave, Business Trips

**Workflow B: "HR Reviewed" (Manager → HR)**
- Used for: Sick Leave, Maternity Leave, Marriage Leave, Miscarriage Leave

**Workflow C: "Full Chain" (Manager → Director → HR)**
- Used for: Annual Leave > 3 days, Unpaid Leave

**Submission Restrictions to Configure:**
- Leave < 3 days: Block submission if notice < 7 days from today
- Leave > 2 days: Block submission if notice < 30 days from today

**Process Delegation Rule:**
- All managers must have a designated deputy
- Deputy receives approvals when manager is on leave
- Configure under: Admin → Workflow → Delegation Rules

**Verification:**
- [ ] Submit test leave request as employee → confirm correct approver receives notification
- [ ] Test delegation: set manager as "on leave" → confirm deputy receives request

---

### 1C — Configure Notifications (Day 4)

| Trigger | Recipient | Method |
|---|---|---|
| New leave submitted | Direct Manager | Email |
| Leave approved | Employee + HR | Email |
| Leave rejected | Employee | Email |
| Pending > 24 hrs no action | Manager | Email reminder |
| Leave needs documentation | Employee | Email |

- [ ] Set HR notification email: hr.egy@51talk.com
- [ ] Set escalation rule: pending > 48 hrs → notify Director

---

### 1D — Configure ESS Portal (Day 5)

- [ ] Issue Certificate: Configure **HR Letter only** (confirmed by management)
- [ ] Overtime Application: **Disable/hide** — no overtime policy (confirmed by management)
- [ ] Personnel Application: Verify form fields match HR requirements
- [ ] Business Trip (Local): Configure per company travel policy
- [ ] I Need a Business Travel: Configure for international/external travel

**Stage 1 Sign-off Criteria:**
- All leave types correctly named and configured
- All approval workflows assigned to leave types
- Test leave submission completes full workflow end-to-end
- ESS portal sections fully accessible

---

## Stage 2: Integration Setup (Week 2)

**Owner:** HRBP + Attendance Dashboard owner
**Duration:** 3 days

### 2A — iTalent Leave Export Configuration (Day 1)

Configure iTalent to export approved leaves in this format:

```
| CRM | Date | Leave Type | Status |
|-----|------|------------|--------|
| 12345 | 2026-03-01 | Annual Leave | Approved |
```

- Export format: Excel (.xlsx)
- Export trigger: Manual (HR runs on 21st of each month)
- Filter: Approved only (exclude pending/rejected)
- Date range: 21st previous month → 20th current month

### 2B — Dashboard Import Validation (Day 2)

Test the export-import flow:
1. Export sample leave data from iTalent
2. Import into Attendance Dashboard leave sheet
3. Run Dashboard report and verify leave days are correctly excluded from penalties
4. Confirm leave type codes match Dashboard recognition logic

**Leave Code Mapping to Verify:**
| iTalent Name | Dashboard Code | Action if Missing |
|---|---|---|
| Annual Leave | AL | Add to Dashboard |
| Casual Leave | CL | Add to Dashboard |
| Sick Leave | SL | Add to Dashboard |
| Unpaid Leave | UL | Add to Dashboard |
| Maternity Leave | ML | Add to Dashboard |
| Paternity Leave | PL | Add to Dashboard |
| Marriage Leave | MAL | Add to Dashboard |
| Bereavement Leave | BL | Add to Dashboard |
| Miscarriage Leave | MCL | Add to Dashboard |

### 2C — Monthly Operations SOP (Day 3)

Document and distribute the monthly HR operations procedure:

```
MONTHLY LEAVE PROCESSING PROCEDURE
===================================
21st of each month:
  1. HR logs into iTalent → Reports → Leave Export
  2. Set date range: [21st prev month] to [20th current month]
  3. Filter: Approved leaves only
  4. Export as Excel
  5. Open Attendance Dashboard (Streamlit)
  6. Upload the export as the leave sheet
  7. Process attendance report as normal
  8. Generate penalties report
```

**Stage 2 Sign-off Criteria:**
- Export-import test successful with no data loss
- All leave codes recognized by Dashboard
- Monthly SOP documented and tested

---

## Stage 3: Employee Data Migration (Week 2, parallel with Stage 2)

**Owner:** HRBP
**Duration:** 2–3 days

### 3A — Prepare Master Data Import File

Collect from Attendance Dashboard master data + HR records:

| Field | Source |
|---|---|
| Employee ID (AC-No / PS ID) | Attendance Dashboard |
| CRM | Attendance Dashboard |
| Full Name | Attendance Dashboard |
| Department | Attendance Dashboard |
| Join Date | HR records (critical for annual leave calc) |
| Vendor | Attendance Dashboard (Just HR / Migrate) |
| National ID | HR records |
| Manager/Approver | Org chart |
| Email Address | Company directory |

### 3B — Calculate Opening Leave Balances

For each employee, calculate remaining leave balances as of go-live date:

**Annual Leave:**
```
If tenure < 1 year:  Opening balance = 15 - days_used_YTD
If tenure ≥ 1 year:  Opening balance = 21 - days_used_YTD
```

**Casual Leave:**
```
Opening balance = 7 - days_used_YTD
```

**Paternity Leave:**
```
Opening occurrences = 3 - occurrences_used_YTD
```

### 3C — Import & Verify

- [ ] Import master data into iTalent
- [ ] Verify employee count matches HR records
- [ ] Verify opening balances for 5 sample employees
- [ ] Confirm each employee has correct manager assigned

**Stage 3 Sign-off Criteria:**
- 100% of active employees imported
- Opening balances verified for all leave types
- Manager assignments confirmed for all employees

---

## Stage 4: Pilot — One Department (Week 3)

**Owner:** HRBP + Pilot Department Manager
**Duration:** 1 week

### Why Pilot First?
- Catch configuration issues before they affect all employees
- Build internal champions who can help train others
- Validate the full workflow end-to-end in real conditions
- Low risk: only 1 team affected

### Pilot Department
**CC Team** — confirmed by management ✅

### Pilot Week Schedule

**Day 1 (Monday) — Kickoff:**
- Brief pilot manager on system
- Share employee quick-start guide
- Enable pilot department in iTalent

**Day 2–3 — Live Usage:**
- Employees submit any pending leave requests via iTalent
- Manager approves/rejects via My Approval
- HRBP monitors for issues

**Day 4 — Mid-Pilot Check:**
- HRBP reviews all submitted requests
- Check: notifications sent? approvals working? balances updated?
- Fix any issues found

**Day 5 (Friday) — Pilot Review:**
- HRBP + Pilot Manager debrief
- Document all issues found
- Decision: Go/No-Go for full rollout

### Pilot Monitoring Checklist
- [ ] At least 3 leave requests submitted and approved
- [ ] Email notifications received by manager and employee
- [ ] Leave balance correctly deducted after approval
- [ ] Leave export includes pilot leaves correctly
- [ ] No errors in Dashboard after importing pilot leaves
- [ ] Employees found the portal easy to use (quick survey)

---

## Stage 5: Fix & Adjust (Week 4)

**Owner:** HRBP
**Duration:** 3–5 days

Based on pilot findings:
- Fix any configuration issues
- Update user guides if needed
- Adjust notification wording if unclear
- Resolve any Dashboard integration issues

**Go/No-Go Decision:**
- All pilot monitoring criteria met → **Go for full rollout**
- Any critical issue unresolved → **Extend pilot by 1 week**

---

## Stage 6: Full Company Rollout (Week 5–6)

**Owner:** HRBP
**Duration:** 2 weeks

### Training Sessions

| Session | Audience | Duration | Content |
|---|---|---|---|
| Manager Training | All team managers | 1 hour | My Approval, Process Delegation, Batch Approval |
| Employee Training | All staff | 30 min | Leave Application, My Attendance, My Profile |
| HR Operations | HR team | 1 hour | Monthly export process, balance management, reports |

**Training Materials to Prepare:**
- [ ] Employee quick-start guide (PDF, Arabic + English)
- [ ] Manager approval guide (PDF)
- [ ] HR monthly operations SOP (Word doc)
- [ ] FAQ document (top 10 expected questions)

### Rollout Schedule

**Week 5:**
- Day 1: Training sessions for all managers
- Day 2–3: Training sessions for all employees (by department)
- Day 4–5: Employees begin submitting leaves in iTalent (email process still active)

**Week 6:**
- Days 1–5: Parallel run (both email + iTalent active)
- Day 5: Final verification of all active requests in system

**Parallel Run Rules:**
- Employees submit leaves in **both** email and iTalent
- HR approves in both systems
- At end of week 6: compare both logs for consistency

---

## Stage 7: Cutover — Email Process Retired (End of Week 6)

**Cutover Checklist:**
- [ ] All pending leave requests migrated to iTalent
- [ ] Managers notified: email submissions no longer accepted
- [ ] Announcement sent to all employees
- [ ] HR email auto-reply updated: "Please submit all leave requests via iTalent ESS portal"
- [ ] Old leave sheet archived (kept for reference, not updated further)

**Cutover Announcement Template:**
```
Subject: Leave Requests Now via iTalent — Effective [Date]

Team,

Starting [date], all leave requests must be submitted through the iTalent
Employee Self-Service portal at https://51talk.italent.cn.

Email-based leave requests will no longer be accepted.

If you need help accessing the portal, please contact hr.egy@51talk.com.

Thank you,
HR Team
```

---

## What Could Go Wrong — Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Employees don't know how to use the system | High | Medium | Training + quick-start guide + HR support |
| Manager approval bottleneck | Medium | High | Process Delegation configured; 48hr escalation |
| Leave balance errors at import | Medium | High | Verify 5 sample employees before import |
| Dashboard not recognizing iTalent leave codes | Low | High | Test export-import before pilot starts |
| Employee not in iTalent system | Low | Medium | Full audit of employee list before go-live |
| Manager rejects system adoption | Low | High | Escalate to Director; demo system value |
| System downtime during critical period | Low | Medium | Backup: revert to email process temporarily |

---

## What Will Be Missing / Not Covered by iTalent

These areas are **outside iTalent scope** and require separate handling:

| Area | Current Process | Recommendation |
|---|---|---|
| Fingerprint attendance data | Captured by physical device, exported manually | Continue as-is; iTalent only receives approved leaves |
| Penalty calculation | Attendance Dashboard Streamlit | Continue as-is; iTalent feeds leaves, Dashboard calculates penalties |
| Payroll processing | Manual (Just HR/Odoo + Migrate/ZenHR) | No change; penalty report from Dashboard feeds payroll |
| Medical insurance claims | GlobeMed Egypt (direct) | No change; iTalent does not manage insurance |
| Social insurance | Shared contribution | No change |
| Commission calculation | Separate process | No change |
| Disciplinary records | HR-managed | Consider adding to iTalent Personnel Application later |

---

## Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Leave request submission via iTalent | 100% within 4 weeks of cutover | Count of email requests received after cutover |
| Approval turnaround time | < 24 hours | iTalent approval timestamps |
| Leave data accuracy in Dashboard | 0 discrepancies | Compare iTalent export vs old leave sheet |
| Employee satisfaction with ESS | > 80% positive | Short survey after 1 month |
| HR time saved on leave admin | > 2 hours/week | HR self-reported |

---

## Document Index

| Document | Purpose | Location |
|---|---|---|
| Manager Approval Brief | Seek management sign-off | `docs/plans/iTalent-Manager-Approval-Brief.md` |
| Technical Implementation Plan | Detailed configuration steps | `docs/plans/2026-02-25-italent-implementation-plan.md` |
| Execution & Rollout Plan (this doc) | Transition strategy | `docs/plans/iTalent-Execution-Rollout-Plan.md` |
| Employee Quick-Start Guide | To be created | `docs/training/employee-guide.pdf` |
| Manager Approval Guide | To be created | `docs/training/manager-guide.pdf` |
| Monthly HR Operations SOP | To be created | `docs/sop/monthly-leave-process.md` |

---

*Execution Plan v1.0 | 51Talk Egypt HRBP | February 25, 2026*
