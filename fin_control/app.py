from fastapi import FastAPI

from fin_control.routers import auth_router, users_router

app = FastAPI()

app.include_router(users_router.router)
app.include_router(auth_router.router)
