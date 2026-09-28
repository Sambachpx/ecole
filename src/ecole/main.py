from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{user_id}")
def read_item(user_id: int, q: str | None = None):
    return {"user_id": user_id, "q": q}
