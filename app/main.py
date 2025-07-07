from fastapi import FastAPI
from app.subscriber import start_subscriber
from app.routers import upload, user_role, retrieve 

app = FastAPI()

app.include_router(upload.router, tags=["File Upload"])
app.include_router(user_role.router, tags=["User Role Management"])
app.include_router(retrieve.router, tags=["Document Retrieval"])  

@app.on_event("startup")
async def startup_event():
    print("Starting Document Processor...")
    await start_subscriber()
    print("Background subscriber started")

@app.get("/")
def read_root():
    return {"message": "Document Processor is running!"}
