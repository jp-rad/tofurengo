from pydantic import Field
from ._json_base_model import JsonBaseModel

# Allowed glyph set identifiers
VALID_GLYPH_SETS = ["mj-plus", "mj-plusx", "mj", "mj-onka"]

class TofurengoRequest(JsonBaseModel):
    # Glyph set used for normalization or rendering
    glyph_set: str = Field(
        default="mj-plus",
        description="Glyph set to use.",
        enum=VALID_GLYPH_SETS
    )

    # Input text to process
    text: str = Field(
        default="",
        description="Input text to process."
    )
