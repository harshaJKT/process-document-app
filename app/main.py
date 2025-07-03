from fastapi import FastAPI
from app.subscriber import start_subscriber
from app.routers import upload, user_role

app = FastAPI()

# Include routers
app.include_router(upload.router, tags=["File Upload"])
app.include_router(user_role.router, tags=["User Role Management"])


@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    - Start background subscriber
    """
    print(" Starting Document Processor...")

    #  Tables are created manually via DBeaver or alembic (not here)

    #  Start background subscriber
    await start_subscriber()
    print(" Background subscriber started.")


@app.get("/")
def read_root():
    return {"message": " Document Processor is running!"}

 