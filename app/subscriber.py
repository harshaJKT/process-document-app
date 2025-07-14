from app.messaging import broker
from app.message_processor import process_document
from app.logger import setup_logger
logger = setup_logger(__name__)

async def start_subscriber():
    """
    Start the background subscriber to process uploaded documents
    """
    broker.subscribe(topic_name="doc_uploaded", handler=process_document)
    logger.info("[Subscriber] Started listening for document uploads")
