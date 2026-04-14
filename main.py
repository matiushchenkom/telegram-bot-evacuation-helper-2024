from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
import logging

# ConversationHandler states
(
    CHOOSING, SEEKING_COMPANION, CAR_OWNER, EVACUATION, 
    PERSON_COUNT, DEPARTURE, DESTINATION, TRAVEL_DATE, 
    COMMENT, PHONE_NUMBER, TELEGRAM_ID, 
    PERSON_COUNT_EVACUATION, NAMES_EVACUATION, 
    DEPARTURE_EVACUATION, COMMENT_EVACUATION, 
    PHONE_NUMBER_EVACUATION, TELEGRAM_ID_EVACUATION
) = range(17)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainCommands:
    """Handles core bot commands and navigation."""
    
    @staticmethod
    def start(update: Update, context: CallbackContext) -> int:
        """Greeting message and bot description."""
        update.message.reply_text(
            '👋 Hello! I am a chatbot for finding travel companions in Ukraine. 🔍🚌\n\n'
            '🚨 We also help create posts to find volunteers for evacuation from occupied and frontline territories.📢🚑\n\n'
            'Looking for a ride? Have free seats? 🧳🚙 Or need help with evacuation? 🚨\n'
            'Create your post for our Telegram channel right now!\n\n Press /choose to select options. 🔍✨'
        )
        return ConversationHandler.END

    @staticmethod
    def choose(update: Update, context: CallbackContext) -> int:
        """Initial choice menu with inline buttons."""
        keyboard = [
            [InlineKeyboardButton("🔍 LOOKING FOR A RIDE🚗", callback_data='option_1')],
            [InlineKeyboardButton("🔍 I AM A DRIVER. OFFERING A RIDE🚗", callback_data='option_2')],
            [InlineKeyboardButton("🚨 NEED EVACUATION. URGENT!📢", callback_data='option_3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Which option applies to you? Please select:', reply_markup=reply_markup)
        return CHOOSING

    @staticmethod
    def button(update: Update, context: CallbackContext) -> int:
        """Processes callback queries from the choice menu."""
        query = update.callback_query
        query.answer()

        follow_up_map = {
            'option_1': SEEKING_COMPANION,
            'option_2': CAR_OWNER,
            'option_3': EVACUATION
        }

        state = follow_up_map.get(query.data)
        if state is not None:
            query.message.reply_text(
                'Are you sure you want to create a post? 🤔\n\n'
                'Enter ANYTHING to confirm (e.g., ✅).\n'
                'To cancel, press /cancel ❌'
            )
            return state
        return CHOOSING

    @staticmethod
    def cancel(update: Update, context: CallbackContext) -> int:
        """Ends the conversation and resets the bot state."""
        update.message.reply_text(
            'Action cancelled. \n\n'
            'To return to the main MENU - press /choose 🔄\n'
            'To restart the bot from the beginning - press /start 🚀'
        )
        return ConversationHandler.END

class CompanionSearch:
    """Logic for standard travel companion matching (Drivers/Passengers)."""

    @staticmethod
    def seeking_companion(update: Update, context: CallbackContext) -> int:
        """Starts the ride-seeking flow."""
        context.user_data['choice'] = '🔍 PASSENGER SEARCHING FOR RIDE 🚗'
        update.message.reply_text(
            "Great! I will help you create a post.\n\n"
            "❗️❗️❗️ All posts are moderated. Incorrect forms will be deleted. ❗️❗️❗️\n\n"
            "👩‍👦 How many people are traveling? 👨‍👩‍👧‍👦",
            reply_markup=ReplyKeyboardMarkup([[str(i)] for i in range(1, 11)], one_time_keyboard=True)
        )
        return PERSON_COUNT

    @staticmethod
    def car_owner(update: Update, context: CallbackContext) -> int:
        """Starts the driver flow."""
        context.user_data['choice'] = '🔍 DRIVER OFFERING A RIDE 🚗'
        update.message.reply_text(
            "Great! I will help you find passengers.\n\n"
            "!! All posts are moderated. Please fill out the form correctly. !!\n\n"
            "How many people can you take in your car?",
            reply_markup=ReplyKeyboardMarkup([[str(i)] for i in range(1, 11)], one_time_keyboard=True)
        )
        return PERSON_COUNT

    @staticmethod
    def person_count(update: Update, context: CallbackContext) -> int:
        """Records seat/person count and asks for departure point."""
        context.user_data['person_count'] = update.message.text
        update.message.reply_text(
            "Where are you departing from?🏬\n\n Specify the location (e.g., Kyiv, Central Station 🏫)\n"
            "If it is a village, include the region (e.g., Kyiv region, Kalynivka 🏡)\n\n"
            "Your address:"
        )
        return DEPARTURE

    @staticmethod
    def departure(update: Update, context: CallbackContext) -> int:
        """Records departure and asks for destination."""
        context.user_data['departure'] = update.message.text
        update.message.reply_text(
            "Where are you going?🚘\n\n Specify the destination (e.g., Lviv, Center 🏦)\n\n"
            "Your answer:"
        )
        return DESTINATION

    @staticmethod
    def destination(update: Update, context: CallbackContext) -> int:
        """Records destination and asks for travel date."""
        context.user_data['destination'] = update.message.text
        update.message.reply_text("Travel date?📅\n\n Format: DD.MM.YYYY (e.g., 30.09.2023)")
        return TRAVEL_DATE

    @staticmethod
    def travel_date(update: Update, context: CallbackContext) -> int:
        """Records date and asks for additional comments."""
        context.user_data['travel_date'] = update.message.text
        update.message.reply_text(
            "Add a comment to your post. 💬\n\n"
            "You can mention car model, price, pet preferences, etc. 💸🐕\n\n"
            "Comment:"
        )
        return COMMENT

    @staticmethod
    def comment(update: Update, context: CallbackContext) -> int:
        """Records comment and requests contact phone number."""
        context.user_data['comment'] = update.message.text
        update.message.reply_text(
            "☎️ Provide your phone number for contact:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Share phone number📲", request_contact=True)]],
                one_time_keyboard=True
            )
        )
        return PHONE_NUMBER

    @staticmethod
    def phone_number(update: Update, context: CallbackContext) -> int:
        """Handles phone number input (via contact button or text)."""
        contact = update.message.contact
        if contact:
            context.user_data['phone_number'] = contact.phone_number
        else:
            context.user_data['phone_number'] = update.message.text
        
        update.message.reply_text("📱 Provide your Telegram ID (e.g., @username):")
        return TELEGRAM_ID

    @staticmethod
    def telegram_id(update: Update, context: CallbackContext) -> int:
        """Finalizes the ride post and sends it to the target channel."""
        context.user_data['telegram_id'] = update.message.text
        user_data = context.user_data
        post = (
            f"{user_data.get('choice', 'Unknown')}\n"
            f"👥 Persons: {user_data.get('person_count', 'Unknown')}\n"
            f"📍 From: {user_data.get('departure', 'Unknown')}\n"
            f"🏁 To: {user_data.get('destination', 'Unknown')}\n"
            f"📅 Date: {user_data.get('travel_date', 'Unknown')}\n"
            f"💬 Comment: {user_data.get('comment', 'No comment')}\n"
            f"☎️ Phone: {user_data.get('phone_number', 'Unknown')}\n"
            f"📱 Telegram: {user_data.get('telegram_id', 'Unknown')}"
        )
        update.message.reply_text("Post created and sent to the main channel:\n\n" + post)
        
        # Send post to the specific Telegram Channel
        chat_id = '-1002009177529'
        context.bot.send_message(chat_id=chat_id, text=post)
        
        update.message.reply_text('To return to MENU - /choose\nTo restart - /start')
        return ConversationHandler.END

