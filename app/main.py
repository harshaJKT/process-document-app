from fastapi import FastAPI
from app.subscriber import start_subscriber
from app.routers import upload, user_role , query

app = FastAPI()

# Include routers
app.include_router(upload.router, tags=["File Upload"])
app.include_router(user_role.router, tags=["User Role Management"])
app.include_router(query.router,tags=["Query"])

@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    - Create database tables
    - Start background subscriber
    """
    print("Starting Document Processor...")

    # Create database tables
    # Tables are created during Postgres Setup on DBeaver.

    # Start background subscriber
    await start_subscriber()
    print("Background subscriber started")


@app.get("/")
def read_root():
    return {"message": "Document Processor is running!"}
