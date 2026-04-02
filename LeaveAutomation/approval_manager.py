import json
import os
from datetime import date
from email_parser import LeaveRequest

PENDING_FILE = os.path.join(os.path.dirname(__file__), "pending_requests.json")


def _load_pending():
    """Load pending requests from JSON file."""
    if not os.path.exists(PENDING_FILE):
        return []
    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [LeaveRequest.from_dict(d) for d in data]


def _save_pending(requests):
    """Save pending requests to JSON file."""
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in requests], f, indent=2, default=str)


def add_pending(requests):
    """Add new parsed requests to the pending queue."""
    existing = _load_pending()
    # Avoid duplicates by message_id
    existing_ids = {r.message_id for r in existing if r.message_id}
    new_count = 0
    for req in requests:
        if req.message_id and req.message_id in existing_ids:
            continue
        existing.append(req)
        new_count += 1
    _save_pending(existing)
    return new_count


def get_pending():
    """Get all pending requests."""
    return _load_pending()


def remove_pending(message_id):
    """Remove a request from the pending queue by message_id."""
    pending = _load_pending()
    pending = [r for r in pending if r.message_id != message_id]
    _save_pending(pending)


def display_pending():
    """Display pending requests in a formatted table."""
    pending = _load_pending()
    if not pending:
        print("\n  No pending leave requests.\n")
        return []

    print(f"\n  {'#':<4} {'Employee':<25} {'Leave Type':<22} {'Dates':<25} {'Conf':<6}")
    print(f"  {'─'*4} {'─'*25} {'─'*22} {'─'*25} {'─'*6}")

    for i, req in enumerate(pending, 1):
        dates = ""
        if req.start_date:
            dates = req.start_date.strftime("%d-%b-%Y")
            if req.end_date and req.end_date != req.start_date:
                dates += f" → {req.end_date.strftime('%d-%b-%Y')}"
        else:
            dates = "N/A"

        conf_marker = ""
        if req.confidence < 0.5:
            conf_marker = " ⚠"
        elif req.confidence < 0.7:
            conf_marker = " ?"

        print(f"  {i:<4} {req.employee_name:<25} {req.leave_type:<22} {dates:<25} {req.confidence:.0%}{conf_marker}")

    print(f"\n  Total: {len(pending)} pending request(s)\n")
    return pending


def review_request(req):
    """Interactive review of a single request. Returns ('approved'|'rejected'|'skip', modified_request, reason)."""
    print(f"\n  ┌─ Leave Request Details ─────────────────────────")
    print(f"  │ Employee:   {req.employee_name}")
    print(f"  │ Sender:     {req.sender}")
    print(f"  │ Leave Type: {req.leave_type}")
    print(f"  │ Start Date: {req.start_date or 'N/A'}")
    print(f"  │ End Date:   {req.end_date or 'N/A'}")
    print(f"  │ Reason:     {req.reason or 'N/A'}")
    print(f"  │ Confidence: {req.confidence:.0%}")
    print(f"  │ Subject:    {req.subject}")
    print(f"  └──────────────────────────────────────────────────")

    if req.confidence < 0.5:
        print("  ⚠  Low confidence parse — review carefully!")

    print("\n  Actions: [A]pprove  [R]eject  [E]dit  [S]kip")
    action = input("  > ").strip().lower()

    if action == "a":
        return "approved", req, ""

    elif action == "r":
        reason = input("  Rejection reason: ").strip()
        return "rejected", req, reason

    elif action == "e":
        req = _edit_request(req)
        # After editing, ask again
        return review_request(req)

    else:
        return "skip", req, ""


def _edit_request(req):
    """Allow manual editing of parsed fields."""
    print("\n  Edit fields (press Enter to keep current value):")

    name = input(f"  Employee name [{req.employee_name}]: ").strip()
    if name:
        req.employee_name = name

    lt = input(f"  Leave type [{req.leave_type}]: ").strip()
    if lt:
        from leave_types import match_leave_type
        matched, conf = match_leave_type(lt)
        if matched and conf > 0.5:
            req.leave_type = matched
            print(f"  → Matched to: {matched}")
        else:
            req.leave_type = lt

    sd = input(f"  Start date [{req.start_date}] (DD-MM-YYYY): ").strip()
    if sd:
        from dateutil import parser as dp
        try:
            req.start_date = dp.parse(sd, dayfirst=True).date()
        except ValueError:
            print("  Invalid date, keeping original.")

    ed = input(f"  End date [{req.end_date}] (DD-MM-YYYY): ").strip()
    if ed:
        from dateutil import parser as dp
        try:
            req.end_date = dp.parse(ed, dayfirst=True).date()
        except ValueError:
            print("  Invalid date, keeping original.")

    req.confidence = 1.0  # Manual review = full confidence
    return req
