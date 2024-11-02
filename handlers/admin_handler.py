from sqlalchemy.orm import joinedload

from config import *

from telebot import TeleBot, types

from db_orm.order import Order
from handlers.base_handler import BaseHandler
from handlers.base_handler import set_handler_text, set_handler_status, set_handler_none, set_handler_callback

from db_orm.product import Product
from database import Database


class AdminHandler(BaseHandler):
    @staticmethod
    @set_handler_text(TEXT_BUTTON_PRODUCTS)
    def handle_text_products(user_id, bot):
        for product in bot.products.values():
            if product.count < 0:
                continue

            markup = product.get_markup_admin()
            caption = product.get_caption()
            bot.send_photo(user_id, product.photo_id, caption, "Markdown", reply_markup=markup)

    @staticmethod
    @set_handler_callback(["product"])
    def handle_callback_product(data, bot, person, db, message, user_id, call):
        _, doing, product_id = data.split()
        product = bot.products[int(product_id)]
        if doing == "add":
            product.count += 1
            db.session.commit()
            markup = product.get_markup_admin()
            bot.edit_message_caption(product.get_caption(), user_id, message.id, parse_mode="Markdown",
                                     reply_markup=markup)
        elif doing == "sub":
            if product.count == 0:
                bot.answer_callback_query(call.id, "Товар и так закончился")
                return
            product.count -= 1
            db.session.commit()
            markup = product.get_markup_admin()
            bot.edit_message_caption(product.get_caption(), user_id, message.id, parse_mode="Markdown",
                                     reply_markup=markup)
        elif doing == "edit":
            person.status = f"product_edit {product_id}"
            bot.send_message(user_id, "Напишите количество", reply_markup=bot.get_cancel_markup())
        elif doing == "delete":
            product.count = -1
            db.session.commit()
            bot.delete_message(user_id, message.id)

    @staticmethod
    @set_handler_status("product_edit")
    def handle_text_product_edit(status, text, db, bot, user_id, person):
        _, product_id = status.split()
        product = bot.products[int(product_id)]

        if not text.isnumeric():
            bot.send_message(user_id, "Это не число")
            return

        product.count = int(text)
        db.session.commit()
        bot.send_message(user_id, "Данные изменены", reply_markup=bot.self.get_main_markup(user_id))
        person.status = None

    @staticmethod
    @set_handler_text(TEXT_BUTTON_CANCEL)
    def handle_text_cancel(user_id, bot, person):
        if person.status in ["sending_product_photo", "sending_product_name", "sending_product_price",
                             "sending_product_count"]:
            person.status = None
            person.product = None
        elif person.status and person.status.startswith("cancelled"):
            person.status = None
        else:
            person.status = None

        bot.send_message(user_id, "Действие было отменено", reply_markup=bot.get_main_markup(user_id))

    @staticmethod
    @set_handler_text(ADMIN_TEXT_BUTTON_LEAVE)
    def handle_text_leave(user_id, bot, person, db):
        if person.connected_client:
            bot.send_message(person.connected_client.user_id, "От вас отсоединился админ")
            person.connected_client = None
            db.session.commit()
            bot.send_message(user_id, "Вы отсоединились от клиента", reply_markup=bot.get_main_markup(user_id))
        else:
            bot.send_message(user_id, "Вы небыли подключены к клиенту", reply_markup=bot.get_main_markup(user_id))

    @staticmethod
    @set_handler_text(ADMIN_TEXT_BUTTON_ADD_PRODUCT)
    def handle_text_add_product(user_id, bot, person):
        person.product = Product()
        bot.send_message(user_id, "Фото товара:", reply_markup=bot.get_cancel_markup())
        person.status = "sending_product_photo"

    @staticmethod
    @set_handler_status("sending_product_photo")
    def handle_photo_product(photo, user_id, bot, person):
        person.product.photo_id = photo.file_id
        bot.send_message(user_id, "Название товара:", reply_markup=bot.get_cancel_markup())
        person.status = "sending_product_name"

    @staticmethod
    @set_handler_status("sending_product_name")
    def handle_text_name_product(text, user_id, bot, person):
        person.product.name = text
        bot.send_message(user_id, "Цена товара:", reply_markup=bot.get_cancel_markup())
        person.status = "sending_product_price"

    @staticmethod
    @set_handler_status("sending_product_price")
    def handle_text_price_product(text, user_id, bot, person):
        if not text.replace(".", "", 1).isnumeric():
            bot.send_message(user_id, "Неправильная форма ввода!\nПример: 2.25")
            bot.send_message(user_id, "Цена товара:", reply_markup=bot.get_cancel_markup())
            return
        person.product.price = float(text)
        bot.send_message(user_id, "Количество товара:", reply_markup=types.ForceReply())
        person.status = "sending_product_count"

    @staticmethod
    @set_handler_status("sending_product_count")
    def handle_text_count_product(text, user_id, bot, person, db: Database):
        if not text.isnumeric():
            bot.send_message(user_id, "Неправильная форма ввода!\nПример: 10")
            bot.send_message(user_id, "Количество товара:", reply_markup=bot.get_cancel_markup())
            return
        person.product.count = int(text)
        db.session.add(person.product)
        db.session.commit()
        bot.products[person.product.id] = person.product
        bot.send_message(user_id, "Товар был сохранен!", reply_markup=bot.get_main_markup(user_id))
        person.status = None

    @staticmethod
    @set_handler_callback(["confirm"])
    def handle_callback_confirm(data, bot, person, user_id, message, db: Database):
        _, doing, order_id = data.split()
        order = db.session.query(Order).filter_by(id=order_id).options(
            joinedload(Order.client)
        ).first()

        if order.assigned_admin_id:
            bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)
            bot.send_message(user_id, "Действия над заказом уже приняты", reply_markup=bot.get_main_markup(user_id))
            return

        client = bot.clients[int(order.client.user_id)]
        if doing == "done":
            client.status = f"wait_pay {order.id}"
            client.assigned_admin_id = person.id
            order.status = "wait_pay"
            order.assigned_admin_id = person.id

            db.session.commit()
            text = "Заказ был принят!\nИ так же вы подключены к чату админа\n"
            text += f"Сума заказа: *{order.price} грн*"
            bot.send_message(order.client.user_id, text, parse_mode="Markdown")
            bot.send_message(order.client.user_id, MESSAGE_TO_PAY)
            bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)

            for admin_id in bot.admins:
                bot.send_message(admin_id, f"Админ {person.name} взял на себя заказ {client.name}")

        elif doing == "cancel":
            client.status = None
            order.status = "canceled"
            person.status = f"cancelled {order.client.user_id}"
            db.session.commit()

            bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)
            bot.send_message(order.client.user_id, "Админ отклонил заказ")
            bot.send_message(user_id, "Напишите причину отмены для клиента:", reply_markup=types.ForceReply())

            for admin_id in bot.admins:
                bot.send_message(admin_id, f"Админ {person.name} отклонил заказ {client.name}")

    @staticmethod
    @set_handler_callback(["confirm_ord"])
    def handle_callback_confirm_ord(data, bot, person, user_id, message, db: Database):
        _, doing, order_id = data.split()
        bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)
        order = db.get_order_ws_client_by_id(order_id)
        order.client.assigned_admin = None
        person.connected_client = None
        if doing == "done":
            order.status = "done"
            db.session.commit()
            bot.send_message(order.client.user_id, "Заказ завершен успешно\nАдмин был отключен")
            bot.send_message(user_id, "Заказ завершен успешно")
        elif doing == "cancel":
            order.status = "cancel"
            db.session.commit()
            bot.send_message(order.client.user_id, "Заказ был отменен\nАдмин был отключен")
            bot.send_message(user_id, "Заказ был отменен")

    @staticmethod
    @set_handler_status("cancelled")
    def handle_text_cancelled(text, bot, person, user_id):
        chat_id = int(person.status.split()[1])
        person.status = None
        bot.send_message(chat_id, f"[{person.name}]: {text}")
        bot.send_message(user_id, "Сообщение отправлено!", reply_markup=bot.get_main_markup(user_id))

    @staticmethod
    @set_handler_none
    def handle_none(bot, db, message, user_id, person):
        if message.text and message.text.startswith("👤"):
            orders = db.get_admin_assigned_orders_ws_clients(user_id)
            for order in orders:
                if order.get_admin_button_text() == message.text:
                    person.connected_client = order.client
                    db.session.commit()
                    bot.send_message(user_id, "Клиент был подключен!", reply_markup=bot.get_cancel_markup(True))
                    bot.send_message(order.client.user_id, f"К вам подключился админ [{person.name}]")
                    return
            bot.send_message(user_id, "Такого заказа нет!", reply_markup=bot.get_main_markup(user_id))
            return

        if message.text and person.connected_client:
            bot.send_message(person.connected_client.user_id, f"[{person.name}] : {message.text}")
            return

        print(f"Нету обработчика у админа")
        print(message)
        bot.send_possibilities(message.chat.id, True)
