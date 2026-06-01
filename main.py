from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def home():
    return {"status": "alive", "framework": "FastAPI on Lambda"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}

@app.get("/sum")
def sum(a: int, b: int):
    return {"sum": a - b}

handler = Mangum(app)