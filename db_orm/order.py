from typing import List

from sqlalchemy import ForeignKey

from db_orm.base_orm import Base

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'))
    comment: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float]
    photo_pay_id: Mapped[str] = mapped_column(nullable=True)

    status: Mapped[str]
    assigned_admin_id: Mapped[int] = mapped_column(ForeignKey('admins.id'), nullable=True)

    client: Mapped["Client"] = relationship()
    assigned_admin: Mapped["Admin"] = relationship()
    order_products: Mapped[List["OrderProduct"]] = relationship()

    def get_order_price(self):
        total_amount = 0
        for order_product in self.order_products:
            total_amount += order_product.count * order_product.product.price
        return total_amount

    def get_order_list(self):
        text = f"*🧾 Замовлення номер {self.id}*\n"
        text += f"👤 Клієнт:  {self.client.name}\n"
        text += f"🏠 Номер кімнати: *{self.client.location}*\n\n"
        text += "🛍️ Список товарів:\n\n"

        for order_product in self.order_products:
            text += (f"*📦 {order_product.product.name}*: {order_product.count} \\* "
                     f"{order_product.product.price} грн = *{order_product.count * order_product.product.price} грн*\n")

        text += f"\n💵 Загальна ціна: *{self.get_order_price()} грн*"
        return text

    def get_admin_button_text(self):
        return f"👤 {self.client.name} (ID: {self.id}) 👤"

    def __repr__(self):
        return (f"<Order(id={self.id}, price={self.price}, client={self.client}, status={self.status}, "
                f"assigned_admin_id={self.assigned_admin_id})>")


class OrderProduct(Base):
    __tablename__ = 'order_products'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    count: Mapped[int]

    product: Mapped["Product"] = relationship()
