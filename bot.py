import logging
import re
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "7856354677:AAEdLqgysliPWcOu3cwPXJtwDqozbw8uvZo"

ALINA = "@Alinish_S"
ILONA = "@Ilona"

TRIGGERS = [
    (re.compile(r'\b(klr\s*bus|клр\s*бас|klr|клр)\b', re.IGNORECASE), "KLR Bus"),
    (re.compile(r'\b(g[uü]nsel\s*group|гюнсел\s*груп|g[uü]nsel|гюнсел)\b', re.IGNORECASE), "Günsel Group"),
]

CYCLE_START = datetime(2025, 5, 18, tzinfo=timezone(timedelta(hours=3)))

SCHEDULE = [
    {"day": "вс", "ilona": None,      "alina": (8,  15)},
    {"day": "пн", "ilona": (14, 21),  "alina": (8,  15)},
    {"day": "вт", "ilona": (8,  15),  "alina": (14, 21)},
    {"day": "ср", "ilona": (8,  15),  "alina": (14, 21)},
    {"day": "чт", "ilona": (14, 21),  "alina": (8,  15)},
    {"day": "пт", "ilona": (8,  15),  "alina": None     },
    {"day": "сб", "ilona": None,      "alina": (8,  15)},
    {"day": "вс", "ilona": (8,  15),  "alina": (14, 21)},
    {"day": "пн", "ilona": (14, 21),  "alina": (8,  15)},
    {"day": "вт", "ilona": (8,  15),  "alina": None     },
    {"day": "ср", "ilona": (8,  15),  "alina": (14, 21)},
    {"day": "чт", "ilona": (14, 21),  "alina": (8,  15)},
    {"day": "пт", "ilona": (8,  15),  "alina": (14, 21)},
    {"day": "сб", "ilona": (8,  15),  "alina": (10, 17)},
]


def get_cycle_day():
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    start = CYCLE_START.replace(hour=0, minute=0, second=0, microsecond=0)
    now_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    diff = (now_day - start).days
    return diff % 14


def is_on_shift(shift, hour):
    if shift is None:
        return False
    return shift[0] <= hour < shift[1]


def get_on_duty():
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    hour = now.hour
    cycle_day = get_cycle_day()
    sched = SCHEDULE[cycle_day]
    on_duty = []
    if is_on_shift(sched["alina"], hour):
        on_duty.append(ALINA)
    if is_on_shift(sched["ilona"], hour):
        on_duty.append(ILONA)
    return on_duty


def find_trigger(text):
    for pattern, label in TRIGGERS:
        if pattern.search(text):
            return label
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    label = find_trigger(message.text)
    if not label:
        return
    on_duty = get_on_duty()
    if on_duty:
        tags = " ".join(on_duty)
        reply = f"{label} → {tags}, ваш вопрос по {label}!"
    else:
        reply = (
            f"{label} → {ALINA} {ILONA}, ваш вопрос по {label}! "
            f"(вне смены — уточните позже)"
        )
    await message.reply_text(reply)


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()
