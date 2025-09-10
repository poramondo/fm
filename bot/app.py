import os
import uuid
import logging
import asyncio
from typing import Optional

import asyncpg
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold, hcode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ---------- LOG ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("bot")

# ---------- ENV ----------
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_USER_IDS", "").replace(" ", "").split(",") if x}
DATABASE_URL = os.getenv("DATABASE_URL_SYNC", os.getenv("DATABASE_URL", "")).replace("+asyncpg", "")

TELEGRAM_MODE = os.getenv("TELEGRAM_MODE", "polling").lower()
WEBHOOK_URL   = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET= os.getenv("WEBHOOK_SECRET", "")
WEBAPP_HOST   = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT   = int(os.getenv("WEBAPP_PORT", "8081"))
WEBHOOK_PATH  = os.getenv("WEBHOOK_PATH", "/bot/webhook")

STATUS_CHOICES = ["AWAITING_PAYMENT", "PROCESSING", "COMPLETED", "CANCELED", "EXPIRED"]

BOT_LOCALE = os.getenv("BOT_LOCALE", "ru").lower()
STATUS_LABELS = {
    "ru": {
        "AWAITING_PAYMENT": "💸 Ожидает оплату",
        "PROCESSING": "🛠 Обработка",
        "COMPLETED": "✅ Выполнено",
        "CANCELED": "🛑 Отменено",
        "EXPIRED": "⏰ Истёк срок",
    },
}
def status_label(code: str) -> str:
    return STATUS_LABELS.get(BOT_LOCALE, STATUS_LABELS["ru"]).get(code, code)

# ---------- DB POOL (lazy) ----------
POOL: Optional[asyncpg.Pool] = None
async def get_pool() -> asyncpg.Pool:
    global POOL
    if POOL is None:
        POOL = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        log.info("DB pool created")
    return POOL

# ---------- HELPERS ----------
def main_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗒 Список", callback_data="list:last")
    kb.button(text="📥 Последние 5", callback_data="menu:req")
    kb.adjust(2)
    return kb

def only_admin(handler):
    async def wrapper(message: Message, **kwargs):
        if message.from_user and message.from_user.id in ADMIN_IDS:
            return await handler(message, **kwargs)
        await message.answer("⛔️ Доступ только для админов.")
    return wrapper

def list_item_label(r: asyncpg.Record) -> str:
    dt = r["created_at"]
    when = dt.strftime("%m-%d %H:%M") if hasattr(dt, "strftime") else ""
    return f"{r['currency']} · {status_label(r['status'])} · {when} · {r['id'][:8]}"

def fmt_request_row(r: asyncpg.Record) -> str:
    return (
        f"{hbold('Заявка')} {hcode(r['id'])}\n"
        f"Сеть: {r['currency']}\n"
        f"Адрес получения: {hcode(r['payin_address'] or '-')}\n"
        f"Адрес отправки: {hcode(r['destination_address'] or '-')}\n"
        f"Контакт: {r['contact'] or '-'}\n"
        f"Статус: {hbold(status_label(r['status']))}\n"
        f"Резерв до: {r['reserved_until'] or '-'}\n"
        f"Создана: {r['created_at']}\n"
    )

