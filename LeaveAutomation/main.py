#!/usr/bin/env python3
"""Leave Email Automation — CLI Entry Point

Automates the workflow of reading leave request emails from Alimail,
parsing them, getting HRBP approval, updating the Lark attendance sheet,
and sending reply emails.
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from email_reader import fetch_leave_emails, mark_as_processed
from email_parser import parse_email
from email_responder import send_acknowledgment, send_approval, send_rejection
from lark_client import LarkClient
from approval_manager import (
    add_pending, get_pending, remove_pending,
    display_pending, review_request,
)


def cmd_fetch():
    """Fetch and parse new leave emails."""
    print("\n  Connecting to Alimail (IMAP)...")
    try:
        emails = fetch_leave_emails()
    except Exception as e:
        print(f"  Error connecting to email: {e}")
        return

    if not emails:
        print("  No new leave-related emails found.")
        return

    print(f"  Found {len(emails)} leave-related email(s). Parsing...\n")

    requests = []
    for em in emails:
        req = parse_email(em)
        requests.append(req)
        print(f"  Parsed: {req.employee_name} — {req.leave_type} — "
              f"{req.start_date or '?'} to {req.end_date or '?'} "
              f"(confidence: {req.confidence:.0%})")

    added = add_pending(requests)
    print(f"\n  Added {added} new request(s) to pending queue.")

    # Send acknowledgment emails
    ack = input("\n  Send acknowledgment emails? [y/N]: ").strip().lower()
    if ack == "y":
        for req in requests:
            try:
                send_acknowledgment(req)
                print(f"  Sent ack to {req.sender}")
            except Exception as e:
                print(f"  Failed to send ack to {req.sender}: {e}")

    # Mark emails as processed
    uids = [em["uid"] for em in emails if em.get("uid")]
    if uids:
        try:
            mark_as_processed(uids)
            print(f"  Marked {len(uids)} email(s) as processed.")
        except Exception as e:
            print(f"  Warning: Could not mark emails as processed: {e}")


def cmd_review():
    """Review pending requests (approve/reject)."""
    pending = display_pending()
    if not pending:
        return

    approved = []
    rejected = []

    for req in pending:
        action, modified_req, reason = review_request(req)

        if action == "approved":
            approved.append(modified_req)
            remove_pending(req.message_id)
            print(f"  ✓ Approved: {modified_req.employee_name}")

        elif action == "rejected":
            rejected.append((modified_req, reason))
            remove_pending(req.message_id)
            print(f"  ✗ Rejected: {modified_req.employee_name}")

        else:
            print(f"  — Skipped: {req.employee_name}")

    # Send response emails
    if approved or rejected:
        send = input("\n  Send response emails now? [y/N]: ").strip().lower()
        if send == "y":
            for req in approved:
                try:
                    send_approval(req)
                    print(f"  Sent approval to {req.sender}")
                except Exception as e:
                    print(f"  Failed: {e}")

            for req, reason in rejected:
                try:
                    send_rejection(req, reason)
                    print(f"  Sent rejection to {req.sender}")
                except Exception as e:
                    print(f"  Failed: {e}")

    # Sync approved to Lark
    if approved:
        sync = input("\n  Sync approved requests to Lark sheet now? [y/N]: ").strip().lower()
        if sync == "y":
            _sync_to_lark(approved)


def cmd_sync():
    """Sync approved requests to Lark sheet (from pending with manual selection)."""
    pending = display_pending()
    if not pending:
        return

    print("  Select requests to sync to Lark (comma-separated numbers, or 'all'):")
    sel = input("  > ").strip().lower()

    if sel == "all":
        selected = pending
    else:
        try:
            indices = [int(x.strip()) - 1 for x in sel.split(",")]
            selected = [pending[i] for i in indices if 0 <= i < len(pending)]
        except (ValueError, IndexError):
            print("  Invalid selection.")
            return

    _sync_to_lark(selected)

    # Remove synced from pending
    for req in selected:
        remove_pending(req.message_id)


def _sync_to_lark(requests):
    """Write leave entries to the Lark sheet."""
    print("\n  Connecting to Lark...")
    lark = LarkClient()

    try:
        lark.authenticate()
        print("  Authenticated with Lark API.")
    except Exception as e:
        print(f"  Lark authentication failed: {e}")
        return

    try:
        lark.resolve_wiki_url()
        print(f"  Resolved spreadsheet: {lark.spreadsheet_token}")
    except Exception as e:
        print(f"  Failed to resolve wiki URL: {e}")
        return

    # Get available sheets and let user pick if needed
    try:
        sheets = lark.get_sheets()
        if not sheets:
            print("  No sheets found in spreadsheet.")
            return

        if len(sheets) == 1:
            lark.set_sheet(sheets[0]["sheet_id"])
            print(f"  Using sheet: {sheets[0].get('title', sheets[0]['sheet_id'])}")
        else:
            print("\n  Available sheets:")
            for i, s in enumerate(sheets, 1):
                print(f"    {i}. {s.get('title', s['sheet_id'])}")
            choice = input("  Select sheet number: ").strip()
            try:
                idx = int(choice) - 1
                lark.set_sheet(sheets[idx]["sheet_id"])
            except (ValueError, IndexError):
                print("  Invalid selection, using first sheet.")
                lark.set_sheet(sheets[0]["sheet_id"])
    except Exception as e:
        print(f"  Failed to get sheets: {e}")
        return

    # Write each approved leave
    for req in requests:
        dates = req.date_range()
        if not dates:
            print(f"  Skipping {req.employee_name}: no valid dates")
            continue

        for d in dates:
            try:
                lark.write_leave(req.employee_name, d, req.leave_type)
                print(f"  ✓ {req.employee_name} — {d.strftime('%d-%b')} — {req.leave_type}")
            except ValueError as e:
                print(f"  ✗ {req.employee_name} — {d.strftime('%d-%b')}: {e}")
            except Exception as e:
                print(f"  ✗ Error: {e}")


def cmd_history():
    """View processing history (pending queue)."""
    display_pending()


def main():
    """Main CLI menu."""
    print("\n" + "=" * 56)
    print("  Leave Email Automation System")
    print("  51Talk MENA — HRBP Team")
    print("=" * 56)

    while True:
        print("\n  Menu:")
        print("    1. Fetch & parse new leave emails")
        print("    2. Review pending requests (approve/reject)")
        print("    3. Sync approved requests to Lark sheet")
        print("    4. View pending requests")
        print("    5. One-shot (fetch → review → sync)")
        print("    0. Exit")

        choice = input("\n  Select option: ").strip()

        if choice == "1":
            cmd_fetch()
        elif choice == "2":
            cmd_review()
        elif choice == "3":
            cmd_sync()
        elif choice == "4":
            cmd_history()
        elif choice == "5":
            cmd_fetch()
            cmd_review()
        elif choice == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("  Invalid option.")


if __name__ == "__main__":
    main()
