from tofurengo.builder import build_normalizer, build_renderer
from tofurengo.glyph_normalizer import GlyphNormalizer

glyph_set_info = {
    "mj":      {"set": "mj",       "version": "6.02.201"},
    "mj-onka": {"set": "mj",       "version": "6.02.201-onka"},
    "mj-plus": {"set": "mj_plus",  "version": "4.10"},
    "mj-plusx":{"set": "mj_plusx", "version": "1.20"},
}

normalizers = {
    name: build_normalizer(info["set"], info["version"])
    for name, info in glyph_set_info.items()
}

renderer = build_renderer()

def get_normalizer(glyph_set: str):
    if glyph_set not in glyph_set_info:
        raise ValueError(f"Unknown normalizer: {glyph_set}")

    return {
        "info": glyph_set_info[glyph_set],
        "engine": normalizers[glyph_set],
    }

# normalize_service
def normalize_service(glyph_set: str, text: str):
    e = get_normalizer(glyph_set)
    eng: GlyphNormalizer = e["engine"]
    info = e["info"]

    n = eng.normalize(text)
    errors = [err.to_dict() for err in n.errors]

    return {
        "service": "normalize",
        "meta": {
            "engine": glyph_set,
            "glyph": info,
        },
        "text": {
            "input": text,
            "normalized": n.text,
        },
        "errors": errors
    }

# render_service (does not call normalize_tags)
def render_service(glyph_set: str, normalized_text: str):
    info = glyph_set_info[glyph_set]

    rendered_variant = renderer.render(normalized_text, use_base=False)
    rendered_base = renderer.render(normalized_text, use_base=True)

    return {
        "service": "render",
        "meta": {
            "engine": glyph_set,
            "glyph": info,
        },
        "text": {
            "rendered": {
                "base": rendered_base,
                "variant": rendered_variant,
            }
        },
        "errors": []
    }

# convert_service (normalize + render)
def convert_service(glyph_set: str, text: str):
    e = get_normalizer(glyph_set)
    eng: GlyphNormalizer = e["engine"]
    info = e["info"]

    n = eng.normalize(text)
    errors = [err.to_dict() for err in n.errors]

    rendered_variant = renderer.render(n.text, use_base=False)
    rendered_base = renderer.render(n.text, use_base=True)

    return {
        "service": "convert",
        "meta": {
            "engine": glyph_set,
            "glyph": info,
        },
        "text": {
            "input": text,
            "normalized": n.text,
            "rendered": {
                "base": rendered_base,
                "variant": rendered_variant,
            }
        },
        "errors": errors
    }
