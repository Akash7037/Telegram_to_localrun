import time
import telebot
from .config import Config
from .logger import logger
from .classifier import IntentClassifier
from .executor import CommandExecutor

class TelegramListener:
    def __init__(self):
        self.bot = telebot.TeleBot(Config.TELEGRAM_BOT_TOKEN)
        self.classifier = IntentClassifier()
        self.is_running = False

        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            if message.chat.id != Config.WHITELISTED_CHAT_ID:
                logger.warning(f"Ignored message from unauthorized user: {message.chat.id}")
                return

            text = message.text
            logger.info(f"Received message: {text}")
            
            try:
                classification = self.classifier.classify(text)
                
                if classification.get("type") == "command":
                    action = classification.get("action")
                    params = classification.get("params", {})
                    result = CommandExecutor.execute(action, params)
                    self.bot.reply_to(message, f"✅ {result}")
                else:
                    # For casual, we just log it as per requirements
                    logger.info(f"Casual chat: {text}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                self.bot.reply_to(message, "❌ Sorry, I encountered an error processing that.")

    def start(self):
        if not self.is_running:
            logger.info("Starting Telegram Listener...")
            self.is_running = True
            # We use a custom loop instead of infinity_polling to allow for external pausing
            while self.is_running:
                try:
                    self.bot.polling(non_stop=False, interval=1, timeout=Config.POLLING_TIMEOUT)
                except Exception as e:
                    logger.error(f"Polling error: {str(e)}. Retrying in 10s...")
                    time.sleep(10)

    def stop(self):
        logger.info("Stopping Telegram Listener...")
        self.is_running = False
        self.bot.stop_polling()
