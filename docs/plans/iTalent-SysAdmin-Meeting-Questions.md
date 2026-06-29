# iTalent System Admin Meeting — Questions & Requirements
**Prepared by:** Ahmed Elsadek — HRBP, 51Talk Egypt
**Date:** 2026-05-03
**Purpose:** Pre-implementation alignment on system capabilities, constraints, and configuration access

---

## How to Use This Sheet

| Priority | Meaning |
|---|---|
| 🔴 Blocker | Cannot proceed with implementation without this answer |
| 🟡 High | Needed before go-live |
| 🟢 Nice to Know | Useful but not blocking |

---

## Section 1: Reports & Data Export

> Our use case: Every 21st of the month, HR exports all approved leaves from iTalent and imports them into our Attendance Dashboard (Streamlit) to calculate salary deductions and penalties.

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 1.1 | Can we export approved leaves filtered by a custom date range (e.g., 21st–20th of each month)? | 🔴 Blocker | We need exact date range filtering — the export period is 21st of last month to 20th of current month, not a calendar month |
| 1.2 | What file formats are available for leave export? (Excel, CSV, PDF?) | 🔴 Blocker | We need Excel (.xlsx) — the Dashboard import only accepts Excel |
| 1.3 | Can we filter the export to show **Approved only** (exclude Pending and Rejected)? | 🔴 Blocker | If not possible, we'll need to filter manually — please confirm |
| 1.4 | What columns are included in the leave export? Can we choose/configure them? | 🔴 Blocker | We need at minimum: CRM, Date (one row per day), Leave Type, Status. Confirm if "CRM" is an exportable field |
| 1.5 | If an employee takes a 3-day leave, does the export show 3 separate rows (one per day) or one row for the full range? | 🔴 Blocker | We need one row per calendar day — the Dashboard processes daily attendance |
| 1.6 | Can we schedule an automatic export (e.g., auto-export on 21st of every month to an email or folder)? | 🟡 High | Preferred — reduces manual steps. If not available, manual export is acceptable |
| 1.7 | Is there a report showing leave balance per employee across all leave types? Can it be exported? | 🟡 High | Needed for quarterly balance audits |
| 1.8 | Can we build custom reports (e.g., leaves by department, by leave type, by date range)? | 🟡 High | Required for HR reporting to management |
| 1.9 | Is there a report showing approval turnaround time (submitted → approved)? | 🟢 Nice | We want to track if managers are approving within 24 hours |
| 1.10 | Can the export be run by a non-admin HR user, or does it require admin access? | 🟡 High | The person running monthly exports is HRBP, not IT admin — access level must be confirmed |

---

## Section 2: Abuse Prevention & Policy Controls

> Our concern: Employees may exploit leave without documentation, submit backdated leaves, or bypass limits.

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 2.1 | Can we enforce a **minimum advance notice** rule? (e.g., must submit at least 7 days before leave date) | 🔴 Blocker | Our policy: <3 days leave = 7 days notice. >2 days leave = 30 days notice. This must be system-enforced |
| 2.2 | Can we enforce a **maximum consecutive days** cap per leave type? (e.g., Casual Leave max 2 days per request) | 🔴 Blocker | Casual Leave is limited to 2 days per request per our policy |
| 2.3 | Can we set a **maximum annual cap** per leave type? (e.g., Casual Leave = 7 days/year total) | 🔴 Blocker | System must block submission when balance is exhausted |
| 2.4 | Can we require **mandatory document attachment** for specific leave types? (Sick, Marriage, Maternity, Bereavement) | 🔴 Blocker | System must block submission unless attachment is uploaded for these leave types |
| 2.5 | Can we prevent **backdated leave requests**? (e.g., block submission for a date that has already passed) | 🟡 High | Backdated leave is a common abuse vector — we want to control this or at minimum require HR approval |
| 2.6 | If a backdated leave is allowed, does it create an audit flag or require special approval? | 🟡 High | Recommend: backdated leaves auto-route to HR for review, not just direct manager |
| 2.7 | Can we set a **blackout period** (dates when leave submission is blocked)? e.g., peak business seasons | 🟡 High | Useful for call center peak periods — we may need to block Annual Leave in certain months |
| 2.8 | Can a manager **cancel** an already-approved leave? What is the process? | 🟡 High | Managers sometimes need to recall approvals — we need to understand if this is possible and if it notifies the employee |
| 2.9 | Can an employee **withdraw** a submitted or approved leave? Is there an audit trail? | 🟡 High | Employees sometimes withdraw requests — we need to confirm balance is restored correctly |
| 2.10 | Is there a **duplicate submission check**? (e.g., if an employee submits two leaves overlapping the same date) | 🟡 High | System should reject overlapping date submissions automatically |
| 2.11 | Can we track and report on employees who have **exhausted a specific leave type**? | 🟢 Nice | Helps HR proactively manage cases where employees have no remaining balance |

