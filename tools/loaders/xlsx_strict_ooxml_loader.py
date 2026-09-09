"""
xlsx_strict_ooxml_loader.py
===========================

Strict OOXML (ISO/IEC 29500 Strict) 形式の XLSX を読み取るためのローダー。

このモジュールは Strict OOXML の構造に従い、次の処理を行う：

- workbook.xml から最初のシートの XML ファイル名を取得
- sharedStrings.xml を読み込み、文字列セルの値を復元
- sheet XML を解析し、行ごとに {セル参照: 値} の dict を生成
- A1, B1, C1... のセル参照から列名を復元（ヘッダー行）

対象：
- Strict OOXML 形式の XLSX

非対象：
- Transitional OOXML（一般的な Excel）
- xls（BIFF）
- xlsm（マクロ付き）

本モジュールは Strict OOXML の仕様に基づき、
セル値をそのまま正確に取得するためのローダーである。
"""

import zipfile
import xml.etree.ElementTree as ET


# ------------------------------------------------------------
# workbook.xml → 1枚目のシートの XML ファイル名を取得
# ------------------------------------------------------------

def find_first_sheet_filename(z: zipfile.ZipFile) -> str:
    """
    Strict OOXML の workbook.xml は r:id を持たないことがある。
    その場合は sheetId を用いて最初のシートを特定する。
    """

    wb_xml = z.read("xl/workbook.xml")
    wb_root = ET.fromstring(wb_xml)

    ns_uri = wb_root.tag.split("}")[0].strip("{")
    ns = f"{{{ns_uri}}}"

    sheet_elems = wb_root.findall(f".//{ns}sheet")
    if not sheet_elems:
        raise ValueError("workbook.xml に <sheet> がありません")

    first_sheet = sheet_elems[0]

    # Strict OOXML: r:id が存在しない
    rid = first_sheet.attrib.get(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    )

    if rid is None:
        sheet_id = first_sheet.attrib.get("sheetId")
        if sheet_id is None:
            raise ValueError("Strict OOXML: sheetId がありません")
        return f"xl/worksheets/sheet{sheet_id}.xml"

    # Transitional OOXML: r:id が存在する場合
    rels_xml = z.read("xl/_rels/workbook.xml.rels")
    rels_root = ET.fromstring(rels_xml)

    rels_ns_uri = rels_root.tag.split("}")[0].strip("{")
    rels_ns = f"{{{rels_ns_uri}}}"

    for rel in rels_root.findall(f".//{rels_ns}Relationship"):
        if rel.attrib.get("Id") == rid:
            target = rel.attrib.get("Target")
            return "xl/" + target

    raise ValueError(f"workbook.xml.rels に r:id={rid} がありません")


# ------------------------------------------------------------
# sharedStrings.xml の読み込み
# ------------------------------------------------------------

def load_shared_strings(z: zipfile.ZipFile, rich: bool = False) -> list[str]:
    """
    sharedStrings.xml を読み込み、文字列セルの値を復元する。

    rich=True の場合は、複数の <t> を連結して 1つの文字列として扱う。
    """

    if "xl/sharedStrings.xml" not in z.namelist():
        return []

    ss_xml = z.read("xl/sharedStrings.xml")
    ss_root = ET.fromstring(ss_xml)

    ss_ns_uri = ss_root.tag.split("}")[0].strip("{")
    ss_ns = f"{{{ss_ns_uri}}}"

    shared = []

    if rich:
        # rich text: <r><t> が複数ある場合は連結する
        for si in ss_root.findall(f".//{ss_ns}si"):
            text = "".join(t.text or "" for t in si.findall(f".//{ss_ns}t"))
            shared.append(text)
    else:
        # 通常の文字列セル
        for si in ss_root.findall(f".//{ss_ns}si"):
            t = si.find(f".//{ss_ns}t")
            shared.append(t.text if t is not None else "")

    return shared


# ------------------------------------------------------------
# sheet XML → 行データ抽出
# ------------------------------------------------------------

def load_sheet_rows(z: zipfile.ZipFile, sheet_filename: str) -> list[dict[str, str]]:
    """
    sheet XML を解析し、行ごとに {セル参照: 値} の dict を返す。
    """

    sheet_xml = z.read(sheet_filename)
    root = ET.fromstring(sheet_xml)

    ns_uri = root.tag.split("}")[0].strip("{")
    ns = f"{{{ns_uri}}}"

    shared = load_shared_strings(z)

    rows = []

    for row in root.findall(f".//{ns}row"):
        record = {}

        for c in row.findall(f"{ns}c"):
            cell_ref = c.attrib.get("r")
            cell_type = c.attrib.get("t")
            v = c.find(f"{ns}v")

            if v is None:
                value = ""
            else:
                raw = v.text
                if cell_type == "s":
                    # sharedStrings の index
                    value = shared[int(raw)]
                else:
                    value = raw

            record[cell_ref] = value

        rows.append(record)

    return rows


# ------------------------------------------------------------
# ヘッダー解析（A1, B1, C1 → 列名）
# ------------------------------------------------------------

def parse_header(rows: list[dict[str, str]]) -> dict[str, str]:
    """
    1行目（ヘッダー行）のセル参照から列名を復元する。

    A1 → A, B1 → B のように列記号を抽出し、
    {列記号: 列名} の dict を返す。
    """

    if not rows:
        raise ValueError("sheet XML に <row> がありません")

    header_row = rows[0]
    headers = {}

    for cell_ref, value in header_row.items():
        col = "".join(c for c in cell_ref if c.isalpha())
        headers[col] = value.strip()

    return headers
