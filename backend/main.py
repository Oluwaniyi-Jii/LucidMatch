from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "LucidMatch API Reasoning Engine is Active"}
