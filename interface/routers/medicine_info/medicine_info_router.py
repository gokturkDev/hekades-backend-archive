import csv
from io import StringIO

import inject
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from business.entity.medicine_info.medicine_info_entity import MedicineInfoEntity
from interface.auth.auth import get_current_admin_user
from main.dependency_container import DepContainer

router = APIRouter(prefix="/medicine_info", tags=["medicine_info"])


@router.post("/")
def upload_medicine_info(file: UploadFile = File(...), admin_user=Depends(get_current_admin_user)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    file_content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(StringIO(file_content), delimiter=",")

    infos = []
    for row in reader:
        # row is a dictionary with the keys being the keys of columns
        try:
            medicine_info = MedicineInfoEntity(
                name=row["ILAC ADI"],
                active_substance_name=row["ETKIN MADDE"],
                company_name=row["FIRMA ADI"],
                kub_link=row["KUB link"],
                sut=row["SUT"],
            )
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing column {e} for row {row}")
        infos.append(medicine_info)

    inject.instance(DepContainer).medicine_info_repo.add(infos)
