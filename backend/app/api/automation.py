from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api import deps
from app.db.redis_client import redis_conn
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

router = APIRouter(dependencies=[Depends(deps.get_current_user)])

CONFIG_HASH = "automation:config"

class ConfigItem(BaseModel):
    key: str
    value: str

@router.get("/config/{key}")
def get_config_item(key: str):
    val = redis_conn.hget(CONFIG_HASH, key)
    return {"key": key, "value": val or ""}

@router.post("/config")
def set_config_item(item: ConfigItem):
    redis_conn.hset(CONFIG_HASH, mapping={item.key: item.value})
    return {"success": True}

@router.post("/newsletter/preview")
def newsletter_preview():
    subject = "AI Weekly Newsletter"
    rss_url = redis_conn.hget(CONFIG_HASH, "RSS_URL") or ""
    header = f"<h2>Weekly Digest</h2><p>Source: {rss_url or 'N/A'}</p>"
    body = """
    <h3>Highlights</h3>
    <ul>
      <li>Top AI news from RSS</li>
      <li>Twitter/Reddit summaries</li>
      <li>Internal announcements</li>
    </ul>
    """
    html = f"<!doctype html><html><body>{header}{body}</body></html>"
    return {"subject": subject, "html": html}

class NewsletterPayload(BaseModel):
    subject: str
    html: str

@router.post("/newsletter/send")
def newsletter_send(payload: NewsletterPayload):
    smtp_host = redis_conn.hget(CONFIG_HASH, "SMTP_HOST")
    smtp_port = redis_conn.hget(CONFIG_HASH, "SMTP_PORT")
    sender_user = redis_conn.hget(CONFIG_HASH, "SENDER_USERNAME")
    sender_pass = redis_conn.hget(CONFIG_HASH, "SENDER_PASSWORD")
    to_addrs = redis_conn.hget(CONFIG_HASH, "TO_ADDRS")
    from_alias = redis_conn.hget(CONFIG_HASH, "FROM_ALIAS") or "AI Console"

    if not all([smtp_host, smtp_port, sender_user, to_addrs]):
        raise HTTPException(status_code=400, detail="SMTP 配置不完整，请在设置中填写必要字段")

    recipients = [addr.strip() for addr in (to_addrs or "").split(",") if addr.strip()]
    if not recipients:
        raise HTTPException(status_code=400, detail="未配置收件人")

    msg = MIMEText(payload.html, "html", "utf-8")
    msg["Subject"] = payload.subject
    msg["From"] = formataddr((from_alias, sender_user))
    msg["To"] = ", ".join(recipients)

    try:
        port = int(smtp_port)
        if port == 465:
            with smtplib.SMTP_SSL(smtp_host, port) as server:
                if sender_pass:
                    server.login(sender_user, sender_pass)
                server.sendmail(sender_user, recipients, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, port) as server:
                server.ehlo()
                try:
                    server.starttls()
                    server.ehlo()
                except Exception:
                    pass
                if sender_pass:
                    server.login(sender_user, sender_pass)
                server.sendmail(sender_user, recipients, msg.as_string())
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")
