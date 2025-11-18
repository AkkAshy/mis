from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date
from app.db.session import SessionLocal
from app.models.queue import Queue as QueueModel
import logging

logger = logging.getLogger(__name__)


def clear_old_queues():
    """
    Очистка всех очередей, которые старше сегодняшней даты.
    Вызывается автоматически каждый день в 00:00.
    """
    db = SessionLocal()
    try:
        today = date.today()
        deleted_count = db.query(QueueModel).filter(QueueModel.queue_date < today).delete()
        db.commit()
        logger.info(f"✓ Queue reset completed. Removed {deleted_count} old entries.")
        print(f"✓ Queue reset completed at {date.today()}. Removed {deleted_count} old entries.")
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error clearing old queues: {e}")
        print(f"✗ Error clearing old queues: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Запуск планировщика задач для автоматического сброса очередей.
    """
    scheduler = BackgroundScheduler()

    # Добавляем задачу на очистку очередей каждый день в 00:00
    scheduler.add_job(
        clear_old_queues,
        trigger=CronTrigger(hour=0, minute=0),
        id="clear_old_queues",
        name="Clear old queues daily at midnight",
        replace_existing=True
    )

    scheduler.start()
    logger.info("✓ Scheduler started. Queue reset scheduled for 00:00 daily.")
    print("✓ Scheduler started. Queue reset scheduled for 00:00 daily.")

    return scheduler
