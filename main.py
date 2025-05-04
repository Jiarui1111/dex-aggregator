from fastapi import FastAPI
from db.session import create_db_and_tables
from routes import orders
from tasks.scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    start_scheduler()

app.include_router(orders.router, prefix="/api")
