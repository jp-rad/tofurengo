import pytest

from tofurengo.builder import build_normalizer, build_renderer

def test_usage_example():
    print("=== Usage Example ===")


    # Input text containing an MJ Hentaigana Glyph Tag (An-no-A)
    text = "'{MJ090001}'"

    # ------------------------------------------------------------
    # 1. Build Normalizer and Renderer
    # ------------------------------------------------------------
    # Load the MJ dataset (version 6.02.201) and create a normalizer
    normalizer = build_normalizer("mj", "6.02.201")

    # Create a renderer (use_base=False uses IVS/UCSSeq, use_base=True uses base character)
    renderer = build_renderer(use_base=False, tofu="U+25A1")

    # ------------------------------------------------------------
    # 2. Normalize Glyph Tags
    # ------------------------------------------------------------
    normalized = normalizer.normalize(text)
    print(normalized.text)
    # Output: '{MJ090001 b=U+5B89 v=U+1B002 set=mj}'

    # ------------------------------------------------------------
    # 3. Render Text to Unicode
    # ------------------------------------------------------------
    rendered = renderer.render(normalized.text)
    print(rendered)
    # Output: Hentaigana character (Kana Supplement U+1B002)

    # Using base Kanji fallback:
    base_renderer = build_renderer(use_base=True)
    print(base_renderer.render(normalized.text))
    # Output: Base Kanji character (U+5B89)

    # ------------------------------------------------------------
    # 4. Handle Escape Sequences (Section 4 of Specification)
    # ------------------------------------------------------------
    # Escaping '{' using '{{' prevents tag parsing and outputs a literal '{'
    text_with_escape = "Literal bracket: {{MJ090001}"
    normalized_esc = normalizer.normalize(text_with_escape)
    print(normalized_esc.text)
    # Output: "Literal bracket: {{MJ090001}"

    rendered_esc = renderer.render(normalized_esc.text)
    print(rendered_esc)
    # Output: "Literal bracket: {MJ090001}"

