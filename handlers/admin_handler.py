from config import *

from telebot import TeleBot, types

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
                bot.answer_callback_query(call.id, "⚠️ Товар вже закінчився")
                return
            product.count -= 1
            db.session.commit()
            markup = product.get_markup_admin()
            bot.edit_message_caption(product.get_caption(), user_id, message.id, parse_mode="Markdown",
                                     reply_markup=markup)
        elif doing == "edit":
            person.status = f"product_edit {product_id}"
            bot.send_message(user_id, "✍️ Введіть кількість:", reply_markup=bot.get_cancel_markup())
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
            bot.send_message(user_id, "🚫 Це не число")
            return

        product.count = int(text)
        db.session.commit()
        bot.send_message(user_id, "✅ Дані змінено", reply_markup=bot.get_main_markup(user_id))
        person.status = None

    @staticmethod
    @set_handler_text(TEXT_BUTTON_CANCEL)
    def handle_text_cancel(user_id, bot, person, db):
        if person.connected_client:
            db.cancel_orders_by_client_id(person.connected_client_id)
            bot.send_message(person.connected_client.user_id, "❌ Ваші замовлення були скасовані")
            person.connected_client = None
            db.session.commit()
            bot.send_message(user_id, "❌ Замовлення були скасовані", reply_markup=bot.get_main_markup(user_id))
            return
        elif person.status and person.status.startswith("sending_product"):
            person.status = None
            person.product = None
        elif person.status and person.status.startswith("cancelled"):
            person.status = None
        else:
            person.status = None

        bot.send_message(user_id, "❌ Дію було скасовано", reply_markup=bot.get_main_markup(user_id))

    @staticmethod
    @set_handler_text(ADMIN_TEXT_BUTTON_LEAVE)
    def handle_text_leave(user_id, bot, person, db):
        if person.connected_client:
            bot.send_message(person.connected_client.user_id, "👋 Від вас відключився адміністратор")
            person.connected_client = None
            db.session.commit()
            bot.send_message(user_id, "🔌 Ви відключилися від клієнта", reply_markup=bot.get_main_markup(user_id))
        else:
            bot.send_message(user_id, "⚠️ Ви не були підключені до клієнта", reply_markup=bot.get_main_markup(user_id))

    @staticmethod
    @set_handler_text(ADMIN_TEXT_BUTTON_ADD_PRODUCT)
    def handle_text_add_product(user_id, bot, person):
        person.product = Product()
        bot.send_message(user_id, "🖼️ Фото товару:", reply_markup=bot.get_cancel_markup())
        person.status = "sending_product_photo"

    @staticmethod
    @set_handler_status("sending_product_photo")
    def handle_photo_product(photo, user_id, bot, person):
        person.product.photo_id = photo.file_id
        bot.send_message(user_id, "🏷️ Назва товару:", reply_markup=bot.get_cancel_markup())
        person.status = "sending_product_name"

    @staticmethod
    @set_handler_status("sending_product_name")
    def handle_text_name_product(text, user_id, bot, person):
        person.product.name = text
        bot.send_message(user_id, "💰 Ціна товару:", reply_markup=bot.get_cancel_markup())
        person.status = "sending_product_price"

    @staticmethod
    @set_handler_status("sending_product_price")
    def handle_text_price_product(text, user_id, bot, person):
        if not text.replace(".", "", 1).isnumeric():
            bot.send_message(user_id, "🚫 Неправильний формат введення!\nПриклад: 2.25")
            bot.send_message(user_id, "💰 Ціна товару:", reply_markup=bot.get_cancel_markup())
            return
        person.product.price = float(text)
        bot.send_message(user_id, "📦 Кількість товару:", reply_markup=types.ForceReply())
        person.status = "sending_product_count"

    @staticmethod
    @set_handler_status("sending_product_count")
    def handle_text_count_product(text, user_id, bot, person, db: Database):
        if not text.isnumeric():
            bot.send_message(user_id, "🚫 Неправильний формат введення!\nПриклад: 10")
            bot.send_message(user_id, "📦 Кількість товару:", reply_markup=bot.get_cancel_markup())
            return
        person.product.count = int(text)
        db.session.add(person.product)
        db.session.commit()
        bot.products[person.product.id] = person.product
        bot.send_message(user_id, "✅ Товар збережено!", reply_markup=bot.get_main_markup(user_id))
        person.status = None

    @staticmethod
    @set_handler_callback(["confirm"])
    def handle_callback_confirm(data, bot, person, user_id, message, db: Database, call):
        _, doing, order_id = data.split()
        order = db.get_order_ws_depend_by_id(order_id)

        if order.assigned_admin_id:
            bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)
            bot.send_message(user_id, "⚠️ Дії над замовленням вже прийняті", reply_markup=bot.get_main_markup(user_id))
            return

        client = bot.clients[int(order.client.user_id)]
        if doing == "done":
            if [ord_prod for ord_prod in order.order_products if ord_prod.product.count < ord_prod.count]:
                bot.answer_callback_query(call.id, "🚫 Вже не вистачає товару\n🔍 Перевірте товар")
                return

            for order_product in order.order_products:
                order_product.product.count -= order_product.count

            client.status = f"wait_pay {order.id}"
            client.assigned_admin_id = person.id
            order.status = "wait_pay"
            order.assigned_admin_id = person.id

            db.session.commit()
            text = "✅ Замовлення прийняте!\nІ ви також підключені до чату з адміністратором\n"
            text += f"💵 Сума замовлення: *{order.price} грн*"
            bot.send_message(order.client.user_id, text, parse_mode="Markdown")
            bot.send_message(order.client.user_id, MESSAGE_TO_PAY)
            bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)

            for admin_id in bot.admins:
                bot.send_message(admin_id, f"👨‍💼 Адміністратор {person.name} взяв на себе замовлення від {client.name}")
            bot.send_message(user_id, "🔄 Кнопки оновлені", reply_markup=bot.get_main_markup(user_id))

        elif doing == "cancel":
            client.status = None
            order.status = "canceled"
            person.status = f"cancelled {order.client.user_id}"
            db.session.commit()

            bot.edit_message_reply_markup(user_id, message.message_id, reply_markup=None)
            bot.send_message(order.client.user_id, "❌ Адміністратор відхилив замовлення")
            bot.send_message(user_id, "✍️ Вкажіть причину відміни для клієнта:", reply_markup=types.ForceReply())

            for admin_id in bot.admins:
                bot.send_message(admin_id, f"❌ Адміністратор {person.name} відхилив замовлення від {client.name}")

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
            bot.send_message(order.client.user_id, "✅ Замовлення успішно завершено\nАдміністратор був відключений")
            bot.send_message(user_id, "✅ Замовлення успішно завершено", reply_markup=bot.get_main_markup(user_id))
        elif doing == "cancel":
            order.status = "cancel"
            order = db.get_order_ws_depend_by_id(order_id)
            for order_product in order.order_products:
                order_product.product.count += order_product.count
            db.session.commit()
            bot.send_message(order.client.user_id, "❌ Замовлення було скасовано\nАдміністратор був відключений")
            bot.send_message(user_id, "❌ Замовлення було скасовано")

    @staticmethod
    @set_handler_status("cancelled")
    def handle_text_cancelled(text, bot, person, user_id):
        chat_id = int(person.status.split()[1])
        person.status = None
        bot.send_message(chat_id, f"[{person.name}]: {text}")
        bot.send_message(user_id, "📨 Повідомлення надіслано!", reply_markup=bot.get_main_markup(user_id))

    @staticmethod
    @set_handler_none
    def handle_none(bot, db, message, user_id, person):
        if message.text and message.text.startswith("👤"):
            orders = db.get_admin_assigned_orders_ws_clients(user_id)
            for order in orders:
                if order.get_admin_button_text() == message.text:
                    person.connected_client = order.client
                    db.session.commit()
                    bot.send_message(user_id, "🔗 Клієнт був підключений!", reply_markup=bot.get_cancel_markup(True))
                    bot.send_message(order.client.user_id, f"👤 До вас підключився адміністратор [{person.name}]")
                    return
            bot.send_message(user_id, "🚫 Такого замовлення немає!", reply_markup=bot.get_main_markup(user_id))
            return

        if message.text and person.connected_client:
            bot.send_message(person.connected_client.user_id, f"[{person.name}] : {message.text}")
            return

        print(f"🚫 У адміністратора немає обробника")
        print(message)
        bot.send_possibilities(message.chat.id, True)
