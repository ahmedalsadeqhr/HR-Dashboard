# Email: iTalent Implementation Plan — Full Package

---

**To:** [Manager Name]
**From:** Ahmed Elsadek — HRBP, 51Talk Egypt
**Date:** March 1, 2026
**Subject:** iTalent HR System — Full Implementation Plan for Your Review

---

Dear [Manager Name],

Following our recent discussion and your approval to proceed, I have finalized the complete implementation plan for transitioning our leave management and employee self-service processes to iTalent. Please find the full details below.

---

## 1. Background

The company has introduced iTalent as our new HR system. I have conducted a hands-on exploration of the live system and mapped its capabilities against our Employee Handbook and existing Attendance Dashboard. The plan below details exactly how we will configure the system, transition employees, and go live.

---

## 2. Current Situation vs. Target State

| Area | Current | After iTalent |
|---|---|---|
| Leave requests | Email to manager + hr.egy@51talk.com | Digital submission via iTalent ESS portal |
| Approval tracking | No system — email threads | Full audit trail in iTalent |
| Leave balance visibility | HR-managed only | Employees see real-time balance |
| Leave data for payroll | Manual leave sheet (Excel) | Auto-exported from iTalent on 21st monthly |
| Approval enforcement | Honor-based | Configurable multi-level workflows |

---

## 3. What Is Already in the System

After a live review of iTalent (51talk.italent.cn):

**✅ Already configured:**
- 7 leave types (Sick, Annual, Unpaid, Maternity, Paternity, Bereavement, Miscarriage)
- Employee Self-Service portal with My Approval, My Attendance, My Profile
- Batch approval and Process Delegation for managers

**⚠️ Requires configuration before go-live:**
- 2 leave types unnamed (will be set as Casual Leave & Marriage Leave)
- Annual Leave entitlement showing 0 days — needs rule setup
- Approval workflows not yet assigned per leave type
- Email notifications not configured
- Employee data not yet imported

---

## 4. Your Confirmed Decisions (Already Incorporated)

| Decision | Your Answer |
|---|---|
| Pilot department | **CC Team** |
| Approval chain setup | **Add manually later** |
| Overtime | **No overtime policy** — feature will be disabled |
| Annual Leave carryover | **Allow carryover** |
| Issue Certificate types | **HR Letter only** |

---

## 5. Implementation Plan — 7 Phases

| Phase | What | Duration |
|---|---|---|
| **0 — Prerequisites** | Admin access, employee data backup, CC Team manager briefed | 2–3 days |
| **1 — Leave Configuration** | Fix leave types, set entitlements per handbook, configure carryover | Week 1 |
| **2 — Approval Workflows** | Build approval chains per leave type, set notification rules | Week 1 |
| **3 — Dashboard Integration** | Connect iTalent leave export to Attendance Dashboard | Week 2 |
| **4 — ESS Configuration** | HR Letter certificate, disable overtime, configure business trips | Week 2 |
| **5 — Notifications** | Email alerts for managers, employees, and HR on all leave events | Week 2 |
| **6 — Pilot + Full Rollout** | CC Team pilot → evaluate → company-wide rollout | Week 3–6 |
| **7 — Operations** | Monthly export-import cycle, balance management | Month 2+ |

---

## 6. Rollout Strategy

```
Week 1–2:   Configure & integrate
Week 3:     CC Team pilot goes live (parallel with email process)
Week 4:     Review pilot, fix any gaps
Week 5–6:   Full company rollout + training sessions
End Week 6: Email-based leave process retired
Month 2+:   Full operations on iTalent
```

**No risk to employees during transition:**
- Email-based process stays active during the pilot and parallel run
- No employee will lose a leave request during the switch
- Opening leave balances will be imported before anyone can see their account

---

## 7. Leave Types & Entitlements (Per Handbook)

| Leave Type | Days | Pay | Key Rule |
|---|---|---|---|
| Annual Leave | 15 (<1yr) / 21 (≥1yr) | Full | Carryover allowed |
| Casual Leave | 7/year, max 2/request | Full | Counts toward annual balance |
| Sick Leave | As needed | 75% | Doctor's note required |
| Maternity Leave | 120 days | Full | After 1yr service, birth cert required |
| Paternity Leave | 1 day × max 3/year | Full | Proof required |
| Marriage Leave | 3 days | Full | Proof required |
| Bereavement Leave | 3 days | Full | Parents/spouse/children only |
| Miscarriage Leave | Per labor law | Full | Medical documentation required |
| Unpaid Leave | As approved | 0% | Manager + HR dual approval |

---

## 8. Risks & How We're Managing Them

| Risk | Mitigation |
|---|---|
| Employees don't adopt the system | Training sessions + Arabic/English quick-start guide |
| Data mismatch with Attendance Dashboard | 2-week parallel run before cutover |
| Manager approval delays | Process Delegation configured for all managers |
| Leave history lost | Opening balances imported before any employee accesses the system |
| System downtime | Backup: revert to email process temporarily |

---

## 9. What I Still Need From You

- [ ] **Pilot kickoff date** — When should CC Team go live on iTalent?
- [ ] **IT system admin contact** — I need to submit an admin access request to start configuration

---

## 10. Attached Documents

| Document | Purpose |
|---|---|
| `iTalent-Execution-Rollout-Plan.md` | Full step-by-step transition plan with checklists |
| `2026-02-25-italent-implementation-plan.md` | Technical configuration details per phase |

---

Please let me know if you have any questions or would like to discuss any part of the plan.

Best regards,
Ahmed Elsadek
HRBP — 51Talk Egypt
hr.egy@51talk.com
