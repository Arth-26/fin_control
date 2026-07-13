import sys, asyncio
from fastapi import FastAPI

from fin_control.routers import auth_router, transactions_router, users_router

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

app.include_router(users_router.router)
app.include_router(auth_router.router)
app.include_router(transactions_router.router)
