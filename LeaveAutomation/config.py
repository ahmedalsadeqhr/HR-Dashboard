import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

ALIMAIL_EMAIL = os.getenv("ALIMAIL_EMAIL")
ALIMAIL_PASSWORD = os.getenv("ALIMAIL_PASSWORD")
ALIMAIL_IMAP = os.getenv("ALIMAIL_IMAP")
ALIMAIL_SMTP = os.getenv("ALIMAIL_SMTP")

LARK_APP_ID = os.getenv("LARK_APP_ID")
LARK_APP_SECRET = os.getenv("LARK_APP_SECRET")
LARK_WIKI_URL = os.getenv("LARK_WIKI_URL")

# IMAP settings
IMAP_PORT = 993
SMTP_PORT = 465

# Leave email subject keywords (case-insensitive)
LEAVE_KEYWORDS = [
    "leave", "absence", "vacation", "sick", "annual", "casual",
    "day off", "time off", "permission", "early leave",
    "إجازة", "اجازة", "غياب",
]

PROCESSED_FLAG = b"LeaveProcessed"
