from database import Database
from telebot import types


def _set_decorator(name_attr, value):
    def decorator(func):
        def wrapper(*args, **kwargs):
            wrap_kwargs = {k: v for k, v in kwargs.items()
                           if k in func.__code__.co_varnames[:func.__code__.co_argcount]}
            result = func(*args, **wrap_kwargs)
            return result

        setattr(wrapper, name_attr, value)
        return wrapper

    return decorator


def set_handler_text(text: str):
    """
    Сверяется текст в полном объеме

    Работает для функций начинающихся с:
        def handle_text_...(text, db, user_id, bot, message, person, status:opc): Для отправки текста

        def handle_photo_...(photo, db, user_id, bot, message, person, status:opc): Для отправки фото

    :param text:
    :return:
    """
    return _set_decorator("text", text)


def set_handler_status(status: str):
    """
    Сверяется status до первого ' '
    Пример: 'pay_me 25', сверит 'pay_me'

    Работает для функций начинающихся с:
        def handle_text_...(text, db, user_id, bot, message, person, status:opc): Для отправки текста

        def handle_photo_...(photo, db, user_id, bot, message, person, status:opc): Для отправки фото
    :param status:
    :return:
    """
    return _set_decorator("status", status)


def set_handler_callback(callback: list):
    """
    Сверяется callback до первого ' ' в списке []
    Пример: 'pay_me 25', сверит 'pay_me' есть ли в списке ['pay_me', 'pay_you']

    Работает для функций начинающихся с:
        def handle_callback_...(data, db, user_id, bot, message, call, person,
        status:opc): Для отправки callback на inline кнопке
    :param callback: :return:
    """
    return _set_decorator("callback", callback)


set_handler_none = _set_decorator("none", None)


class BaseHandler:

    @staticmethod
    @set_handler_text("stat")
    def handle_text_stat(status, person):
        print(status)
        print(person)

    @staticmethod
    @set_handler_none
    def handle_none(text, message: types.Message, db: Database, bot):
        client = db.add_client(message.chat.id, message.chat.first_name, text)
        bot.clients[client.user_id] = client
        bot.send_message(message.chat.id, "Ви были зарегистрированы!")
        bot.send_possibilities(message.chat.id)

    @classmethod
    def process_text_handlers(cls, startswith_handler, **kwargs):  # (text, person, db, user_id, bot, status:opc)
        handlers = (handle_text for handle_text in sorted(dir(cls), reverse=True)
                    if handle_text.startswith(startswith_handler))
        for handler_attr in handlers:
            handler = getattr(cls, handler_attr)
            text_bool = hasattr(handler, "text") and kwargs.get("text") == handler.text
            status_bool = hasattr(handler, "status") and kwargs.get("status", "*").split()[0] == handler.status
            callback_bool = hasattr(handler, "callback") and kwargs.get("data").split()[0] in handler.callback
            if not (text_bool or status_bool or callback_bool):
                continue
            handler(**kwargs)
            return
        cls.handle_none(**kwargs)


if __name__ == '__main__':
    # print(dir())
    BaseHandler().process_text_handlers("handle_text", status="stat", text=5)
