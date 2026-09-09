from pathlib import Path
import subprocess
import csv

from tofurengo.ucs import ucs_to_glyph

from tools.core.model import GlyphRecord
from tools.core.normalize import (
    to_uplus_string,
    validate_uplus_input,
    sanitize_comment,
)


def load_dwpi_mdb(mdb_path: Path) -> list[GlyphRecord]:
    """
    mdb ファイル の「文字属性辞書」テーブルを読み込み、
    list[GlyphRecord] に変換して返す。
    対応する mdb ファイル：
    - deluxe文字選択DWPI明朝4.10版V2.0.mdb
    - deluxe文字選択DWPIex明朝1.2版.mdb
    """

    records: list[GlyphRecord] = []

    # --- mdb-export を使って CSV を取得
    csv_text = subprocess.check_output(
        ["mdb-export", str(mdb_path), "文字属性辞書"],
        encoding="utf-8"
    )

    # --- CSV をパース
    reader = csv.DictReader(csv_text.splitlines())

    for row in reader:
        comments = []

        # --- name（必須）
        glyph_name = row["MJ文字図形名"].strip()

        # base: 代替文字コード または MS明朝コード
        raw_b = row["代替文字コード"]
        if raw_b:
            comments.append(f"代替")
        else:
            raw_b = row["MS明朝コード"]
            if raw_b:
                comments.append("MS明朝")
            else:
                comments.append("(基本なし)")
            
                    
        b = to_uplus_string(raw_b) if raw_b else None
        if b:
            ok, reason = validate_uplus_input(b)
            if not ok:
                raise ValueError(f"Invalid base for {glyph_name}: {reason}")

        # variant: DWPI明朝コード
        raw_v = row["DWPI明朝コード"]
        v = to_uplus_string(raw_v) if raw_v else None
        if v:
            ok, reason = validate_uplus_input(v)
            if not ok:
                raise ValueError(f"Invalid variant for {glyph_name}: {reason}")

        # --- active 判定
        active = v is not None

        if not active:
            comments.insert(0, "実装なし")
        if b:
            comments.insert(0, ucs_to_glyph(b))

        rec = GlyphRecord(
            name=glyph_name,
            b=b,
            v=v,
            active=active,
            comment=sanitize_comment(" ".join(comments)),
        )
        records.append(rec)

    return records
