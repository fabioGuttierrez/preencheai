from fastapi import FastAPI
from app.api.routes import contracts, template_upload, public_form

app = FastAPI()

app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
app.include_router(template_upload.router, prefix="/templates", tags=["templates"])
app.include_router(public_form.router, prefix="/form", tags=["form"])

@app.get("/ping")
def ping():
	return {"status": "ok"}
from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
	return {"status": "ok"}
