import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHANNEL_USERNAME = "@loopahub"  # Your channel username
CHANNEL_LINK = "https://t.me/loopahub"

async def is_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user is a member of the channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # Statuses that mean the user is in the channel
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership for {user_id}: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = update.effective_user.id
    
    if await is_member(user_id, context):
        # User is a member
        keyboard = [
            [InlineKeyboardButton("📢 Go to Channel", url=CHANNEL_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Welcome to Loopa, {update.effective_user.first_name}! 🚀\n\n"
            "You are verified. Stay tuned for the best content from Loopa Hub.",
            reply_markup=reply_markup
        )
    else:
        # User is not a member, ask to join
        keyboard = [
            [InlineKeyboardButton("1️⃣ Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("2️⃣ Check Verification", callback_data="check_join")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ **Access Denied**\n\n"
            "You must join our official channel to use Loopa.\n"
            "Please click the button below to join, then click 'Check Verification'.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Check Verification' button click."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if await is_member(user_id, context):
        # User has joined
        keyboard = [
            [InlineKeyboardButton("📢 Go to Channel", url=CHANNEL_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="✅ **Verification Successful!**\n\nWelcome to Loopa! You can now use the bot.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # Still not joined
        await query.answer("❌ You haven't joined the channel yet. Please join first!", show_alert=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "Commands available:\n"
        "/start - Join and verify access\n"
        "/help - Show this message"
    )

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return

    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))

    # Run the bot (Long Polling)
    logger.info("Starting Loopa bot with long polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
