from fastapi import APIRouter, Path
from api.models.tofurengo_request import TofurengoRequest, VALID_GLYPH_SETS
from .services import (
    normalize_service,
    render_service,
    convert_service,
)

endpoints_router = APIRouter()

# GET convert
@endpoints_router.get("/convert/{glyph_set}/{text:path}")
def convert(
    glyph_set: str = Path(
        ...,
        description="Glyph set to use.",
        enum=VALID_GLYPH_SETS
    ),
    text: str = Path(
        ...,
        description="Input text to process."
    )
):
    return convert_service(glyph_set, text)

# POST normalize (uses glyph_set from request body)
@endpoints_router.post("/normalize")
def normalize(payload: TofurengoRequest):
    return normalize_service(payload.glyph_set, payload.text)

# POST render (uses glyph_set from request body)
@endpoints_router.post("/render")
def render(payload: TofurengoRequest):
    return render_service(payload.glyph_set, payload.text)
