from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_contracts():
	# Exemplo: retorna lista mock
	return [{"id": 1, "status": "pending"}, {"id": 2, "status": "generated"}]
