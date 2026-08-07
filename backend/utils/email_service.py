import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, html_body, text_body=None):
    """
    Send email via SMTP.
    Set these on Render Environment:
      SMTP_HOST=smtp.gmail.com
      SMTP_PORT=587
      SMTP_USER=yourgmail@gmail.com
      SMTP_PASSWORD=your_gmail_app_password
      SMTP_FROM=NovaBank <yourgmail@gmail.com>
    """
    host = os.environ.get("SMTP_HOST", "").strip()
    port = int(os.environ.get("SMTP_PORT", "587") or 587)
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    from_addr = os.environ.get("SMTP_FROM", user or "noreply@novabank.best").strip()

    if not host or not user or not password:
        print("EMAIL SKIPPED (SMTP not configured):", subject, "->", to_email)
        print("Body preview:", (text_body or html_body)[:200])
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())
        print("EMAIL SENT:", subject, "->", to_email)
        return True
    except Exception as e:
        print("EMAIL ERROR:", repr(e))
        return False


def send_otp_email(to_email, otp, purpose="verification"):
    if purpose == "register":
        subject = "NovaBank — Verify your email"
        title = "Email verification code"
    elif purpose == "reset":
        subject = "NovaBank — Password reset code"
        title = "Password reset code"
    else:
        subject = "NovaBank — Verification code"
        title = "Verification code"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px">
      <h2 style="color:#2563eb">NovaBank</h2>
      <h3>{title}</h3>
      <p>Your one-time code is:</p>
      <p style="font-size:32px;font-weight:bold;letter-spacing:6px;color:#0f172a">{otp}</p>
      <p style="color:#64748b">This code expires in 10 minutes. If you did not request this, ignore this email.</p>
    </div>
    """
    return send_email(to_email, subject, html, f"Your NovaBank code is: {otp}")


def send_receipt_email(to_email, receipt):
    """receipt = dict with reference, type, amount, from_account, to_account, etc."""
    subject = f"NovaBank Receipt — {receipt.get('reference', 'Transaction')}"
    rows = ""
    for label, key in [
        ("Reference", "reference"),
        ("Type", "type"),
        ("Amount", "amount"),
        ("From", "from_account"),
        ("To", "to_account"),
        ("Bank", "bank_name"),
        ("Status", "status"),
        ("Date", "date"),
    ]:
        val = receipt.get(key)
        if val is None or val == "":
            continue
        if key == "amount":
            val = f"${float(val):,.2f}"
        rows += f"<tr><td style='padding:8px;color:#64748b'>{label}</td><td style='padding:8px;font-weight:600'>{val}</td></tr>"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;border-radius:12px">
      <h2 style="color:#2563eb">NovaBank</h2>
      <p style="color:#16a34a;font-weight:700">✓ Transaction successful</p>
      <table style="width:100%;border-collapse:collapse">{rows}</table>
      <p style="color:#94a3b8;font-size:12px;margin-top:20px">Keep this email as your receipt.</p>
    </div>
    """
    return send_email(to_email, subject, html)
