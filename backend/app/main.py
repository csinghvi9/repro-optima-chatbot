from fastapi import FastAPI
from app.api_configure import configure_app, configure_database

# from app.database import init_db
from contextlib import asynccontextmanager
from app.routes.index import router


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_db()
#     yield

configs = [configure_app, configure_database]

app = FastAPI()

for config in configs:
    config(app)

@app.get("/")
def root():
    return {"status": "running"}
