from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.session import get_session
from models.order import Order
from models.enums import OrderStatus
from datetime import datetime

router = APIRouter()

@router.post("/orders/limit")
def create_limit_order(order: Order, session: Session = Depends(get_session)):
    order.created_at = datetime.fromisoformat(order.created_at)
    order.expiry_time = datetime.fromisoformat(order.expiry_time)
    session.add(order)
    session.commit()
    session.refresh(order)
    return {"message": "Order created", "order": order}



@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="The order does not exist")

    if order.status not in [OrderStatus.OPEN, OrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="The order can no longer be cancelled")

    order.status = OrderStatus.CANCELLED
    session.add(order)
    session.commit()
    session.refresh(order)

    return {"message": "Order Cancelled", "order": order}


@router.post("/orders/{order_id}/reset")
def reset_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="The order does not exist")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only orders in PENDING status are allowed to be reset")

    order.status = OrderStatus.OPEN
    session.add(order)
    session.commit()
    return {"message": "Order status has been reset to OPEN", "order": order}