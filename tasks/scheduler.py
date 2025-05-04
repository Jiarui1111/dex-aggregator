from apscheduler.schedulers.background import BackgroundScheduler
from services.order_matcher import match_orders

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(match_orders, 'interval', seconds=60)  # Execute every 60 seconds
    scheduler.start()