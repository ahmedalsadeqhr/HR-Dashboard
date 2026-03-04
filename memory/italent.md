# iTalent HR System — 51Talk Egypt

## Portal
- URL: 51talk.italent.cn
- Modules: ESS (Employee Self-Service), Leave Management, Attendance, My Approval

## Architecture
- iframe-based navigation
- Leave form has 34 form elements

## Confirmed Configuration Decisions
| Question | Decision |
|---|---|
| Pilot department | CC Team |
| Overtime applications | Disabled (no overtime policy) |
| Annual leave carryover | Allowed (no hard cutoff) |
| Issue Certificate type | HR Letter only |
| Approval chains | Manual setup at a later stage |

## Leave Types (existing in system)
- 7 leave types configured
- 2 unnamed placeholders need renaming
- Annual leave entitlement needs setup

## Implementation Phases
1. Stage 0: Prerequisites (admin access, data backup)
2. Stage 1: System configuration (leave types, approval workflows, notifications)
3. Stage 2: Dashboard integration (monthly leave exports → Attendance Dashboard)
4. Stage 3: Data migration (employee master data, opening leave balances)
5. Stage 4: CC Team pilot (at least 3 leave requests, validate full workflow)
6. Stage 5: Full rollout (2-week parallel run with email process)
7. Stage 6: Email process retirement, ongoing operations

## Leave Balance Rules (for import)
- < 1 year tenure: 15 days annual leave
- ≥ 1 year tenure: 21 days annual leave

## Plans & Documents
- `docs/plans/2026-02-25-italent-implementation-plan.md`
- `docs/plans/iTalent-Execution-Rollout-Plan.md`
- `docs/plans/iTalent-Manager-Approval-Brief.md`
- `docs/plans/Email-To-Manager-Full-Plan.md`
- `docs/plans/Email-To-SysAdmin-Access-Request.md`
- Screenshots: `italent_screenshots/`
