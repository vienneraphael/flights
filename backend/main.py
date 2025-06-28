from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Welcome to the flights API"}
