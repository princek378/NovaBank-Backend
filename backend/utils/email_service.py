import os
import json
import urllib.request
import urllib.error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, html_body, text_body=None):
    """
    Prefer Resend HTTPS API (works on Render free tier).
    Fall back to SMTP if RESEND_API_KEY is not set.
    """
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    from_addr = os.environ.get(
        "SMTP_FROM",
        "NovaBank <onboarding@resend.dev>",
    ).strip()

    if resend_key:
        return _send_via_resend(resend_key, from_addr, to_email, subject, html_body, text_body)

    return _send_via_smtp(from_addr, to_email, subject, html_body, text_body)


def _send_via_resend(api_key, from_addr, to_email, subject, html_body, text_body):
    payload = {
        "from": from_addr,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    }
    if text_body:
        payload["text"] = text_body

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print("EMAIL SENT via Resend:", subject, "->", to_email, body)
            return True
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print("EMAIL ERROR (Resend):", e.code, err)
        return False
    except Exception as e:
        print("EMAIL ERROR (Resend):", repr(e))
        return False


def _send_via_smtp(from_addr, to_email, subject, html_body, text_body):
    host = os.environ.get("SMTP_HOST", "").strip()
    port = int(os.environ.get("SMTP_PORT", "587") or 587)
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()

    if not host or not user or not password:
        print("EMAIL SKIPPED (no RESEND_API_KEY and SMTP not configured):", subject, "->", to_email)
        print("Body preview:", (text_body or html_body)[:300])
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr or user
    msg["To"] = to_email
    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())
        print("EMAIL SENT via SMTP:", subject, "->", to_email)
        return True
    except Exception as e:
        print("EMAIL ERROR (SMTP):", repr(e))
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
      <p style="font-size:32px;font-weight:bold;letter-spacing:6px">{otp}</p>
      <p style="color:#64748b">Expires in 10 minutes. Ignore if you did not request this.</p>
    </div>
    """
    return send_email(to_email, subject, html, f"Your NovaBank code is: {otp}")


def send_receipt_email(to_email, receipt):
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
            try:
                val = f"${float(val):,.2f}"
            except Exception:
                pass
        rows += f"<tr><td style='padding:8px;color:#64748b'>{label}</td><td style='padding:8px;font-weight:600'>{val}</td></tr>"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;border-radius:12px">
      <h2 style="color:#2563eb">NovaBank</h2>
      <p style="color:#16a34a;font-weight:700">Transaction successful</p>
      <table style="width:100%;border-collapse:collapse">{rows}</table>
    </div>
    """
    return send_email(to_email, subject, html)
