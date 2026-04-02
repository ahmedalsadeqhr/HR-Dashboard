import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def _send_email(to_addr, subject, body_html, in_reply_to=None):
    """Send an email via Alimail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = config.ALIMAIL_EMAIL
    msg["To"] = to_addr
    msg["Subject"] = subject

    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to

    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP_SSL(config.ALIMAIL_SMTP, config.SMTP_PORT) as server:
        server.login(config.ALIMAIL_EMAIL, config.ALIMAIL_PASSWORD)
        server.sendmail(config.ALIMAIL_EMAIL, to_addr, msg.as_string())


def send_acknowledgment(request):
    """Send acknowledgment that leave request was received."""
    subject = f"Re: {request.subject}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <p>Dear {request.employee_name},</p>
        <p>Your leave request has been <strong>received</strong> and is being processed.</p>
        <table style="border-collapse: collapse; margin: 15px 0;">
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Leave Type:</td>
                <td style="padding: 5px 0;">{request.leave_type}</td></tr>
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Start Date:</td>
                <td style="padding: 5px 0;">{request.start_date or 'N/A'}</td></tr>
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">End Date:</td>
                <td style="padding: 5px 0;">{request.end_date or 'N/A'}</td></tr>
        </table>
        <p>You will receive another email once your request has been reviewed.</p>
        <p>Best regards,<br>HR Team</p>
    </div>
    """
    _send_email(request.sender, subject, body, request.message_id)


def send_approval(request):
    """Send approval notification."""
    subject = f"Re: {request.subject}"
    dates = f"{request.start_date}"
    if request.end_date and request.end_date != request.start_date:
        dates = f"{request.start_date} to {request.end_date}"

    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <p>Dear {request.employee_name},</p>
        <p>Your leave request has been <strong style="color: green;">APPROVED</strong>.</p>
        <table style="border-collapse: collapse; margin: 15px 0;">
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Leave Type:</td>
                <td style="padding: 5px 0;">{request.leave_type}</td></tr>
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Date(s):</td>
                <td style="padding: 5px 0;">{dates}</td></tr>
        </table>
        <p>Your leave has been recorded in the attendance system.</p>
        <p>Best regards,<br>HR Team</p>
    </div>
    """
    _send_email(request.sender, subject, body, request.message_id)


def send_rejection(request, reason=""):
    """Send rejection notification."""
    subject = f"Re: {request.subject}"
    dates = f"{request.start_date}"
    if request.end_date and request.end_date != request.start_date:
        dates = f"{request.start_date} to {request.end_date}"

    reason_html = ""
    if reason:
        reason_html = f'<tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Reason:</td><td style="padding: 5px 0;">{reason}</td></tr>'

    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <p>Dear {request.employee_name},</p>
        <p>Your leave request has been <strong style="color: red;">DECLINED</strong>.</p>
        <table style="border-collapse: collapse; margin: 15px 0;">
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Leave Type:</td>
                <td style="padding: 5px 0;">{request.leave_type}</td></tr>
            <tr><td style="padding: 5px 15px 5px 0; font-weight: bold;">Date(s):</td>
                <td style="padding: 5px 0;">{dates}</td></tr>
            {reason_html}
        </table>
        <p>Please contact HR if you have any questions.</p>
        <p>Best regards,<br>HR Team</p>
    </div>
    """
    _send_email(request.sender, subject, body, request.message_id)
