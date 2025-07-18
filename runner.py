from telegram_bot import TelegramBot


class Runner:
    @staticmethod
    def run(self):
        telegram_bot = TelegramBot()
        telegram_bot.setup_handlers()
        telegram_bot.start_polling()


if __name__ == '__main__':
    Runner().run()
