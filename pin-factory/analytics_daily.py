"""
NeatNook Daily Pinterest Analytics Tracker + Email Report (Zero Dependencies)

Env vars:
  PINTEREST_READ_TOKEN  - Pinterest API v5 access token (read-only or standard)
  SMTP_USER             - Gmail address (e.g. khoaanh15111997@gmail.com)
  SMTP_APP_PASSWORD     - Gmail 16-char App Password (https://myaccount.google.com/apppasswords)
  REPORT_TO_EMAIL       - Destination email (defaults to SMTP_USER)
  SMTP_HOST             - Optional (default: smtp.gmail.com)
  SMTP_PORT             - Optional (default: 465)

Usage:
  python pin-factory/analytics_daily.py --dry-run
  python pin-factory/analytics_daily.py
"""
import datetime as dt
import json
import os
import smtplib
import sys
import urllib.parse
import urllib.request
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = ROOT / "business" / "metrics.jsonl"
DRY_RUN = "--dry-run" in sys.argv

today = dt.date.today()
start_date = (today - dt.timedelta(days=7)).isoformat()
end_date = today.isoformat()


def send_email(subject: str, text_body: str, html_body: str):
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_APP_PASSWORD", "")
    to_email = os.environ.get("REPORT_TO_EMAIL", smtp_user)
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))

    if not smtp_user or not smtp_pass or not to_email:
        print("Skipping email (set SMTP_USER and SMTP_APP_PASSWORD to enable email reports).")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"NeatNook Analytics <{smtp_user}>"
    msg["To"] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print(f"Email report sent to {to_email}")


def main():
    if DRY_RUN:
        sample = {
            "date": end_date,
            "window": f"{start_date}..{end_date}",
            "impressions_7d": 0,
            "saves_7d": 0,
            "pin_clicks_7d": 0,
            "outbound_clicks_7d": 0,
            "avg_outbound_per_day": 0.0,
            "go_signal_amazon": False,
        }
        print("[DRY RUN] Daily Pinterest Analytics + Email tracker ready:")
        print(json.dumps(sample, indent=2))
        return

    token = os.environ.get("PINTEREST_READ_TOKEN") or os.environ.get("PINTEREST_ACCESS_TOKEN")
    if not token:
        print("ERROR: Missing PINTEREST_READ_TOKEN env var.", file=sys.stderr)
        sys.exit(1)

    params = urllib.parse.urlencode(
        {
            "start_date": start_date,
            "end_date": end_date,
            "metric_types": "IMPRESSION,SAVE,PIN_CLICK,OUTBOUND_CLICK",
        }
    )
    req = urllib.request.Request(
        f"https://api.pinterest.com/v5/user_account/analytics?{params}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    summary = (data.get("all") or {}).get("summary_metrics") or {}
    impressions = int(summary.get("IMPRESSION", 0))
    saves = int(summary.get("SAVE", 0))
    pin_clicks = int(summary.get("PIN_CLICK", 0))
    outbound = int(summary.get("OUTBOUND_CLICK", 0))
    avg_outbound = round(outbound / 7.0, 2)
    go_signal = avg_outbound >= 20.0

    record = {
        "date": end_date,
        "window": f"{start_date}..{end_date}",
        "impressions_7d": impressions,
        "saves_7d": saves,
        "pin_clicks_7d": pin_clicks,
        "outbound_clicks_7d": outbound,
        "avg_outbound_per_day": avg_outbound,
        "go_signal_amazon": go_signal,
    }
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    status_line = (
        "GO SIGNAL: Da cham moc >= 20 click/ngay - san sang mua .com & mo Amazon Associates!"
        if go_signal
        else "Dang giai doan nuoi traffic (muc tieu mo Amazon: >= 20 click/ngay)."
    )
    subject = f"[NeatNook] Pinterest Report {end_date} - {outbound} outbound clicks (7d)"
    text_body = (
        f"NeatNook Pinterest Daily Report ({end_date})\n"
        f"- 7d Impressions: {impressions:,}\n"
        f"- 7d Saves: {saves:,}\n"
        f"- 7d Pin Clicks: {pin_clicks:,}\n"
        f"- 7d Outbound Clicks: {outbound:,} (~{avg_outbound}/day)\n\n"
        f"{status_line}\n"
    )
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;padding:18px;border:1px solid #e7e2da;border-radius:12px;">
      <h2 style="margin-top:0;color:#1e1d1b;">NeatNook Pinterest Report ({end_date})</h2>
      <ul style="line-height:1.8;color:#333;">
        <li><strong>7d Impressions:</strong> {impressions:,}</li>
        <li><strong>7d Saves:</strong> {saves:,}</li>
        <li><strong>7d Pin Clicks:</strong> {pin_clicks:,}</li>
        <li><strong>7d Outbound Clicks:</strong> {outbound:,} (~{avg_outbound}/ngày)</li>
      </ul>
      <p style="padding:10px 14px;background:#eef4f1;border-radius:8px;color:#2c463c;"><strong>{status_line}</strong></p>
    </div>
    """
    print(text_body)
    send_email(subject, text_body, html_body)


if __name__ == "__main__":
    main()
