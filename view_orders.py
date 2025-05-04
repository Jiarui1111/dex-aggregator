from sqlmodel import select
from db.session import get_session
from models.order import Order

for session in get_session():
    orders = session.exec(select(Order)).all()
    for order in orders:
        print(order)
