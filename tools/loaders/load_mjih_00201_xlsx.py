from pathlib import Path
from typing import Literal
import zipfile

from tofurengo.ucs import glyph_to_ucs

from tools.core.model import GlyphRecord
from tools.core.normalize import (
    to_uplus_string,
    validate_uplus_input,
    sanitize_comment,
)

from tools.loaders.xlsx_strict_ooxml_loader import (
    find_first_sheet_filename,
    load_sheet_rows,
    parse_header,
)


# ------------------------------------------------------------
# 列名（MJIH00201.xlsx 固有）
# ------------------------------------------------------------

COL_MJ_NAME     = "MJ文字図形名"
COL_FONT        = "font文字"
COL_UCS         = "UCS符号位置"
COL_JIBO        = "字母"
COL_JIBO_UCS    = "字母のUCS符号位置"
COL_ONKA1       = "音価１"
COL_ONKA2       = "音価２"
COL_ONKA3       = "音価３"
COL_NOTE        = "備考"

REQUIRED_COLUMNS = {
    COL_MJ_NAME,
    COL_FONT,
    COL_UCS,
    COL_JIBO,
    COL_JIBO_UCS,
    COL_ONKA1,
    COL_ONKA2,
    COL_ONKA3,
    COL_NOTE,
}


# ------------------------------------------------------------
# ローダー本体
# ------------------------------------------------------------

def load_mjih_00201_xlsx(path: Path, base_from: Literal["jibo", "onka"]) -> list[GlyphRecord]:
    """
    MJ文字情報一覧表 変体仮名編 Ver.002.01 を Strict OOXML として読み込むローダー。

    本ローダーは GlyphRecord の属性 b / v を次の仕様に従って構築する：

    4. Attributes（属性）
    4.1 b — base（基本字形）
        IVS を含まない UCS コードポイント並び。
        本ファイルでは「字母のUCS符号位置」もしくは「」が b に相当する。

        base_from:
            "jibo" → 字母を基本字形とする
            "onka" → 音価を基本字形とする（音価１）
        
    4.2 v — variant（異体字）
        IVS を含む UCS コードポイント並び。
        本ファイルでは「変体仮名自身の UCS符号位置」が v に相当する。
        UCS が未割り当ての場合は v=None とし、active=False とする。

    comment は次の情報を連結して構築する：
        字母 / 音価1 / 音価2 / 音価3 / 備考
    """

    with zipfile.ZipFile(path, "r") as z:
        sheet_filename = find_first_sheet_filename(z)
        rows = load_sheet_rows(z, sheet_filename)
        headers = parse_header(rows)

    # --- 必須列チェック ---
    if not REQUIRED_COLUMNS.issubset(headers.values()):
        missing = REQUIRED_COLUMNS - set(headers.values())
        raise ValueError(f"Missing required columns in XLSX: {missing}")

    # 列名 → 列記号（A, B, C...）
    col_map = {v: k for k, v in headers.items()}

    def get(row_dict, col_name):
        """
        行 dict から列名で値を取得する。
        A列なら A1/A2/A3... のように cell_ref.startswith(col) で判定。
        """
        col = col_map[col_name]
        for cell_ref, value in row_dict.items():
            if cell_ref.startswith(col):
                return value.strip()
        return ""

    # --- レコード生成 ---
    records: list[GlyphRecord] = []

    for row_dict in rows[1:]:
        glyph_name = get(row_dict, COL_MJ_NAME)
        if glyph_name == "":
            continue

        # ------------------------------------------------------------
        # b — base（基本字形）
        #   字母の UCS（IVS を含まない UCS コードポイント並び）
        #   もしくは
        #   音価1 （ひらがなの１文字）
        # ------------------------------------------------------------
        if base_from == "jibo":
            b_col = COL_JIBO_UCS
            b_raw = get(row_dict, b_col)
        else:  # "phonetic"
            b_col = COL_ONKA1
            b_char = get(row_dict, b_col)
            b_raw = glyph_to_ucs(b_char)
        
        b = to_uplus_string(b_raw)
        ok, reason = validate_uplus_input(b)
        if not ok:
            raise ValueError(f"Invalid {b_col} for {glyph_name}: {reason}")

        # ------------------------------------------------------------
        # v — variant（異体字）
        #   変体仮名自身の UCS（IVS を含む UCS コードポイント並び）
        #   UCS 未割り当ての場合は v=None, active=False
        # ------------------------------------------------------------
        ucs_raw = get(row_dict, COL_UCS)

        if ucs_raw == "":
            v = None
            active = False
        else:
            v = to_uplus_string(ucs_raw)
            ok, reason = validate_uplus_input(v)
            if not ok:
                raise ValueError(f"Invalid UCS for {glyph_name}: {reason}")
            active = True

        # ------------------------------------------------------------
        # comment（字母 + 音価1/2/3 + 備考）
        # ------------------------------------------------------------
        jimo  = get(row_dict, COL_JIBO)
        onka1 = get(row_dict, COL_ONKA1)
        onka2 = get(row_dict, COL_ONKA2)
        onka3 = get(row_dict, COL_ONKA3)
        note  = get(row_dict, COL_NOTE)

        comment_parts = [
            f"[{COL_JIBO}]" if base_from == "jibo" else f"[{COL_ONKA1}]",
            jimo,
            onka1 if onka1 else "",
            onka2 if onka2 else "",
            onka3 if onka3 else "",
            note if note else "",
        ]

        comment = sanitize_comment(" ".join([p for p in comment_parts if p]))

        rec = GlyphRecord(
            name=glyph_name,
            b=b,
            v=v,
            active=active,
            comment=comment,
        )

        records.append(rec)

    return records
