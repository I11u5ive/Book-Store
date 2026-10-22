import logging
from celery import shared_task

from .services import build_stock_report

logger = logging.getLogger(__name__)


@shared_task
def generate_stock_report():
    report = build_stock_report()
    logger.info("Periodic warehouse report generated: %s", report)
    return report
