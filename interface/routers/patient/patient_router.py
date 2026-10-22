import logging
import uuid

import inject
from fastapi import APIRouter, Depends, HTTPException

from business.ai.ai_facade import AIFacade
from business.entity.patient.patient_entity import PatientEntity
from business.entity.user.user_entity import UserEntity
from interface.auth.auth import get_current_active_user
from interface.routers.patient.schemas import PatientAddModel
from main.dependency_container import DepContainer

router = APIRouter(prefix="/patient", tags=["patient"])
logger = logging.getLogger("hekades")


@router.get("/all")
def get_all_patients(user: UserEntity = Depends(get_current_active_user)) -> list[PatientEntity]:
    return inject.instance(DepContainer).patient_repo.get_all_patients(user.email)


@router.post("/add")
async def add_patient(model: PatientAddModel, user: UserEntity = Depends(get_current_active_user)):
    patient_id = str(uuid.uuid4())
    patient_summary = await inject.instance(DepContainer).ai_facade.summarize_patient_record(model.patient_file_text)

    patient = PatientEntity(**model.model_dump(), user_id=user.email, patient_id=patient_id, patient_summary=patient_summary)
    inject.instance(DepContainer).patient_repo.add_patient(patient)


@router.put("/edit/{patient_id}")
async def edit_patient(patient_id: str, model: PatientAddModel, user: UserEntity = Depends(get_current_active_user)):
    patient_summary = await inject.instance(DepContainer).ai_facade.summarize_patient_record(model.patient_file_text)

    patient = PatientEntity(**model.model_dump(), user_id=user.email, patient_id=patient_id, patient_summary=patient_summary)
    inject.instance(DepContainer).patient_repo.update_patient(patient)


@router.delete("/delete/{patient_id}")
def delete_patient(patient_id: str, user: UserEntity = Depends(get_current_active_user)):
    patients = inject.instance(DepContainer).patient_repo.get_all_patients(user.email)
    if not any(patient.patient_id == patient_id for patient in patients):
        raise HTTPException(status_code=404, detail="Patient not found")

    inject.instance(DepContainer).patient_repo.delete_patient(patient_id)
