from fastapi import FastAPI

app = FastAPI(title="My FastAPI App")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "FastAPI is running!"}
