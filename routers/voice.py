from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import services.voice_service as voice_service

router = APIRouter()

class TTSSchema(BaseModel):
    text: str

processed_recordings = {}

@router.post("/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    filename = file.filename
    if filename and filename in processed_recordings:
        return {"status": "success", "transcript": processed_recordings[filename]}
        
    try:
        content = await file.read()
        transcription = voice_service.transcribe_audio(content)
        if filename:
            processed_recordings[filename] = transcription
        return {"status": "success", "transcript": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

@router.post("/tts")
def text_to_speech_endpoint(data: TTSSchema):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    filepath = voice_service.text_to_speech(data.text)
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="Failed to synthesize speech.")
        
    return FileResponse(filepath, media_type="audio/mpeg", filename=os.path.basename(filepath))
