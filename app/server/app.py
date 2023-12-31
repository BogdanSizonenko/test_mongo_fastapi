from fastapi import FastAPI
from .routes.user import router as UserRouter
from .routes.notifications import router as NotificationRouter


app = FastAPI()

app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(NotificationRouter, tags=["Notification"], prefix="/notification")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this app!"}