---

## Section 3: Access Control & User Management

> Our setup: We have ~2 vendors (Just HR / Migrate), multiple departments, and managers who must only see their own team.

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 3.1 | Can we create **role-based access** so managers only see their own team's leave requests? | 🔴 Blocker | A CC Team manager must not see Sales Team leave — data segregation is mandatory |
| 3.2 | How do we assign an employee's **direct manager** in the system? Is it per employee or per department? | 🔴 Blocker | We have employees with different managers within the same department — need per-employee assignment |
| 3.3 | Can we have **multiple admin accounts** with different permission levels? (e.g., full admin vs. HR-only admin) | 🟡 High | HR should be able to manage leaves and balances without touching system-level config |
| 3.4 | What happens when a manager **leaves or changes**? Can we reassign their team quickly? | 🟡 High | We have occasional manager changes — need a clean reassignment process |
| 3.5 | Can we configure **Process Delegation** (deputy manager) for when a manager is on leave? | 🔴 Blocker | Our workflow depends on this — if a manager is absent, approvals must route to their deputy |
| 3.6 | Is there an **employee self-registration** option, or does HR always create accounts? | 🟡 High | We prefer HR-controlled account creation to prevent unauthorized access |
| 3.7 | Can we **deactivate** (not delete) a resigned employee's account while retaining their historical data? | 🟡 High | We need historical leave records for payroll reconciliation — hard deletion is unacceptable |
| 3.8 | What is the **password policy**? Can we enforce complexity and expiry? | 🟢 Nice | Basic security hygiene — recommended minimum: 8 chars, expiry every 90 days |
| 3.9 | Is there **two-factor authentication (2FA)** available for admin accounts? | 🟢 Nice | Recommended for HR and admin accounts given they contain sensitive employee data |
| 3.10 | Can we see a **login activity log** — who logged in, when, from which device? | 🟢 Nice | Useful for detecting unauthorized access |

---

## Section 4: Leave Balance Management

> Our challenge: We are migrating mid-year. Employees already have used some leave in 2026 — we must import accurate opening balances.

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 4.1 | Can we perform a **bulk import of opening leave balances** via Excel? | 🔴 Blocker | We have ~100+ employees — manual entry per person is not feasible |
| 4.2 | Can we **manually adjust** an individual employee's leave balance after import? (e.g., correcting an error) | 🔴 Blocker | Errors will happen during migration — we need a quick correction path |
| 4.3 | Does the system **automatically calculate Annual Leave entitlement** based on join date? (15 days < 1yr / 21 days ≥ 1yr) | 🔴 Blocker | This is our exact policy — if not automatic, we will have to manage this manually for every new joiner |
| 4.4 | How does **annual leave carryover** work at year-end? Is there a cap on carried-over days? | 🔴 Blocker | Management confirmed carryover is allowed — we need the system to support this without forcing expiry |
| 4.5 | When is the **leave year reset**? (January 1? Employee anniversary date?) | 🟡 High | We need to know so we can set opening balances correctly during migration |
| 4.6 | If an employee's annual balance runs out, can they go into **negative balance** (borrow from future entitlement)? | 🟡 High | This sometimes happens — we need to define whether the system blocks it or allows with approval |
| 4.7 | Is there an automated **accrual** feature? (e.g., 1.25 days added per month instead of all at once on Jan 1) | 🟢 Nice | Not required immediately, but useful for future planning |
| 4.8 | Can we run a **balance reconciliation report** to compare system balances vs. our manual records? | 🟡 High | Needed during parallel run phase to validate data accuracy |

---

## Section 5: System Configuration & Customization

> Our concern: We found unnamed leave types, a typo in the menu, and unconfigured fields during our system exploration. We need to know our admin boundaries.

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 5.1 | Can **we** (HRBP/HR admin) rename leave types directly in the admin panel, or does this require a request to you? | 🔴 Blocker | We need to rename "Leave Item 6" → Casual Leave and "Leave Item 34" → Marriage Leave immediately |
| 5.2 | Can we fix the **"Leave Applictaion" typo** in the sidebar menu? Which admin section controls menu labels? | 🟡 High | This typo appears in 2 locations — looks unprofessional to employees |
| 5.3 | Can we **hide or disable** menu items that are not relevant to us? (e.g., Overtime Application — we have no overtime policy) | 🟡 High | We want to hide Overtime Application from all ESS users to avoid confusion |
| 5.4 | Can we configure **custom leave types** beyond what's currently visible in the system? | 🟡 High | We may need to add types in the future (e.g., Emergency Leave) without waiting for vendor support |
| 5.5 | What is the **difference between our admin access and your (sysadmin) access**? What can we NOT do ourselves? | 🔴 Blocker | We need a clear boundary — so we know when to contact you vs. handle it ourselves |
| 5.6 | Can we customize **email notification templates**? (Change the email subject/body text to match our company tone) | 🟢 Nice | Default templates may not be in Arabic or may not match our communication style |
| 5.7 | Is there a **sandbox/test environment** we can use to test changes before applying them to production? | 🟡 High | We want to test workflow configurations without risking live employee data |
| 5.8 | Can we configure the **ESS portal language** to Arabic for employees who prefer Arabic? | 🟡 High | 51Talk Egypt has Arabic-speaking staff — bilingual interface is important |

