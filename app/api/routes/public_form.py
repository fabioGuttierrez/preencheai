from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_forms():
	return [{"id": 1, "status": "pending"}, {"id": 2, "status": "completed"}]

@router.get("/")
def public_form():
	return {"message": "Form endpoint"}
@router.get("/")
def list_forms():
	return [{"id": 1, "status": "pending"}, {"id": 2, "status": "completed"}]
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def public_form():
	return {"message": "Form endpoint"}
