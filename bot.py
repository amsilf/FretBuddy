import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
import config
import fretboard

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
MAIN_MENU = 0
SELECTING_FRET = 1
PLAYING_GAME = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    # Create vertical keyboard layout with inline buttons
    keyboard = [
        [InlineKeyboardButton(str(fret), callback_data=f"fret_{fret}")]
        for fret in config.FRET_OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if the update is from a command or a callback query
    if update.message:
        await update.message.reply_text(
            "Welcome to Guitar Fretboard Learning Bot! 🎸\n\n"
            "I'll help you learn the notes on your guitar fretboard.\n"
            "Please select the maximum fret you want to practice:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Welcome to Guitar Fretboard Learning Bot! 🎸\n\n"
            "I'll help you learn the notes on your guitar fretboard.\n"
            "Please select the maximum fret you want to practice:",
            reply_markup=reply_markup
        )
    return SELECTING_FRET 

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button presses for fret selection."""
    query = update.callback_query
    await query.answer()
    
    # Extract fret number from callback data
    selected_fret = int(query.data.split('_')[1])
    
    # Generate first question
    fretboard_visual, string_num, fret_num, correct_note = fretboard.create_question(
        selected_fret,
        orientation=context.user_data.get('orientation', 'vertical'),
        mode=context.user_data.get('mode', 'show')
    )
    
    # Store correct answer in context
    context.user_data['max_fret'] = selected_fret
    context.user_data['correct_note'] = correct_note
    context.user_data['attempts'] = 0
    context.user_data['string_num'] = string_num
    context.user_data['fret_num'] = fret_num
    
    # Initialize session statistics
    context.user_data['stats'] = {
        'correct_answers': 0,
        'wrong_answers': 0,
        'total_questions': 0,
        'questions_with_hints': 0  # Questions where user needed a second attempt
    }
    
    # Create keyboard with End Session button
    keyboard = [[InlineKeyboardButton("End Session", callback_data="game_end")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Use edit_message_text to update the existing message
    await query.message.edit_text(
        f"Great! Let's practice with {selected_fret} frets.\n"
        "What note is marked with '?' on the fretboard?\n\n"
        f"```\n{fretboard_visual}\n```",
        reply_markup=reply_markup
    )
    
    return PLAYING_GAME

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's answer and provide feedback."""
    user_answer = fretboard.format_note_name(update.message.text)
    correct_note = context.user_data['correct_note']
    string_num = context.user_data['string_num']
    fret_num = context.user_data['fret_num']
    
    # Update total questions count on first attempt
    if context.user_data['attempts'] == 0:
        context.user_data['stats']['total_questions'] += 1
    
    if user_answer == correct_note:
        # Create keyboard with End Session button
        keyboard = [[InlineKeyboardButton("End Session", callback_data="game_end")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update statistics for correct answer
        if context.user_data['attempts'] == 0:
            context.user_data['stats']['correct_answers'] += 1
        
        await update.message.reply_text(
            f"🎉 Correct! The note at fret {fret_num} on string {string_num} is {correct_note}.\n\n"
            "Let's try another one!"
        )
        
        # Generate new question
        fretboard_visual, string_num, fret_num, correct_note = fretboard.create_question(
            context.user_data['max_fret'],
            orientation=context.user_data.get('orientation', 'vertical'),
            mode=context.user_data.get('mode', 'show')
        )
        
        # Update context with new question
        context.user_data['correct_note'] = correct_note
        context.user_data['attempts'] = 0
        context.user_data['string_num'] = string_num
        context.user_data['fret_num'] = fret_num
        
        await update.message.reply_text(
            "What note is marked with '?' on the fretboard?\n\n"
            f"```\n{fretboard_visual}\n```",
            reply_markup=reply_markup
        )
    else:
        # Wrong answer
        context.user_data['attempts'] += 1
        if context.user_data['attempts'] >= 2:
            # Update statistics for wrong answer and hint usage
            context.user_data['stats']['wrong_answers'] += 1
            context.user_data['stats']['questions_with_hints'] += 1
            
            await update.message.reply_text(
                f"The correct answer was {correct_note}. Let's try a new one!"
            )
            
            # Generate new question after two failed attempts
            fretboard_visual, string_num, fret_num, correct_note = fretboard.create_question(
                context.user_data['max_fret'],
                orientation=context.user_data.get('orientation', 'vertical'),
                mode=context.user_data.get('mode', 'show')
            )
            
            # Update context with new question
            context.user_data['correct_note'] = correct_note
            context.user_data['attempts'] = 0
            context.user_data['string_num'] = string_num
            context.user_data['fret_num'] = fret_num
            
            await update.message.reply_text(
                "What note is marked with '?' on the fretboard?\n\n"
                f"```\n{fretboard_visual}\n```"
            )
        else:
            await update.message.reply_text(
                "That's not correct. Try again! 🎸"
            )
    
    return PLAYING_GAME

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Guitar Fretboard Learning Bot Help:\n\n"
        "/start - Start learning\n"
        "/setfret - Change maximum fret number\n"
        "/help - Show this help message"
    )

async def setfret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /setfret command to change the maximum fret."""
    # Create vertical keyboard layout with inline buttons
    keyboard = [
        [InlineKeyboardButton(str(fret), callback_data=f"fret_{fret}")]
        for fret in config.FRET_OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select the maximum fret you want to practice:",
        reply_markup=reply_markup
    )
    return SELECTING_FRET

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display settings menu for orientation and mode selection."""
    keyboard = [
        [InlineKeyboardButton("Orientation: Vertical", callback_data="orientation_vertical"),
         InlineKeyboardButton("Orientation: Horizontal", callback_data="orientation_horizontal")],
        [InlineKeyboardButton("Mode: Show Notes", callback_data="mode_show"),
         InlineKeyboardButton("Mode: Hide Notes", callback_data="mode_hide")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if the update is from a command or a callback query
    if update.message:
        await update.message.reply_text(
            "Choose your settings:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Choose your settings:",
            reply_markup=reply_markup
        )

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle settings selection."""
    query = update.callback_query
    await query.answer()
    
    # Update user settings based on selection
    if query.data.startswith("orientation_"):
        context.user_data['orientation'] = query.data.split('_')[1]
        await query.message.edit_text(
            f"Settings updated: Orientation - {context.user_data.get('orientation', 'vertical')}, "
            f"Mode - {context.user_data.get('mode', 'show')}"
        )
        return MAIN_MENU
    elif query.data.startswith("mode_"):
        context.user_data['mode'] = query.data.split('_')[1]
        await query.message.edit_text(
            f"Settings updated: Orientation - {context.user_data.get('orientation', 'vertical')}, "
            f"Mode - {context.user_data.get('mode', 'show')}"
        )
        return MAIN_MENU
    elif query.data == "menu_main":
        # Create main menu keyboard
        keyboard = [
            [InlineKeyboardButton("Start", callback_data="menu_start")],
            [InlineKeyboardButton("Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("Quit", callback_data="menu_quit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            "Main Menu:",
            reply_markup=reply_markup
        )
        return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the main menu with options to start, access settings, or quit."""
    keyboard = [
        [InlineKeyboardButton("Start", callback_data="menu_start")],
        [InlineKeyboardButton("Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("Quit", callback_data="menu_quit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "Main Menu:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            "Main Menu:",
            reply_markup=reply_markup
        )
    return MAIN_MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu selection."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_start":
        # Create fret selection keyboard
        keyboard = [
            [InlineKeyboardButton(str(fret), callback_data=f"fret_{fret}")]
            for fret in config.FRET_OPTIONS
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            "Please select the maximum fret you want to practice:",
            reply_markup=reply_markup
        )
        return SELECTING_FRET
    elif query.data == "menu_settings":
        await settings(update, context)
        return MAIN_MENU
    elif query.data == "menu_quit":
        await query.message.edit_text("Goodbye! 👋")
        return ConversationHandler.END

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle game-related callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "game_end":
        # Get statistics
        stats = context.user_data.get('stats', {
            'correct_answers': 0,
            'wrong_answers': 0,
            'total_questions': 0,
            'questions_with_hints': 0
        })
        
        # Calculate accuracy
        total_questions = stats['total_questions']
        correct_answers = stats['correct_answers']
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Create statistics message
        stats_message = (
            "📊 Session Statistics:\n\n"
            f"Total Questions: {total_questions}\n"
            f"Correct Answers: {correct_answers}\n"
            f"Wrong Answers: {stats['wrong_answers']}\n"
            f"Questions with Hints: {stats['questions_with_hints']}\n"
            f"Accuracy: {accuracy:.1f}%\n\n"
            "Training session ended. Back to main menu:"
        )
        
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("Start", callback_data="menu_start")],
            [InlineKeyboardButton("Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("Quit", callback_data="menu_quit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            stats_message,
            reply_markup=reply_markup
        )
        return MAIN_MENU
    
    return PLAYING_GAME

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", main_menu)
        ],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(menu_handler, pattern=r"^menu_"),
                CallbackQueryHandler(settings_handler, pattern=r"^(orientation|mode)_")
            ],
            SELECTING_FRET: [
                CallbackQueryHandler(button_handler, pattern=r"^fret_\d+$")
            ],
            PLAYING_GAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_answer
                ),
                CallbackQueryHandler(game_handler, pattern=r"^game_")
            ]
        },
        fallbacks=[
            CommandHandler("start", main_menu)
        ]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 