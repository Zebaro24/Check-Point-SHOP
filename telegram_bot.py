from telebot import TeleBot, types

from database import Database
from handlers.client_handler import ClientHandler
from handlers.admin_handler import AdminHandler
from handlers.base_handler import BaseHandler
from config import *

from time import sleep


class TelegramBot(TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_TOKEN)
        self.db = Database(DATABASE_URL)
        self.db.connect()

        self.admins, self.clients, self.products = self.db.get_all_data()
        print(self.admins)
        print(self.clients)
        print(self.products)

        self.main_markup = self.get_main_markup()

        self.my_photo = None

    @staticmethod
    def get_cancel_markup(leave=False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if not leave:
            markup.add(types.KeyboardButton(TEXT_BUTTON_CANCEL))
        elif leave:
            markup.add(types.KeyboardButton(ADMIN_TEXT_BUTTON_LEAVE))
        return markup

    def get_main_markup(self, admin_id=None):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        markup.add(types.KeyboardButton(TEXT_BUTTON_PRODUCTS))

        if not admin_id:
            markup.add(types.KeyboardButton(TEXT_BUTTON_ACCOUNT))
            markup.add(types.KeyboardButton(TEXT_BUTTON_BUY))
        else:
            markup.add(types.KeyboardButton(ADMIN_TEXT_BUTTON_ADD_PRODUCT))

            orders = self.db.get_admin_assigned_orders_ws_clients(admin_id)

            for order in orders:
                markup.add(types.KeyboardButton(order.get_admin_button_text()))

        return markup

    def send_possibilities(self, chat_id, admin=False):
        if admin:
            self.send_message(chat_id, "Вот ваши возможности Admin:", reply_markup=self.get_main_markup(chat_id))
            return
        self.send_message(chat_id, "Вот ваши возможности:", reply_markup=self.main_markup)

    # <--- Handlers --->
    def start_command(self, message: types.Message):
        self.delete_message(message.chat.id, message.message_id)
        self.send_sticker(message.chat.id, START_STICKER)
        sleep(0.5)
        self.send_message(message.chat.id, START_MESSAGE_FIRST)
        sleep(1)
        self.send_message(message.chat.id, START_MESSAGE_SECOND)
        if message.chat.id not in self.admins | self.clients:
            sleep(0.5)
            self.send_message(message.chat.id, REGISTRATION_MESSAGE, reply_markup=types.ForceReply())
            return
        self.send_possibilities(message.chat.id, message.chat.id in self.admins)

    def handle_message(self, chat_id, trans_data, startswith_handler):
        if chat_id in self.admins:
            admin = self.admins[chat_id]
            trans_data["person"] = admin
            if admin.status:
                trans_data["status"] = admin.status
            AdminHandler.process_text_handlers(startswith_handler, **trans_data)
        elif chat_id in self.clients:
            client = self.clients[chat_id]
            trans_data["person"] = client
            if client.status:
                trans_data["status"] = client.status
            ClientHandler.process_text_handlers(startswith_handler, **trans_data)
        else:
            BaseHandler.process_text_handlers(startswith_handler, **trans_data)

    def handle_text_message(self, message: types.Message):
        # (text, person, db, user_id, bot, status:opc)
        trans_data = {
            "text": message.text,
            "db": self.db,
            "user_id": message.chat.id,
            "bot": self,
            "message": message,
        }
        self.handle_message(message.chat.id, trans_data, "handle_text")

    def handle_photo_message(self, message: types.Message):
        # (text, person, db, user_id, bot, status:opc)
        trans_data = {
            "photo": message.photo[0],
            "db": self.db,
            "user_id": message.chat.id,
            "bot": self,
            "message": message,
        }
        self.handle_message(message.chat.id, trans_data, "handle_photo")

    def handle_callback_query(self, call):
        # (text, person, db, user_id, bot, status:opc)
        trans_data = {
            "data": call.data,
            "db": self.db,
            "user_id": call.message.chat.id,
            "bot": self,
            "message": call.message,
            "call": call,
        }
        self.handle_message(call.message.chat.id, trans_data, "handle_callback")

    # <--- Work Methods --->
    def setup_handlers(self):
        # Настройка всех обработчиков команд
        @self.message_handler(commands=['start', 'help'])
        def handle_start_help(message: types.Message):
            print(f"Старт от {message.chat.first_name}")
            self.start_command(message)

        @self.message_handler(func=lambda message: True)
        def handle_all_messages(message: types.Message):
            print(f"Сообщение от {message.chat.first_name} содержит \"{message.text}\"")
            self.handle_text_message(message)

        @self.message_handler(content_types=['photo'])
        def handle_photo(message: types.Message):
            print(f"Фото от {message.chat.first_name} фото {message.photo[0]}")
            self.handle_photo_message(message)

        @self.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            print(f"Нажатие кнопки от {call.message.chat.first_name} на {call.data}")
            self.handle_callback_query(call)

    def start_polling(self):
        # Запуск бота
        print("Бот запущен!")
        try:
            self.polling()  # Убрать restart_on_change
        except KeyboardInterrupt:
            print("Бот был остановлен!")
        finally:
            self.db.session.close()


if __name__ == '__main__':
    telegram_bot = TelegramBot()
    telegram_bot.setup_handlers()
    telegram_bot.start_polling()