class EvacuationHelp:
    """Special logic for handling emergency evacuation requests."""

    @staticmethod
    def evacuation(update: Update, context: CallbackContext) -> int:
        """Starts the evacuation request flow."""
        context.user_data['choice'] = '🚨 EVACUATION NEEDED 📢'
        update.message.reply_text(
            "Understood! I will help you create an evacuation request for occupied or frontline areas. 🙏🚨\n\n"
            "This post will be shared with volunteer organizations. 🚑\n\n"
            "❗️❗️❗️ Moderation active. False reports will result in a ban. ❗️❗️❗️\n\n"
            "👩‍👦 How many people need evacuation?",
            reply_markup=ReplyKeyboardMarkup([[str(i)] for i in range(1, 11)], one_time_keyboard=True)
        )
        return PERSON_COUNT_EVACUATION

    @staticmethod
    def person_count_evacuation(update: Update, context: CallbackContext) -> int:
        """Asks for the names and ages of people to be evacuated."""
        context.user_data['person_count_evacuation'] = update.message.text
        update.message.reply_text("👨‍👩‍👧 Provide the full list of names and ages (Full Name, Age):")
        return NAMES_EVACUATION

    @staticmethod
    def names_evacuation(update: Update, context: CallbackContext) -> int:
        """Asks for specific evacuation address."""
        context.user_data['names_evacuation'] = update.message.text
        update.message.reply_text(
            "🏢 Where do you need evacuation from? 🏥\n\n"
            "Provide full address: City, Street, Apt #\n\n"
            "Your address: "
        )
        return DEPARTURE_EVACUATION

    @staticmethod
    def departure_evacuation(update: Update, context: CallbackContext) -> int:
        """Asks for critical medical or logistics info."""
        context.user_data['departure_evacuation'] = update.message.text
        update.message.reply_text(
            "💬 Provide additional comments.\n\n"
            "Mention disabilities, injuries, pets, or any CRITICAL information. 🚨👨🏻‍🦽🤰🏼\n\n"
            "Your comment:"
        )
        return COMMENT_EVACUATION

    @staticmethod
    def comment_evacuation(update: Update, context: CallbackContext) -> int:
        """Requests contact info for evacuation."""
        context.user_data['comment_evacuation'] = update.message.text
        update.message.reply_text(
            "☎️ Provide your phone number:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Share phone number📲", request_contact=True)]],
                one_time_keyboard=True
            )
        )
        return PHONE_NUMBER_EVACUATION

    @staticmethod
    def phone_number_evacuation(update: Update, context: CallbackContext) -> int:
        """Processes phone for evacuation."""
        contact = update.message.contact
        if contact:
            context.user_data['phone_number_evacuation'] = contact.phone_number
        else:
            context.user_data['phone_number_evacuation'] = update.message.text

        update.message.reply_text("📱 Provide your Telegram ID:")
        return TELEGRAM_ID_EVACUATION

    @staticmethod
    def telegram_id_evacuation(update: Update, context: CallbackContext) -> int:
        """Finalizes and broadcasts the emergency evacuation post."""
        context.user_data['telegram_id_evacuation'] = update.message.text
        user_data = context.user_data
        post1 = (
            f"{user_data.get('choice', 'Unknown')}\n"
            f"👨‍👩‍👦‍👦 Persons: {user_data.get('person_count_evacuation', 'Unknown')}\n"
            f"👥 Names: {user_data.get('names_evacuation', 'Unknown')}\n"
            f"📍 From: {user_data.get('departure_evacuation', 'Unknown')}\n"
            f"💬 Comment: {user_data.get('comment_evacuation', 'No comment')}\n"
            f"📱 Phone: {user_data.get('phone_number_evacuation', 'Unknown')}\n"
            f"📱 Telegram: {user_data.get('telegram_id_evacuation', 'Unknown')}"
        )
        update.message.reply_text("Evacuation post created:\n\n" + post1)
        
        # Broadcast to channel and volunteer organizations
        chat_id = '-1002009177529'
        context.bot.send_message(chat_id=chat_id, text=post1)
        
        update.message.reply_text('To return to MENU - /choose\nTo restart - /start')
        return ConversationHandler.END

