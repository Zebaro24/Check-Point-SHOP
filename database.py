from db_orm.base_orm import Base
from db_orm.roles import Client, Admin
from db_orm.order import Order, OrderProduct
from db_orm.product import Product

from sqlalchemy import create_engine, DDL, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
import sqlalchemy


class Database:
    def __init__(self, db_uri):
        url = db_uri.replace('postgres', 'postgresql+psycopg2')
        self.engine = create_engine(url)
        self.session = Session(self.engine)

    def connect(self):
        try:
            self.session.connection()
            self.session.execute(DDL("SET search_path TO check_point_shop,public"))
            return True
        except sqlalchemy.exc.OperationalError:
            return False

    def add_admin(self, name, user_id):
        self.session.add(Admin(name=name, user_id=user_id))
        self.session.commit()

    def add_client(self, user_id, name, location):
        client = Client(user_id=user_id, name=name, location=location)
        self.session.add(client)
        self.session.commit()
        return client

    def get_product(self, product_id):
        return self.session.query(Product).filter_by(product_id=product_id).first()

    def add_order_by_client(self, client: Client):
        order = Order(client_id=client.id, price=client.get_order_price(), status="wait_confirm")
        self.session.add(order)
        self.session.commit()
        for product, count in client.order.items():
            order_product = OrderProduct(order_id=order.id, product=product, count=count)
            self.session.add(order_product)
        self.session.commit()
        client.order = {}
        client.status = None
        return order

    def get_admin_assigned_orders_ws_clients(self, admin_id):
        admin_id_subquery = select(Admin.id).where(Admin.user_id == admin_id).scalar_subquery()

        valid_statuses = ["wait_pay", "processing"]
        orders = self.session.execute(
            select(Order, Client)
            .options(joinedload(Order.client))
            .join(Client)
            .where(Order.assigned_admin_id == admin_id_subquery)
            .where(Order.status.in_(valid_statuses))
        ).scalars().all()

        for order in orders:
            print(order)

        return orders

    def cancel_orders_by_client_id(self, client_id):
        status_list = ["wait_pay", "processing"]
        orders = (self.session.query(Order)
                  .options(joinedload(Order.order_products).joinedload(OrderProduct.product))
                  .filter(Order.client_id == client_id, Order.status.in_(status_list)).all())
        for order in orders:
            order.status = "cancel"

            for order_product in order.order_products:
                order_product.product.count += order_product.count

    def get_order_ws_depend_by_id(self, id_order):
        order = self.session.query(Order).options(
            joinedload(Order.client),
            joinedload(Order.assigned_admin),
            joinedload(Order.order_products).joinedload(OrderProduct.product)
        ).filter(Order.id == id_order).first()
        return order

    def get_order_ws_client_by_id(self, id_order):
        return self.session.query(Order).options(joinedload(Order.client)).filter(Order.id == id_order).first()

    def get_all_data(self):
        admins_list = self.session.query(Admin).options(
            joinedload(Admin.connected_client),
            joinedload(Admin.assigned_clients)
        ).all()
        clients_list = self.session.query(Client).options(
            joinedload(Client.assigned_admin)
        ).all()
        products_list = self.session.query(Product).all()

        admins = {admin.user_id: admin for admin in admins_list}
        clients = {client.user_id: client for client in clients_list}
        products = {product.id: product for product in products_list}

        return admins, clients, products

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)


if __name__ == '__main__':
    # Пример использования:
    from os import getenv

    # Создание экземпляра базы данных
    db = Database(getenv("DATABASE_URL"))
    db.connect()

    # db.add_admin("Zebaro", 771348519)
    # for i in db.get_all_data():
    #     print(i)
    print(db.get_order_list_by_id(11))

    # Создание таблицы
    # db.create_tables()

    # Удаление таблицы (при необходимости)
    # db.drop_tables()

    db.session.close()
