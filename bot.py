
import os
import sqlite3
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

DB = "projects.db"

def setup_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network TEXT,
                name TEXT,
                reference TEXT
            )
        """)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 NFT MINT BOT\n\n"
        "Welcome!\n\n"
        "/id - Your Telegram ID\n"
        "/help - Commands\n"
        "/projects - My projects\n"
        "/add - Add a project"
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your Telegram ID: {update.effective_user.id}"
    )

def authorized(update):
    return OWNER_ID and str(update.effective_user.id) == OWNER_ID

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/id - Show your ID\n"
        "/projects - List projects\n"
        "/add network | name | link_or_contract\n\n"
        "Networks: ethereum, base, polygon, solana"
    )

async def add_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("Access not configured.")
        return

    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]

    if len(parts) != 3:
        await update.message.reply_text(
            "Format:\n/add base | Project Name | Website or Contract"
        )
        return

    network, name, reference = parts
    allowed = ["ethereum", "base", "polygon", "solana"]

    if network.lower() not in allowed:
        await update.message.reply_text("Unsupported network.")
        return

    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO projects (network, name, reference) VALUES (?, ?, ?)",
            (network.lower(), name, reference)
        )

    await update.message.reply_text(f"✅ Added: {name}")

async def projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("Access not configured.")
        return

    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT id, network, name, reference FROM projects"
        ).fetchall()

    if not rows:
        await update.message.reply_text("No projects added yet.")
        return

    result = "\n\n".join(
        f"#{r[0]} | {r[2]}\nNetwork: {r[1]}\n{r[3]}"
        for r in rows
    )
    await update.message.reply_text(result)

def main():
    setup_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add_project))
    app.add_handler(CommandHandler("projects", projects))

    print("NFT Mint Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
