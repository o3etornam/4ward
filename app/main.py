from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routers import ussd

app = FastAPI(title="NUMA")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=ussd.router)


@app.get("/")
async def index():
    return responses.RedirectResponse("/docs")
