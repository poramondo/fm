import os
import logging
import httpx
from typing import Iterable
from aiogram.utils.markdown import hbold, hcode  # это просто удобные форматтеры, не обязательны
from app.models.request import Request

log = logging.getLogger("notify.telegram")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [x for x in os.getenv("TELEGRAM_ADMIN_IDS", "").replace(" ", "").split(",") if x]
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "true").lower() in ("1", "true", "yes")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")  # например: https://fastmix.io

def _admin_ids() -> Iterable[int]:
    for x in ADMIN_IDS:
        try:
            yield int(x)
        except Exception:
            continue

def _status_label(code: str) -> str:
    mapping = {
        "AWAITING_PAYMENT": "💸 Ожидает оплату",
        "PROCESSING": "🛠 Обработка",
        "COMPLETED": "✅ Выполнено",
        "CANCELED": "🛑 Отменено",
        "EXPIRED": "⏰ Истёк срок",
        "NEW": "🆕 Создана",
    }
    return mapping.get(code, code)

async def notify_new_request(req: Request) -> None:
    if not TELEGRAM_ENABLED or not BOT_TOKEN or not ADMIN_IDS:
        return

    link = f"\nСсылка: {PUBLIC_BASE_URL}/status/{req.id}" if PUBLIC_BASE_URL else ""
    text = (
        f"{hbold('Новая заявка')}\n"
        f"ID: {hcode(req.id)}\n"
        f"Сеть: {req.currency}\n"
        f"Pay-in: {hcode(req.allocated_address or '-')}\n"
        f"Dest: {hcode(req.payout_address)}\n"
        f"Контакт: {req.contact or '-'}\n"
        f"Статус: {_status_label(req.status)}"
        f"{link}"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        for admin_id in _admin_ids():
            try:
                await client.post(url, json={
                    "chat_id": admin_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                })
            except Exception as e:
                log.warning("Failed to notify admin %s: %s", admin_id, e)