class Bot:
    """Main Bot class to initialize and run the Telegram bot."""
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.add_handlers()

    def add_handlers(self):
        """Register all conversation and command handlers."""
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', MainCommands.start), CommandHandler('choose', MainCommands.choose)],
            states={
                CHOOSING: [CallbackQueryHandler(MainCommands.button)],
                SEEKING_COMPANION: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.seeking_companion)],
                CAR_OWNER: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.car_owner)],
                EVACUATION: [MessageHandler(Filters.text & ~Filters.command, EvacuationHelp.evacuation)],
                PERSON_COUNT: [MessageHandler(Filters.regex('^\d+$'), CompanionSearch.person_count)],
                DEPARTURE: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.departure)],
                DESTINATION: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.destination)],
                TRAVEL_DATE: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.travel_date)],
                COMMENT: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.comment)],
                PHONE_NUMBER: [MessageHandler(Filters.contact | (Filters.text & ~Filters.command), CompanionSearch.phone_number)],
                TELEGRAM_ID: [MessageHandler(Filters.text & ~Filters.command, CompanionSearch.telegram_id)],
                PERSON_COUNT_EVACUATION: [MessageHandler(Filters.regex('^\d+$'), EvacuationHelp.person_count_evacuation)],
                NAMES_EVACUATION: [MessageHandler(Filters.text & ~Filters.command, EvacuationHelp.names_evacuation)],
                DEPARTURE_EVACUATION: [MessageHandler(Filters.text & ~Filters.command, EvacuationHelp.departure_evacuation)],
                COMMENT_EVACUATION: [MessageHandler(Filters.text & ~Filters.command, EvacuationHelp.comment_evacuation)],
                PHONE_NUMBER_EVACUATION: [MessageHandler(Filters.contact | (Filters.text & ~Filters.command), EvacuationHelp.phone_number_evacuation)],
                TELEGRAM_ID_EVACUATION: [MessageHandler(Filters.text & ~Filters.command, EvacuationHelp.telegram_id_evacuation)]
            },
            fallbacks=[CommandHandler('cancel', MainCommands.cancel)]
        )
        self.dispatcher.add_handler(conv_handler)

    def start(self):
        """Starts the long-polling process."""
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    # It is recommended to use environment variables for the TOKEN for security
    bot = Bot("BOT_TOKEN")
    bot.start()
