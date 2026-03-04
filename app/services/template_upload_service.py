import os
from fastapi import UploadFile
from typing import List

UPLOAD_DIR = "app/templates_html/"

def handle_template_upload(files: List[UploadFile], company_id: int):
    saved_files = []
    company_dir = os.path.join(UPLOAD_DIR, str(company_id))
    os.makedirs(company_dir, exist_ok=True)
    for file in files:
        file_path = os.path.join(company_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        saved_files.append(file_path)
    return {"uploaded": saved_files}
