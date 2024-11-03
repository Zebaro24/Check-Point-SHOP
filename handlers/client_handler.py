import telebot

from config import *
from telebot import TeleBot, types

from handlers.base_handler import BaseHandler
from handlers.base_handler import set_handler_text, set_handler_status, set_handler_none, set_handler_callback


class ClientHandler(BaseHandler):
    @staticmethod
    @set_handler_text(TEXT_BUTTON_PRODUCTS)
    def handle_text_products(message, bot, person):
        for product in bot.products.values():
            if product.count <= 0:
                continue

            if product in person.order:
                caption = product.get_caption(person.order[product])
            else:
                caption = product.get_caption()

            markup = product.get_markup_client(product in person.order)
            bot.send_photo(message.chat.id, product.photo_id, caption, "Markdown", reply_markup=markup)

    @staticmethod
    @set_handler_text(TEXT_BUTTON_ACCOUNT)
    def handle_text_account(user_id, bot: TeleBot, person):
        text = f"Ваше ім'я: {person.name}\n"
        text += f"Ваша кімната: {person.location}\n\n"
        text += "Ось ваші дії по зміні профілю:"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(ACCOUNT_TEXT_BUTTON_EDIT_NAME))
        markup.add(types.KeyboardButton(ACCOUNT_TEXT_BUTTON_EDIT_LOCATION))

        bot.send_message(user_id, text, reply_markup=markup)

    @staticmethod
    @set_handler_text(ACCOUNT_TEXT_BUTTON_EDIT_NAME)
    def handle_text_account_name(user_id, bot, person):
        person.status = "account_edit name"
        bot.send_message(user_id, "Введіть нове ім'я:", reply_markup=bot.get_cancel_markup())

    @staticmethod
    @set_handler_text(ACCOUNT_TEXT_BUTTON_EDIT_LOCATION)
    def handle_text_account_location(user_id, bot, person):
        person.status = "account_edit location"
        bot.send_message(user_id, "Введіть нову кімнату:", reply_markup=bot.get_cancel_markup())

    @staticmethod
    @set_handler_status("account_edit")
    def handle_text_account_edit(status, text, user_id, db, bot, person):
        _, doing = status.split()
        if doing == "name":
            person.name = text
        elif doing == "location":
            person.location = text
        db.session.commit()
        bot.send_message(user_id, "Данні були змінені", reply_markup=bot.get_main_markup())
        person.status = None

    @staticmethod
    @set_handler_text(TEXT_BUTTON_CANCEL)
    def handle_text_cancel(user_id, bot, person):
        bot.send_message(user_id, "Действие было отменено", reply_markup=bot.get_main_markup())
        person.status = None

    @staticmethod
    @set_handler_callback(["sub", "clear", "add"])
    def handle_callback_edit(data, bot, person, user_id, message, call):
        doing, product_id = data.split()
        if person.status == "wait_confirm":
            bot.answer_callback_query(call.id, "Заказ уже на подтверждении!")
            return
        product_id = int(product_id)
        product = bot.products[product_id]
        if doing == "sub" and product in person.order:
            if person.order[product] <= 1:
                del person.order[product]
            elif person.order[product] > 1:
                person.order[product] -= 1
        elif doing == "clear" and product in person.order:
            del person.order[product]
        elif doing == "add":
            if product not in person.order:
                person.order[product] = 0

            if product.count < person.order[product] + 1:
                bot.answer_callback_query(call.id, "Мы не можем доставить товара больше чем есть")
                if not person.order[product]:
                    del person.order[product]
                return

            person.order[product] += 1

        markup = product.get_markup_client(product in person.order)

        if product in person.order:
            caption = product.get_caption(person.order[product])
        else:
            caption = product.get_caption()

        try:
            bot.edit_message_caption(caption, user_id, message.message_id, parse_mode="Markdown", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            bot.answer_callback_query(call.id, "Кнопка нажата!")

    @staticmethod
    @set_handler_text(TEXT_BUTTON_BUY)
    def handle_text_buy(user_id, bot, person):
        if not person.order:
            bot.send_message(user_id, "Заказ пуст")
            return
        text = person.get_order_list()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Отправить на подтверждение", callback_data="buy"))
        bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

    @staticmethod
    @set_handler_callback(["buy"])
    def handle_callback_buy(bot, person, user_id, message, db):
        if not person.order:
            bot.send_message(user_id, "Заказ пуст!")
            return
        text = person.get_order_list(True)
        order = db.add_order_by_client(person)
        markup = types.InlineKeyboardMarkup()
        confirm_done = types.InlineKeyboardButton(text="✅", callback_data=f"confirm done {order.id}")
        confirm_cancel = types.InlineKeyboardButton(text="❌", callback_data=f"confirm cancel {order.id}")
        markup.add(confirm_done, confirm_cancel)

        for admin in bot.admins:
            bot.send_message(admin, text, parse_mode="Markdown", reply_markup=markup)

        person.status = "wait_confirm"
        bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)
        bot.send_message(user_id, "Заказ отправлен на подтверждение!")

    @staticmethod
    @set_handler_status("wait_pay")
    def handle_photo_pay(photo, status, bot: TeleBot, person, db, user_id):
        id_order = int(status.split()[1])
        order = db.get_order_ws_depend_by_id(id_order)
        order.photo_pay_id = photo.file_id
        order.status = "processing"
        db.session.commit()
        person.status = None
        text = order.get_order_list()
        bot.send_photo(user_id, photo.file_id, text, parse_mode="Markdown")
        bot.send_message(user_id, "Ожидайте доставки")
        markup = types.InlineKeyboardMarkup()
        confirm_done = types.InlineKeyboardButton(text="☑️", callback_data=f"confirm_ord done {order.id}")
        confirm_cancel = types.InlineKeyboardButton(text="🚫", callback_data=f"confirm_ord cancel {order.id}")
        markup.add(confirm_done, confirm_cancel)
        bot.send_photo(order.assigned_admin.user_id, photo.file_id, text, parse_mode="Markdown", reply_markup=markup)

    @staticmethod
    @set_handler_none
    def handle_none(bot, message, person):
        if person.status:
            bot.send_message(message.chat.id, "Завершите действие")
            return
        if message.text and person.assigned_admin:
            bot.send_message(person.assigned_admin.user_id, f"[{person.name}:{person.id}] : {message.text}")
            return
        print(f"Нету обработчика у клиента")
        print(message)
        bot.send_possibilities(message.chat.id)
