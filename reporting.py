import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any

import config

logger = logging.getLogger(__name__)

def generate_html_report(stats: Dict[str, Any]) -> str:
    """Generates an HTML formatted report from the processing statistics."""
    html_style = """
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; }
        table { border-collapse: collapse; width: 80%; max-width: 700px; margin: 20px 0; box-shadow: 0 2px 3px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #dddddd; text-align: left; padding: 12px; }
        th { background-color: #f2f2f2; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .summary { margin-bottom: 20px; font-size: 1.1em; }
        .success { color: #28a745; font-weight: bold; }
        .no-change { color: #ffc107; }
        .error { color: #dc3545; font-weight: bold; }
        h2 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 5px;}
    </style>
    """

    table_rows = ""
    total_inserted = 0
    for feed_name, count in sorted(stats.items()):
        if isinstance(count, int):
            total_inserted += count
            status_class = "success" if count > 0 else "no-change"
            status_text = f"{count:,} new records" if count > 0 else "No new records"
        else:
            status_class = "error"
            status_text = f"Failed: {count}"

        table_rows += f"<tr><td>{feed_name}</td><td class='{status_class}'>{status_text}</td></tr>"

    html_body = f"""
    <html>
    <head>{html_style}</head>
    <body>
        <h2>DhanVani-Data Processing Report</h2>
        <div class="summary">
            <p>The data processing script has completed.</p>
            <p><strong>Total new records inserted: <span class="success">{total_inserted:,}</span></strong></p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Feed Name</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        <p><small>This is an automated report.</small></p>
    </body>
    </html>
    """
    return html_body

def send_email_report(report_stats: Dict[str, Any]) -> bool:
    """
    Constructs and sends an email report with processing statistics.
    Returns True if successful, False otherwise.
    """
    if not all([config.SMTP_USER, config.SMTP_PASSWORD, config.EMAIL_RECIPIENTS]):
        logger.warning("Email credentials or recipients not configured. Skipping email report.")
        logger.warning("Please set SMTP_USER, SMTP_PASSWORD, and EMAIL_RECIPIENTS in your environment.")
        return False

    subject = f"DhanVani-Data Run Report - {sum(v for v in report_stats.values() if isinstance(v, int)):,} New Records"
    html_content = generate_html_report(report_stats)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"DhanVani Reporter <{config.SMTP_USER}>"
    msg['To'] = config.EMAIL_RECIPIENTS

    msg.attach(MIMEText(html_content, 'html'))

    try:
        logger.info(f"Connecting to SMTP server {config.SMTP_SERVER}:{config.SMTP_PORT} to send report...")
        with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
            logger.info(f"Email report sent successfully to {config.EMAIL_RECIPIENTS}.")
            return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: Failed to send email. Check your SMTP_USER and SMTP_PASSWORD. Error: {e}")
        logger.error("For Gmail, ensure you are using a generated 'App Password', not your regular account password.")
        return False
    except Exception as e:
        logger.error(f"Failed to send email report. Error: {e}")
        return False
