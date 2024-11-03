from db_orm.base_orm import Base

from telebot import types

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    photo_id: Mapped[str]
    name: Mapped[str]
    price: Mapped[float]
    count: Mapped[int]

    def get_caption(self, count_buy=None):
        caption = f"📦 Товар: *{self.name}*\n\n"
        caption += f"💰 Ціна: *{self.price} грн*\n"
        caption += f"🟢 В наявності: *{self.count} позицій*"

        if count_buy:
            caption += f"\n\n🛒 У кошику: *{count_buy} шт.*"
        return caption

    def get_markup_client(self, count_buy=False):
        markup = types.InlineKeyboardMarkup()
        markup_list = []
        if count_buy:
            markup_list.append(types.InlineKeyboardButton(text="➖", callback_data=f"sub {self.id}"))
            markup_list.append(types.InlineKeyboardButton(text="❌", callback_data=f"clear {self.id}"))

        markup_list.append(types.InlineKeyboardButton(text="➕", callback_data=f"add {self.id}"))
        markup.add(*markup_list)

        return markup

    def get_markup_admin(self):
        markup = types.InlineKeyboardMarkup()
        product_add = types.InlineKeyboardButton(text="➕", callback_data=f"product add {self.id}")
        product_delete = types.InlineKeyboardButton(text="🗑", callback_data=f"product delete {self.id}")
        product_edit = types.InlineKeyboardButton(text="✏️", callback_data=f"product edit {self.id}")
        product_sub = types.InlineKeyboardButton(text="➖", callback_data=f"product sub {self.id}")
        markup.add(product_sub, product_edit, product_add)
        markup.add(product_delete)
        return markup

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price}, count={self.count})>"
