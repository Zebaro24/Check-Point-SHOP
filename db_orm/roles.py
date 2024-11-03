from typing import List

from sqlalchemy import ForeignKey, BigInteger

from db_orm.base_orm import Base

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column


class Client(Base):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str]
    location: Mapped[str]

    assigned_admin_id: Mapped[int] = mapped_column(ForeignKey('admins.id'), nullable=True)
    assigned_admin: Mapped["Admin"] = relationship(foreign_keys="Client.assigned_admin_id")

    status = None
    order = {}

    def get_order_price(self):
        total_amount = 0
        for product, count in self.order.items():
            total_amount += product.price * count
        return total_amount

    def get_order_list(self, to_admin=False):
        if to_admin:
            text = f"_📋 Список товарів_ *{self.name} ({self.location})* _:_\n\n"
        else:
            text = "*📋 Список товарів:*\n\n"
        for product, count in self.order.items():
            print(product, count)
            text += f"📦 {product.name}: {count}/{product.count} штук \\* {product.price} грн = *{count * product.price} грн*\n"

        text += f"\n💵 Загальна ціна: *{self.get_order_price()} грн*"
        return text

    def __repr__(self):
        if self.assigned_admin:
            return (f"<Client(id={self.id}, name={self.name}, location={self.location}, "
                    f"assigned_admin={self.assigned_admin_id}, self.status={self.status})>")
        return f"<Client(id={self.id}, name={self.name}, location={self.location}, self.status={self.status})>"


class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str]

    connected_client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'), nullable=True)
    connected_client: Mapped["Client"] = relationship(foreign_keys="Admin.connected_client_id")

    assigned_clients: Mapped[List["Client"]] = relationship(back_populates="assigned_admin",
                                                            foreign_keys=[Client.assigned_admin_id])

    status = None
    product = None

    def __repr__(self):
        if self.connected_client:
            return f"<Admin(id={self.id}, name={self.name}, connected_client={self.connected_client})>"
        return f"<Admin(id={self.id}, name={self.name})>"
