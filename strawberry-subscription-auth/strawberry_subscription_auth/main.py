from fastapi import FastAPI
from .strawberry_schema import broadcast, graphql_app
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await broadcast.connect()


@app.on_event("shutdown")
async def shutdown_event():
    print("shutting down!!!")
    await broadcast.disconnect()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(graphql_app, prefix="/graphql",)
