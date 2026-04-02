import re
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
from leave_types import match_leave_type


class LeaveRequest:
    def __init__(self, **kwargs):
        self.employee_name = kwargs.get("employee_name", "")
        self.leave_type = kwargs.get("leave_type", "")
        self.start_date = kwargs.get("start_date")  # datetime.date
        self.end_date = kwargs.get("end_date")  # datetime.date
        self.reason = kwargs.get("reason", "")
        self.confidence = kwargs.get("confidence", 0.0)
        self.sender = kwargs.get("sender", "")
        self.sender_name = kwargs.get("sender_name", "")
        self.subject = kwargs.get("subject", "")
        self.message_id = kwargs.get("message_id", "")
        self.uid = kwargs.get("uid")
        self.raw_body = kwargs.get("raw_body", "")

    def to_dict(self):
        return {
            "employee_name": self.employee_name,
            "leave_type": self.leave_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "reason": self.reason,
            "confidence": self.confidence,
            "sender": self.sender,
            "sender_name": self.sender_name,
            "subject": self.subject,
            "message_id": self.message_id,
            "uid": self.uid,
            "raw_body": self.raw_body,
        }

    @classmethod
    def from_dict(cls, d):
        from datetime import date
        obj = cls(**d)
        if isinstance(obj.start_date, str):
            obj.start_date = date.fromisoformat(obj.start_date)
        if isinstance(obj.end_date, str):
            obj.end_date = date.fromisoformat(obj.end_date)
        return obj

    def date_range(self):
        """Return list of dates from start_date to end_date inclusive."""
        if not self.start_date:
            return []
        end = self.end_date or self.start_date
        days = (end - self.start_date).days + 1
        return [self.start_date + timedelta(days=i) for i in range(days)]


def _extract_name(sender_name, body):
    """Extract employee name from email sender or body."""
    # Try sender display name first (only if it looks like a real name with spaces)
    if sender_name and " " in sender_name and not re.match(r"^[\w.]+@", sender_name):
        return sender_name.strip(), 0.8

    # Look for common patterns in body
    patterns = [
        r"(?:my name is|i am|this is)\s+([A-Z][a-z]+(?:\s+[A-Za-z]+)+)",
        r"(?:regards|thanks|sincerely|best)\s*(?:regards)?\s*[,.]?\s*\n\s*([A-Z][a-z]+(?:\s+[A-Za-z]+)+)",
        r"\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*$",
    ]
    for pat in patterns:
        m = re.search(pat, body, re.MULTILINE | re.IGNORECASE)
        if m:
            return m.group(1).strip(), 0.7

    # Fallback: use sender email prefix
    if sender_name:
        name = sender_name.split("@")[0].replace(".", " ").replace("_", " ").title()
        return name, 0.5

    return "", 0.0


def _extract_dates(text):
    """Extract start and end dates from free-form text.

    Returns (start_date, end_date, confidence).
    """
    # Common date range patterns
    range_patterns = [
        r"(?:from|starting)\s+(.+?)\s+(?:to|until|till|ending|through)\s+(.+?)(?:\.|,|\n|$)",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}\s+\w+\s+\d{4})\s*(?:to|-)\s*(\d{1,2}\s+\w+\s+\d{4})",
        r"(\d{1,2}\s+\w+)\s*(?:to|-)\s*(\d{1,2}\s+\w+)",
    ]

    for pat in range_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                start = dateutil_parser.parse(m.group(1), fuzzy=True, dayfirst=True).date()
                end = dateutil_parser.parse(m.group(2), fuzzy=True, dayfirst=True).date()
                if end >= start:
                    return start, end, 0.9
            except (ValueError, OverflowError):
                continue

    # Single date patterns
    single_patterns = [
        r"(?:on|date|day)\s+(.+?)(?:\.|,|\n|$)",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*\d{0,4})",
    ]

    for pat in single_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                d = dateutil_parser.parse(m.group(1), fuzzy=True, dayfirst=True).date()
                # If year not specified and date is in the past, assume next year
                if d.year < 2000:
                    d = d.replace(year=datetime.now().year)
                return d, d, 0.8
            except (ValueError, OverflowError):
                continue

    # Last resort: try to find any date-like string
    try:
        d = dateutil_parser.parse(text, fuzzy=True, dayfirst=True).date()
        return d, d, 0.4
    except (ValueError, OverflowError):
        pass

    return None, None, 0.0


def _extract_leave_type(subject, body):
    """Extract leave type from subject and body text."""
    # Try subject first (higher confidence)
    lt, conf = match_leave_type(subject)
    if lt and conf >= 0.7:
        return lt, conf

    # Try body text - look for leave-related sentences
    lines = body.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) < 5 or len(line) > 200:
            continue
        lt2, conf2 = match_leave_type(line)
        if lt2 and conf2 > (conf or 0):
            lt, conf = lt2, conf2

    if lt:
        return lt, conf

    return None, 0.0


def _extract_reason(body, leave_type, dates_text=""):
    """Extract reason/notes from the email body."""
    # Look for reason patterns
    patterns = [
        r"(?:reason|because|due to|for)\s*[:\-]?\s*(.+?)(?:\.|$)",
        r"(?:i need|i would like|i want|requesting)\s+(?:a\s+)?(?:leave\s+)?(?:for|because|due to)\s+(.+?)(?:\.|$)",
    ]
    for pat in patterns:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            reason = m.group(1).strip()
            if len(reason) > 10:
                return reason[:200]

    return ""


def parse_email(email_data):
    """Parse a raw email dict into a LeaveRequest.

    Args:
        email_data: dict from email_reader.fetch_leave_emails()

    Returns:
        LeaveRequest with extracted fields and overall confidence.
    """
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    combined = subject + "\n" + body

    name, name_conf = _extract_name(
        email_data.get("sender_name", ""),
        body,
    )

    leave_type, type_conf = _extract_leave_type(subject, body)
    start_date, end_date, date_conf = _extract_dates(combined)
    reason = _extract_reason(body, leave_type)

    # Overall confidence is the minimum of individual confidences
    confidences = [c for c in [name_conf, type_conf, date_conf] if c > 0]
    overall = min(confidences) if confidences else 0.0

    return LeaveRequest(
        employee_name=name,
        leave_type=leave_type or "Unknown",
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        confidence=round(overall, 2),
        sender=email_data.get("sender", ""),
        sender_name=email_data.get("sender_name", ""),
        subject=subject,
        message_id=email_data.get("message_id", ""),
        uid=email_data.get("uid"),
        raw_body=body,
    )