---

## Section 6: Notifications & Escalations

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 6.1 | Can we configure **email escalation** if a leave request is pending for more than 48 hours? | 🟡 High | We want unapproved requests older than 48hrs to auto-escalate to the team director |
| 6.2 | Can we configure a **daily digest email** for HR showing all pending approvals across the company? | 🟡 High | HR needs visibility into bottlenecks without logging in every hour |
| 6.3 | Does the system send **reminders to employees** if their leave is expiring? (e.g., "You have 5 Annual Leave days remaining — use by Dec 31") | 🟢 Nice | Reduces last-minute leave rushes at year-end |
| 6.4 | Can we send a **notification to HR** whenever a leave with a required document is submitted, so HR can verify the attachment? | 🟡 High | For Sick Leave and Maternity — HR needs to verify documentation before approval |
| 6.5 | Are notifications sent to the **employee's work email**? Can we also notify a personal email or phone (SMS/WhatsApp)? | 🟢 Nice | Some employees may not check work email — alternative channels are a plus |

---

## Section 7: Data Security & Compliance

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 7.1 | Is there an **audit trail** — a log of every change made in the system (who changed what, when)? | 🟡 High | Required for compliance — if a leave balance is changed, we need to know who did it |
| 7.2 | Where is the data **hosted**? Is it in Egypt, China, or elsewhere? Any data residency concerns? | 🟡 High | Sensitive employee data (National ID, salary info) — we need to understand data location |
| 7.3 | What is the **data backup policy**? How frequently are backups taken, and what is the recovery time? | 🟡 High | If the system goes down mid-month, we need to know our recovery options |
| 7.4 | Can we **export a full data backup** of all employee records and leave history on demand? | 🟡 High | We want to maintain an offline copy of employee data as a safety net |
| 7.5 | What is the **data retention policy**? How long is historical leave data kept after an employee leaves? | 🟡 High | Egyptian labor law may require keeping records for a minimum period |
| 7.6 | Does iTalent have a **GDPR or PDPL (Egypt Personal Data Protection Law)** compliance statement? | 🟢 Nice | Relevant if we are audited by Egyptian data protection authorities |

---

## Section 8: Support & SLA

| # | Question | Priority | Our Requirement / Recommendation |
|---|---|---|---|
| 8.1 | What is the **support response time** for critical issues (e.g., system down, employees can't log in)? | 🔴 Blocker | We need to know this before go-live — especially during payroll period (21st of each month) |
| 8.2 | What is the **maintenance/downtime schedule**? Are there planned outages? | 🟡 High | We cannot afford downtime on the 21st of each month — this is our export day |
| 8.3 | Who is our **primary point of contact** for configuration issues vs. technical bugs? | 🟡 High | We need separate escalation paths — HR config questions vs. IT system issues |
| 8.4 | Is there a **ticketing system or portal** for submitting support requests? | 🟡 High | Email-only support is not reliable for time-sensitive issues |
| 8.5 | How are **system updates or new features** communicated to us? Do we get advance notice before changes are deployed? | 🟢 Nice | System updates that change menu navigation or field names could break our processes |
| 8.6 | Is there **training documentation or a user manual** we can access and share with our HR team? | 🟡 High | We are preparing training materials — official documentation from iTalent would accelerate this |

---

## Quick Reference: Our Key Integration Requirements

These are the absolute minimum requirements for our Attendance Dashboard integration to work:

```
✅ Export must include: CRM | Date (per day) | Leave Type | Status
✅ Export format: Excel (.xlsx)
✅ Export filter: Approved leaves only
✅ Export date range: Custom (21st of prev month → 20th of current month)
✅ Leave type names must match exactly:
   Annual Leave | Casual Leave | Sick Leave | Unpaid Leave
   Maternity Leave | Paternity Leave | Marriage Leave
   Bereavement Leave | Miscarriage Leave
```

---

## Notes Column (To Fill During Meeting)

| # | Question # | Admin's Answer | Follow-up Action |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

---

*Document prepared by Ahmed Elsadek — HRBP, 51Talk Egypt | 2026-05-03*
