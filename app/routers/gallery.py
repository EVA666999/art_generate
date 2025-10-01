from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="/api/v1", tags=["paid_gallery"])


@router.get("/paid-gallery/{character}")
async def list_paid_gallery(character: str) -> dict:
    """Возвращает список URL изображений платной галереи для персонажа."""
    project_root = Path(__file__).resolve().parents[2]
    gallery_dir = project_root / "paid_gallery" / character.lower()
    if not gallery_dir.exists() or not gallery_dir.is_dir():
        raise HTTPException(status_code=404, detail="Галерея не найдена")

    exts = {".png", ".jpg", ".jpeg", ".webp"}
    files = []
    for p in sorted(gallery_dir.iterdir()):
        if p.is_file() and p.suffix.lower() in exts:
            # Раздаётся как /paid_gallery/<character>/<filename>
            files.append({
                "name": p.name,
                "url": f"/paid_gallery/{character.lower()}/{p.name}"
            })

    return {"character": character.lower(), "count": len(files), "images": files}


