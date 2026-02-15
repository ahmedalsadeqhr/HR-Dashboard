import imaplib
import json
import os
import email
import email.header
import email.utils
import config

PROCESSED_FILE = os.path.join(os.path.dirname(__file__), "processed_uids.json")


def _load_processed():
    """Load set of already-processed email UIDs."""
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return set(json.load(f))


def _save_processed(uids_set):
    """Save processed UIDs to disk."""
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(uids_set), f)


def _decode_header(header_value):
    """Decode an email header into a plain string."""
    if not header_value:
        return ""
    parts = email.header.decode_header(header_value)
    decoded = []
    for data, charset in parts:
        if isinstance(data, bytes):
            decoded.append(data.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(data)
    return " ".join(decoded)


def _get_body(msg):
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
            if ct == "text/html":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def _is_leave_related(subject, body):
    """Check if email subject or body contains leave-related keywords."""
    text = (subject + " " + body).lower()
    return any(kw in text for kw in config.LEAVE_KEYWORDS)


def _connect():
    """Create and return an authenticated IMAP connection."""
    imap = imaplib.IMAP4_SSL(config.ALIMAIL_IMAP, config.IMAP_PORT)
    imap.login(config.ALIMAIL_EMAIL, config.ALIMAIL_PASSWORD)
    return imap


def fetch_leave_emails(limit=50):
    """Fetch unread leave-related emails from Alimail.

    Returns list of dicts with keys:
        uid, sender, sender_name, subject, body, date, message_id
    """
    results = []
    processed = _load_processed()
    imap = _connect()

    try:
        imap.select("INBOX")

        # Search for unseen emails
        status, data = imap.uid("search", None, "UNSEEN")
        if status != "OK" or not data[0]:
            return results

        uid_list = data[0].split()
        uid_list = uid_list[-limit:]

        for uid_bytes in uid_list:
            uid = uid_bytes.decode()

            # Skip already processed
            if uid in processed:
                continue

            # Fetch the email (BODY.PEEK to avoid marking as read)
            status, msg_data = imap.uid("fetch", uid, "(BODY.PEEK[])")
            if status != "OK":
                continue

            raw = None
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw = response_part[1]

            if raw is None:
                continue

            msg = email.message_from_bytes(raw)

            subject = _decode_header(msg.get("Subject", ""))
            body = _get_body(msg)

            if not _is_leave_related(subject, body):
                continue

            sender = email.utils.parseaddr(msg.get("From", ""))
            date_str = msg.get("Date", "")
            message_id = msg.get("Message-ID", "")

            results.append({
                "uid": uid,
                "sender": sender[1],
                "sender_name": sender[0] or sender[1].split("@")[0],
                "subject": subject,
                "body": body,
                "date": date_str,
                "message_id": message_id,
            })
    finally:
        try:
            imap.logout()
        except Exception:
            pass

    return results


def mark_as_processed(uids):
    """Mark email UIDs as processed by saving to local tracking file."""
    if not uids:
        return

    processed = _load_processed()
    for uid in uids:
        processed.add(str(uid))
    _save_processed(processed)