def kb_for_request(rid: str, current_status: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for st in STATUS_CHOICES:
        if st != current_status:
            kb.button(text=status_label(st), callback_data=f"req:{rid}:set:{st}")
    kb.button(text="🔄 Обновить", callback_data=f"req:{rid}:refresh")
    kb.button(text="🗒 Список", callback_data="list:last")
    kb.adjust(2, 2, 1, 1)
    return kb

async def fetch_request(conn: asyncpg.Connection, rid: str) -> Optional[asyncpg.Record]:
    return await conn.fetchrow(
        """SELECT id::text, currency, destination_address, contact,
                  payin_address, status, reserved_until, created_at, updated_at
           FROM requests WHERE id=$1""",
        rid
    )

# ---------- BOT ----------
dp = Dispatcher()

@dp.message(Command("start"))
@only_admin
async def cmd_start(m: Message, **kwargs):
    await m.answer(
        f"{hbold('MixLab — админ-бот')}\n\n"
        "🗒 Список — последние заявки (кнопки)\n"
        "📥 Последние 5 — быстрый доступ к 5 заявкам\n",
        reply_markup=main_menu_kb().as_markup(),
        parse_mode="HTML"
    )

@dp.message(Command("list"))
@only_admin
async def cmd_list(m: Message, **kwargs):
    arg = None
    parts = m.text.split(maxsplit=1)
    if len(parts) > 1:
        arg = parts[1].strip().upper()
    pool = await get_pool()
    async with pool.acquire() as c:
        if arg:
            rows = await c.fetch(
                """SELECT id::text, currency, payin_address, status, created_at
                   FROM requests WHERE status=$1
                   ORDER BY created_at DESC LIMIT 20""",
                arg
            )
        else:
            rows = await c.fetch(
                """SELECT id::text, currency, payin_address, status, created_at
                   FROM requests ORDER BY created_at DESC LIMIT 20"""
            )
    if not rows:
        return await m.answer("Пусто.")
    lines = [f"{hcode(r['id'])}  {r['currency']:<8}  {r['status']:<10}  → {hcode(r['payin_address'] or '-')}" for r in rows]
    await m.answer("\n".join(lines), parse_mode="HTML")

@dp.message(Command("req"))
@only_admin
async def cmd_req(m: Message, **kwargs):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        pool = await get_pool()
        async with pool.acquire() as c:
            rows = await c.fetch(
                """SELECT id::text, currency, status, created_at
                   FROM requests ORDER BY created_at DESC LIMIT 5"""
            )
        if not rows:
            return await m.answer("Заявок пока нет.")
        kb = InlineKeyboardBuilder()
        for r in rows:
            kb.button(text=list_item_label(r), callback_data=f"req:{r['id']}:open")
        kb.adjust(1)
        return await m.answer("Выберите заявку:", reply_markup=kb.as_markup())

    try:
        rid = str(uuid.UUID(parts[1].strip()))
    except Exception:
        return await m.answer("Неверный UUID.")
    pool = await get_pool()
    async with pool.acquire() as c:
        r = await fetch_request(c, rid)
    if not r:
        return await m.answer("Заявка не найдена.")
    await m.answer(fmt_request_row(r), reply_markup=kb_for_request(r["id"], r["status"]).as_markup(), parse_mode="HTML")

@dp.message(Command("set"))
@only_admin
async def cmd_set(m: Message, **kwargs):
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        return await m.answer("Использование: /set <UUID> <STATUS>")
    try:
        rid = str(uuid.UUID(parts[1]))
    except Exception:
        return await m.answer("Неверный UUID.")
    status = parts[2].upper()
    if status not in STATUS_CHOICES:
        return await m.answer(f"Неверный статус. Разрешены: {', '.join(STATUS_CHOICES)}")
    pool = await get_pool()
    async with pool.acquire() as c:
        r = await c.fetchrow("SELECT id::text FROM requests WHERE id=$1", rid)
        if not r:
            return await m.answer("Заявка не найдена.")
        await c.execute("UPDATE requests SET status=$1, updated_at=NOW() WHERE id=$2", status, rid)
        r2 = await fetch_request(c, rid)
    await m.answer(f"OK. {hcode(rid)} → {hbold(status_label(status))}", parse_mode="HTML")
    if r2:
        await m.answer(fmt_request_row(r2), reply_markup=kb_for_request(rid, r2["status"]).as_markup(), parse_mode="HTML")

# ---------- CALLBACKS ----------
@dp.callback_query(F.data.startswith("req:"))
async def on_req_callback(cb: CallbackQuery):
    try:
        _, rid, action, *rest = cb.data.split(":")
        uuid.UUID(rid)
    except Exception:
        return await cb.answer("Некорректные данные", show_alert=True)
    pool = await get_pool()
    async with pool.acquire() as c:
        if action == "set":
            if not rest:
                return await cb.answer("Нет статуса", show_alert=True)
            new_st = rest[0].upper()
            if new_st not in STATUS_CHOICES:
                return await cb.answer("Неверный статус", show_alert=True)
            await c.execute("UPDATE requests SET status=$1, updated_at=NOW() WHERE id=$2", new_st, rid)
        r = await fetch_request(c, rid)
    if not r:
        return await cb.message.edit_text("Заявка не найдена.")
    await cb.message.edit_text(fmt_request_row(r), reply_markup=kb_for_request(rid, r["status"]).as_markup(), parse_mode="HTML")
    await cb.answer("Готово")

@dp.callback_query(F.data == "list:last")
async def on_list_last(cb: CallbackQuery):
    pool = await get_pool()
    async with pool.acquire() as c:
        rows = await c.fetch(
            """SELECT id::text, currency, status, created_at
               FROM requests ORDER BY created_at DESC LIMIT 5"""
        )
    if not rows:
        await cb.message.edit_text("Пусто.")
        return await cb.answer()
    kb = InlineKeyboardBuilder()
    for r in rows:
        kb.button(text=list_item_label(r), callback_data=f"req:{r['id']}:open")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1, 1)
    await cb.message.edit_text("📥 Последние заявки", reply_markup=kb.as_markup())
    await cb.answer()

