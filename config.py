from os import getenv

DATABASE_URL = getenv("DATABASE_URL")
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')

START_STICKER = "CAACAgIAAxkBAAErA1FnGiVexxd8gYh2K55CsLbNwhLPDgAChwIAAladvQpC7XQrQFfQkDYE"
START_MESSAGE_FIRST = "Привет"
START_MESSAGE_SECOND = "Второе сообщение"
REGISTRATION_MESSAGE = "Для регистрации отправьте номер вашей комнаты"

TEXT_BUTTON_PRODUCTS = "🛍️ Подивитися товари 👀"
TEXT_BUTTON_ACCOUNT = "👤 Профіль 👤"
TEXT_BUTTON_BUY = "📦 Заказати товари 📋"

TEXT_BUTTON_CANCEL = "❌ Відмінити 🔙"
ADMIN_TEXT_BUTTON_ADD_PRODUCT = "✏️ Додати товар 📦"
ADMIN_TEXT_BUTTON_LEAVE = "🚪 Від'єднатися 🙅"

ERROR_NO_ACTION = "⚠️ Такої кнопки немає, оберіть з наведених нижче:"

MESSAGE_TO_PAY = "Оплатите по карте: 4441114409403589\nПосле этого отправьте скрин оплаты в чат"
