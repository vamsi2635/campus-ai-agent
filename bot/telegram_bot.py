import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from dotenv import load_dotenv
from core.extractor import extract_document_data
from core.database import record_entry

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# In-memory queue to track unconfirmed documents
pending_queue = {}

async def handle_document_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming paperwork scans and alerts administrative supervisors."""
    await update.message.reply_text("📄 Document received. Processing through AI Engine... Please wait.")

    photo = update.message.photo[-1]
    file_obj = await photo.get_file()
    temp_filename = f"temp_{update.message.message_id}.jpg"
    await file_obj.download_to_drive(temp_filename)

    try:
        extracted_data = extract_document_data(temp_filename)
        task_id = str(update.message.message_id)
        pending_queue[task_id] = extracted_data

        doc_type = extracted_data.get("document_type", "General Paperwork")
        name = extracted_data.get("student_or_vendor_name", "N/A")
        ref_no = extracted_data.get("identifier_number", "N/A")
        metric = extracted_data.get("academic_metric", "N/A")
        amount = extracted_data.get("primary_amount", 0.0)
        branch = extracted_data.get("department_or_branch", "General")

        admin_summary = (
            f"🔔 **Document Verification Request**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📂 **Document Type:** {doc_type}\n"
            f"👤 **Name:** {name}\n"
            f"🔢 **Roll / Challan / ID:** {ref_no}\n"
            f"🎓 **Branch / Department:** {branch}\n"
            f"📊 **Academic Metric:** {metric}\n"
            f"💰 **Fee / Total Amount:** ₹{amount:,.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Approve recording this record into the campus master ledger?"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{task_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{task_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        target_chat = ADMIN_CHAT_ID if ADMIN_CHAT_ID else update.effective_chat.id
        await context.bot.send_message(
            chat_id=target_chat,
            text=admin_summary,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Document processing error: {str(e)}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

async def process_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes ledger insertion or rejection based on supervisor action."""
    query = update.callback_query
    await query.answer()

    action, task_id = query.data.split("_")
    record = pending_queue.get(task_id)

    if not record:
        await query.edit_message_text("⚠️ This request has expired or has already been processed.")
        return

    name = record.get("student_or_vendor_name", "Unknown Candidate")
    doc_type = record.get("document_type", "Document")

    if action == "approve":
        record_entry(record, status="Approved")
        await query.edit_message_text(
            f"✅ **Entry Approved**\n\n"
            f"'{doc_type}' for **{name}** has been successfully committed to `campus_ledger.xlsx`."
        )
    else:
        record_entry(record, status="Rejected")
        await query.edit_message_text(
            f"❌ **Entry Rejected**\n\n"
            f"Record for **{name}** was marked as rejected in the audit log."
        )

    pending_queue.pop(task_id, None)

def start_bot():
    """Initializes and runs the Telegram Bot polling loop."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: Missing TELEGRAM_BOT_TOKEN in .env file.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.PHOTO, handle_document_incoming))
    application.add_handler(CallbackQueryHandler(process_approval_callback))

    print("🤖 CampusOS Supervisor Bot is online and listening for incoming documents...")
    application.run_polling()

if __name__ == "__main__":
    start_bot()