@dp.callback_query(F.data == "menu:req")
async def on_menu_req(cb: CallbackQuery):
    pool = await get_pool()
    async with pool.acquire() as c:
        rows = await c.fetch(
            """SELECT id::text, currency, status, created_at
               FROM requests ORDER BY created_at DESC LIMIT 5"""
        )
    if not rows:
        await cb.message.edit_text("Заявок пока нет.", reply_markup=main_menu_kb().as_markup())
        return await cb.answer()
    kb = InlineKeyboardBuilder()
    for r in rows:
        kb.button(text=list_item_label(r), callback_data=f"req:{r['id']}:open")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1, 1)
    await cb.message.edit_text("Выберите заявку:", reply_markup=kb.as_markup())
    await cb.answer()

@dp.callback_query(F.data == "menu:main")
async def on_menu_main(cb: CallbackQuery):
    await cb.message.edit_text("Главное меню:", reply_markup=main_menu_kb().as_markup())
    await cb.answer()

# ---------- WEBHOOK SERVER (sync wrapper) ----------
async def run_webhook_server():
    if not WEBHOOK_URL or not WEBHOOK_SECRET:
        raise SystemExit("WEBHOOK_URL/WEBHOOK_SECRET не заданы")

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = web.Application()

    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    async def on_startup(app_):
        await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET, drop_pending_updates=True)
        log.info("Webhook set to %s", WEBHOOK_URL)

    async def on_shutdown(app_):
        await bot.delete_webhook()
        log.info("Webhook deleted")

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()
    log.info("Webhook server started on %s:%s", WEBAPP_HOST, WEBAPP_PORT)

    # держим процесс «вечно»
    await asyncio.Event().wait()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = web.Application()

    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    async def on_startup(app_):
        await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET, drop_pending_updates=True)
        log.info("Webhook set to %s", WEBHOOK_URL)

    async def on_shutdown(app_):
        await bot.delete_webhook()
        log.info("Webhook deleted")

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    log.info("Starting webhook server on %s:%s ...", WEBAPP_HOST, WEBAPP_PORT)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

# ---------- MAIN ----------
async def main():
    if not BOT_TOKEN or not ADMIN_IDS or not DATABASE_URL:
        raise SystemExit("BOT_TOKEN / ADMIN_USER_IDS / DATABASE_URL(_SYNC) не заданы")

    if TELEGRAM_MODE == "webhook":
        log.info("Mode: webhook")
        await run_webhook_server()
    else:
        log.info("Mode: polling")
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())