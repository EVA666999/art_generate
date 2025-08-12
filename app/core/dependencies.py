from fastapi import Depends
from app.services.face_refinement import FaceRefinementService
from app.config.settings import settings

def get_face_refinement_service() -> FaceRefinementService:
    """Получение сервиса для генерации изображений"""
    return FaceRefinementService(
        api_url=settings.SD_API_URL
    ) 