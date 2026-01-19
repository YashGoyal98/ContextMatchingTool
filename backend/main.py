import uvicorn
from fastapi import FastAPI
from backend.controller import router

app = FastAPI(title="Revit Context Backend")

# Register the routes
app.include_router(router)

if __name__ == "__main__":
    # Runs on localhost:8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)