from fastapi import APIRouter, UploadFile, File, Query
from app.services.template_upload_service import handle_template_upload

router = APIRouter()

@router.get("/")
def list_templates():
    return [{"id": 1, "nome": "Template A"}, {"id": 2, "nome": "Template B"}]

@router.post("/admin/template/upload")
def upload_template(files: list[UploadFile] = File(...), company_id: int = Query(...)):
    return handle_template_upload(files, company_id)
