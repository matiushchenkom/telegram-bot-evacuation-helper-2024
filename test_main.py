import unittest
from unittest.mock import MagicMock
from telegram import Update, Message, CallbackQuery, User, Contact
from telegram.ext import CallbackContext

# Import necessary classes and constants from the main bot file
from main import MainCommands, CompanionSearch, CHOOSING, PERSON_COUNT, SEEKING_COMPANION, DEPARTURE, TELEGRAM_ID

class TestTelegramBot(unittest.TestCase):
    """Unit tests for Telegram bot command handlers and conversation logic."""

    def setUp(self):
        """ Set up mock objects for Telegram Update and CallbackContext before each test."""
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=CallbackContext)

        # Mocking message and callback query objects
        self.message = MagicMock(spec=Message)
        self.callback_query = MagicMock(spec=CallbackQuery)

        self.update.message = self.message
        self.update.callback_query = self.callback_query

        # Mocking a Telegram user
        self.user = MagicMock(spec=User)
        self.user.id = 123456
        self.update.effective_user = self.user

    def test_start_command(self):
        """Test the /start command handler."""
        self.message.reply_text = MagicMock()
        result = MainCommands.start(self.update, self.context)
        
        # Verify that a greeting message was sent
        self.message.reply_text.assert_called_once()
        # ConversationHandler.END is usually -1
        self.assertEqual(result, -1)

    def test_choose_command(self):
        """Test the /choose command which presents the main menu."""
        self.message.reply_text = MagicMock()
        result = MainCommands.choose(self.update, self.context)
        
        # Verify that the menu was displayed and state transitioned to CHOOSING
        self.message.reply_text.assert_called_once()
        self.assertEqual(result, CHOOSING)

    def test_button_option_1(self):
        """Test clicking the 'Looking for a ride' inline button."""
        self.callback_query.data = 'option_1'
        self.callback_query.answer = MagicMock()
        self.callback_query.message.reply_text = MagicMock()

        result = MainCommands.button(self.update, self.context)

        # Ensure the callback was acknowledged and handled
        self.callback_query.answer.assert_called_once()
        self.callback_query.message.reply_text.assert_called_once()
        self.assertEqual(result, SEEKING_COMPANION)

    def test_seeking_companion(self):
        """Test the transition to asking for the number of passengers."""
        self.message.reply_text = MagicMock()
        self.context.user_data = {}

        result = CompanionSearch.seeking_companion(self.update, self.context)

        # Verify state data storage and transition to PERSON_COUNT state
        self.message.reply_text.assert_called_once()
        self.assertEqual(self.context.user_data['choice'], '🔍ШУКАЮ ПОПУТНИКА🚗')
        self.assertEqual(result, PERSON_COUNT)

    def test_person_count(self):
        """Test input processing for the number of persons."""
        self.message.text = '3'
        self.message.reply_text = MagicMock()
        self.context.user_data = {}

        result = CompanionSearch.person_count(self.update, self.context)

        # Verify that the count was saved and bot asks for departure location
        self.assertEqual(self.context.user_data['person_count'], '3')
        self.message.reply_text.assert_called_once()
        self.assertEqual(result, DEPARTURE)

    def test_phone_number_with_contact(self):
        """Test phone number submission using the built-in Telegram contact share button."""
        contact = Contact(phone_number='+380123456789', user_id=123456, first_name='Test')
        self.message.contact = contact
        self.message.reply_text = MagicMock()
        self.context.user_data = {}

        result = CompanionSearch.phone_number(self.update, self.context)

        # Verify that the phone number was extracted correctly from the Contact object
        self.assertEqual(self.context.user_data['phone_number'], '+380123456789')
        self.message.reply_text.assert_called_once()
        self.assertEqual(result, TELEGRAM_ID)

    def test_phone_number_without_contact(self):
        """Test phone number submission via manual text entry."""
        self.message.contact = None
        self.message.text = '+380987654321'
        self.message.reply_text = MagicMock()
        self.context.user_data = {}

        result = CompanionSearch.phone_number(self.update, self.context)

        # Verify that the text input was saved as the phone number
        self.assertEqual(self.context.user_data['phone_number'], '+380987654321')
        self.message.reply_text.assert_called_once()

# Run all defined tests
if __name__ == '__main__':
    unittest.main()
