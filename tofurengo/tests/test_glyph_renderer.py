import pytest

from tofurengo.builder import build_normalizer, build_renderer
from tofurengo.resource import get_resource
from tofurengo.glyph_normalizer import NormalizeResult


EXPECTED_VERSION = "0.1.0"

EXPECTED_GLYPH_TABLE = {
    "MJ000001": {"v": "U+3005", "b": "U+3005", "active": True},
    "MJ000012": {"v": "U+2CF1C", "b": "U+2CF1C", "active": False},
    "MJ000013": {"v": "U+3416", "b": "U+3416", "active": False},
    "MJ022336": {"v": "U+845B U+E0103", "b": "U+845B", "active": True},
    "MJ022335": {"v": "U+845B U+E0102", "b": "U+845B", "active": True},
}


# ------------------------------------------------------------
# Resource loading test
# ------------------------------------------------------------

def test_dataset_resource_matches_expected():
    resource = get_resource("template", "0.1.0", base="tofurengo_data")

    print("\n=== Resource Loaded ===")
    print("VERSION:", resource["VERSION"])
    print("GLYPH_TABLE:", resource["GLYPH_TABLE"])
    print("LIBRARY_NAME:", resource["LIBRARY_NAME"])

    assert resource["VERSION"] == EXPECTED_VERSION
    assert resource["GLYPH_TABLE"] == EXPECTED_GLYPH_TABLE


# ------------------------------------------------------------
# Combined test:
# use_base=False then use_base=True (sequential output)
# ------------------------------------------------------------

def test_dataset_sentence_use_base_sequence():
    normalizer = build_normalizer(
        glyph_set="template",
        version="0.1.0",
        base="tofurengo_data",
    )

    text = (
        "Start {{X}} A {MJ000001} B {MJ022335} C {MJ022336} "
        "D {MJ000012} E {MJ000013}}}"
    )

    # Normalize once
    norm = normalizer.normalize(text)

    print("\n=== Normalized Sentence ===")
    print(norm.text)
    print("Errors:", [e.code for e in norm.errors])

    assert isinstance(norm, NormalizeResult)

    # --------------------------------------------------------
    # 1) use_base=False (variant preferred)
    # --------------------------------------------------------

    renderer_v = build_renderer(use_base=False)
    rendered_v = renderer_v.render(norm.text)

    print("\n=== Rendered (use_base=False) ===")
    print(rendered_v)

    # --------------------------------------------------------
    # 2) use_base=True (base preferred)
    # --------------------------------------------------------

    renderer_b = build_renderer(use_base=True)
    rendered_b = renderer_b.render(norm.text)

    print("\n=== Rendered (use_base=True) ===")
    print(rendered_b)

    # --------------------------------------------------------
    # Assertions
    # --------------------------------------------------------

    # Common checks
    assert rendered_v.startswith("Start {X}")
    assert rendered_b.startswith("Start {X}")
    assert rendered_v.endswith("}}")
    assert rendered_b.endswith("}}")

    # Tofu fallback count
    assert rendered_v.count("\u25A1") == 2
    assert rendered_b.count("\u25A1") == 2

    # use_base=False: IVS must appear
    assert "\U000E0102" in rendered_v
    assert "\U000E0103" in rendered_v

    # use_base=True: IVS must not appear
    assert "\U000E0102" not in rendered_b
    assert "\U000E0103" not in rendered_b

    # Base char must appear in both
    assert "\u845B" in rendered_v
    assert "\u845B" in rendered_b

    # MJ000001 is same for both (v=b)
    assert "\u3005" in rendered_v
    assert "\u3005" in rendered_b

