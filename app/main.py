from fastapi import FastAPI
from app.subscriber import start_subscriber
from app.routers import upload, user_role,query
from app.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI()

app.include_router(upload.router, tags=["File Upload"])
app.include_router(user_role.router, tags=["User Role Management"])
app.include_router(query.router,tags=["Query"])


# need to use lifespan as the below is deprecated
@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    - Create database tables
    - Start background subscriber
    """
    logger.info("Starting Document Processor...")

    await start_subscriber()
    logger.info("Background subscriber started")


@app.get("/")
def read_root():
    return {"message": "Document Processor is running!"}
