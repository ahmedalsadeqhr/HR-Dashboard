# iTalent HR System Implementation — Manager Approval Brief

**To:** [Manager Name]
**From:** Ahmed Elsadek — HRBP, 51Talk Egypt
**Date:** February 25, 2026
**Subject:** iTalent HR System Implementation Plan — Approval Request

---

## Executive Summary

We have completed a full exploration and assessment of the company's newly introduced iTalent HR system. Based on a live review of the system and a detailed mapping against the 51Talk Egypt Employee Handbook and our existing Attendance Dashboard, I have developed a structured implementation plan to transition leave management and employee self-service to iTalent.

I am requesting your approval to proceed with a **phased rollout**, starting with a pilot on one department before company-wide deployment.

---

## Why We Are Implementing iTalent

| Current Pain Point | iTalent Solution |
|---|---|
| Leave requests submitted by email — no tracking | Digital leave submission with full audit trail |
| Manual leave sheet maintained by HR | Approved leaves auto-logged and exportable |
| No visibility for employees on leave balance | ESS portal shows real-time balance |
| Approval chain not enforced — risk of unauthorized leaves | Configurable multi-level approval workflows |
| HR manually reconciles leave data with attendance | Automated export feeds directly into Attendance Dashboard |

---

## What We Found in the System

After a hands-on exploration of the live iTalent system (51talk.italent.cn), here is the current configuration status:

**✅ Already Configured:**
- 7 leave types present (Sick, Unpaid, Annual, Maternity, Paternity, Bereavement, Miscarriage)
- Employee Self-Service portal (My Approval, My Attendance, My Profile)
- Batch approval and Process Delegation tools for managers
- Business Trip and Overtime application forms

**⚠️ Needs Configuration Before Go-Live:**
- 2 unnamed leave types need to be set up (Casual Leave & Marriage Leave)
- Annual Leave entitlement not yet configured (currently showing 0 days)
- Approval chains per leave type not yet assigned
- Notification rules not configured
- Employee master data not yet imported

---

## Implementation Plan — 7 Phases

| Phase | What | When |
|---|---|---|
| 1 | Fix & configure all leave types per handbook | Week 1 |
| 2 | Set up approval workflows per leave type | Week 1 |
| 3 | Connect iTalent leave export to Attendance Dashboard | Week 2 |
| 4 | Configure Employee Self-Service features | Week 2 |
| 5 | Set up email notifications & escalation rules | Week 2 |
| 6 | Pilot with 1 department → full rollout | Week 3–6 |
| 7 | Ongoing monthly operations workflow | Month 2+ |

---

## Rollout Strategy

We will **not** go live company-wide immediately. The plan is:

1. **Week 3:** Pilot with **CC Team** (confirmed by management)
2. **Week 4:** Evaluate pilot results, fix any gaps
3. **Week 5–6:** Full company rollout with training sessions
4. **Month 2:** Full operations on iTalent; Attendance Dashboard fed from iTalent exports

During the pilot, both the old email-based process and iTalent will run in parallel — no risk of lost requests.

---

## Manager Decisions — Confirmed ✅

All key decisions have been received and incorporated into the plan:

| # | Question | Answer |
|---|---|---|
| 1 | Which department should be the pilot? | **CC Team** |
| 2 | Who is the approver chain for each team? | **To be added manually later** |
| 3 | Is overtime compensated as comp-off or paid? | **No overtime policy** — Overtime Application will be disabled |
| 4 | Should unused Annual Leave lapse at year-end? | **Allow carryover** — no hard cutoff |
| 5 | What certificate types for Issue Certificate? | **HR Letter only** |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Employees not adopting the system | Training sessions + user guide before go-live |
| Data mismatch between iTalent and Dashboard | 2-week parallel run before cutover |
| Approval bottleneck if manager is on leave | Process Delegation configured for all managers |
| Leave history lost during transition | Opening balances imported before go-live |

---

## What I Need From You

- [x] **Approval to proceed** — ✅ Confirmed
- [x] **Answers to the 5 questions** — ✅ All received
- [ ] **Org chart / reporting lines** — To be provided later (approval chains will be added manually)
- [ ] Suggested date for **CC Team pilot kickoff**

---

## Attached

- Full Technical Implementation Plan: `docs/plans/2026-02-25-italent-implementation-plan.md`
- Execution & Transition Plan: `docs/plans/iTalent-Execution-Rollout-Plan.md`

---

*For questions, contact: Ahmed Elsadek | hr.egy@51talk.com*
