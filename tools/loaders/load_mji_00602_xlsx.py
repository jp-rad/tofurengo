from pathlib import Path
import zipfile

from tofurengo.ucs import ucs_to_glyph

from tools.core.model import GlyphRecord
from tools.core.normalize import (
    to_uplus_string,
    validate_uplus_input,
    pick_ucs_by_rep,
    sanitize_comment,
)
from tools.loaders.xlsx_strict_ooxml_loader import (
    find_first_sheet_filename,
    load_sheet_rows,
    parse_header,
)

# ------------------------------------------------------------
# 列名（mji.00602.xlsx 固有）
# ------------------------------------------------------------

COL_MJ_NAME = "MJ文字図形名"
COL_BASE     = "対応するUCS"
COL_VARIANT  = "実装したMoji_JohoコレクションIVS"
COL_FONT     = "font"
COL_NOTE     = "備考"

REQUIRED_COLUMNS = {
    COL_MJ_NAME,
    COL_BASE,
    COL_VARIANT,
    COL_FONT,
    COL_NOTE,
}


# ------------------------------------------------------------
# ローダー本体
# ------------------------------------------------------------

def load_mji_00602_xlsx(path: Path) -> list[GlyphRecord]:
    """
    mji.00602.xlsx（MJ漢字編）を Strict OOXML として読み込むローダー。

    本ローダーは GlyphRecord の属性 b / v を次の仕様に従って構築する：

    4. Attributes（属性）
    4.1 b — base（基本字形）
        IVS を含まない UCS コードポイント並び。

    4.2 v — variant（異体字）
        IVS を含む UCS コードポイント並び。
        異体字が存在しない場合は v=b。

    処理内容：
    - workbook.xml から最初のシートを特定
    - sharedStrings.xml と sheet XML を解析し、セル値を復元
    - ヘッダー行から列名を取得
    - base（代表文字）と variant（Moji_Joho コレクション IVS）を仕様に従って構築
    - font="実装なし" の場合は active=False とする
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
        comments = []

        glyph_name = get(row_dict, COL_MJ_NAME)
        if glyph_name == "":
            continue

        # --- active 判定（font="実装なし" → False） ---
        font_value = get(row_dict, COL_FONT)
        active = font_value != "実装なし"
        if not active:
            comments.append(font_value)

        # ------------------------------------------------------------
        # b — base（基本字形）
        #   IVS を含まない UCS コードポイント並び
        # ------------------------------------------------------------
        base_raw = get(row_dict, COL_BASE)
        base = to_uplus_string(base_raw)

        if base:
            ok, reason = validate_uplus_input(base)
            if not ok:
                raise ValueError(f"Invalid base for {glyph_name}: {reason}")

            comments.append(ucs_to_glyph(base))

            # ------------------------------------------------------------
            # v — variant（異体字）
            #   IVS を含む UCS コードポイント並び
            #   異体字が存在しない場合は v=b
            # ------------------------------------------------------------
            variant_raw = get(row_dict, COL_VARIANT)

            if variant_raw == "":
                # 異体字が存在しない → v=b
                variant = base
            else:
                # 複数候補がある場合はコメントに残す
                if ";" in variant_raw:
                    comments.append(variant_raw)

                # base と rep を比較して適切な UCS を選択
                variant = pick_ucs_by_rep(variant_raw, base)

                ok, reason = validate_uplus_input(variant)
                if not ok:
                    raise ValueError(f"Invalid variant for {glyph_name}: {reason}")

        else:
            # base が空 → v も空
            base = None
            variant = None

        rec = GlyphRecord(
            name=glyph_name,
            b=base,
            v=variant,
            active=active,
            comment=sanitize_comment(" ".join(comments)),
        )

        records.append(rec)

    return records
