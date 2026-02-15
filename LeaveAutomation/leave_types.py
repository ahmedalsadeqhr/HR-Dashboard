from difflib import SequenceMatcher

LEAVE_TYPES = [
    "Annual Leave",
    "Casual Leave",
    "Sick Leave",
    "Unpaid Leave",
    "Early Leave (HD)",
    "Half Day",
    "Marriage Leave",
    "Paternity Leave",
    "Maternity Leave",
    "Bereavement Leave",
    "Military Call Leave",
    "Pilgrimage Leave",
    "2 Hours",
    "Present",
    "Missing Punch",
    "Annual Leave (Refund)",
    "Sick Leave (Refund)",
    "Half Day (Refund)",
    "Annual Leave (BD)",
    "Casual Leave (BD)",
    "Sick Leave (BD)",
    "Unpaid Leave (BD)",
    "Early Leave (HD) (BD)",
    "Half Day (BD)",
    "Marriage Leave (BD)",
    "Paternity Leave (BD)",
    "Maternity Leave (BD)",
    "Bereavement Leave (BD)",
    "Military Call Leave (BD)",
]

# Aliases map common phrases to canonical leave type names
ALIASES = {
    "annual": "Annual Leave",
    "annual leave": "Annual Leave",
    "vacation": "Annual Leave",
    "casual": "Casual Leave",
    "casual leave": "Casual Leave",
    "personal": "Casual Leave",
    "sick": "Sick Leave",
    "sick leave": "Sick Leave",
    "medical": "Sick Leave",
    "illness": "Sick Leave",
    "unpaid": "Unpaid Leave",
    "unpaid leave": "Unpaid Leave",
    "without pay": "Unpaid Leave",
    "early leave": "Early Leave (HD)",
    "early": "Early Leave (HD)",
    "half day": "Half Day",
    "half": "Half Day",
    "marriage": "Marriage Leave",
    "wedding": "Marriage Leave",
    "paternity": "Paternity Leave",
    "maternity": "Maternity Leave",
    "bereavement": "Bereavement Leave",
    "death": "Bereavement Leave",
    "funeral": "Bereavement Leave",
    "military": "Military Call Leave",
    "pilgrimage": "Pilgrimage Leave",
    "hajj": "Pilgrimage Leave",
    "umrah": "Pilgrimage Leave",
    "2 hours": "2 Hours",
    "two hours": "2 Hours",
    "permission": "2 Hours",
    "missing punch": "Missing Punch",
    "forgot punch": "Missing Punch",
}


def match_leave_type(text):
    """Match free-form text to a canonical leave type.

    Returns (leave_type, confidence) where confidence is 0.0-1.0.
    """
    text_lower = text.lower().strip()

    # Exact alias match
    if text_lower in ALIASES:
        return ALIASES[text_lower], 1.0

    # Substring alias match
    for alias, leave_type in sorted(ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in text_lower:
            return leave_type, 0.9

    # Fuzzy match against canonical leave type names
    best_match = None
    best_score = 0.0
    for lt in LEAVE_TYPES:
        score = SequenceMatcher(None, text_lower, lt.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = lt

    if best_score >= 0.6:
        return best_match, best_score

    return None, 0.0
