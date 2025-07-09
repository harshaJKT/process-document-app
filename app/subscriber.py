from app.messaging import broker
from app.message_processor import process_document


async def start_subscriber():
    """
    Start the subscriber to process uploaded documents
    """
    broker.subscribe("doc_uploaded", process_document)
    print("[Subscriber] Started listening for document uploads")
