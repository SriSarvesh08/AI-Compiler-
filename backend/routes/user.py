from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import json
from database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User Settings"])

class UserSettings(BaseModel):
    model: str
    runtimeMode: str
    exportJson: bool
    exportValidation: bool
    exportEvaluation: bool
    autoRepair: bool
    showPipelineAnimations: bool
    defaultTab: str

@router.post("/settings")
async def update_settings(settings: UserSettings, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    settings_json = json.dumps(settings.dict())
    
    c.execute(
        "UPDATE users SET settings_json = %s WHERE id = %s",
        (settings_json, current_user["id"])
    )
    conn.commit()
    conn.close()
    
    return {"message": "Settings updated successfully", "settings": settings.dict()}
