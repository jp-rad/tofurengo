from pathlib import Path
from tools.core.model import GlyphRecord
from tools.loaders.load_mji_00602_xlsx import load_mji_00602_xlsx
from tools.loaders.load_mjih_00201_xlsx import load_mjih_00201_xlsx

def main():
    BASE = Path(__file__).resolve().parent.parent

    print("")

    xlsx_path = BASE / "data/mji.00602.xlsx"
    print("Absolute path:", xlsx_path)
    records = load_mji_00602_xlsx(xlsx_path)
    print("Total records:", len(records))
    _print_first5_last5(records)

    xlsx_path = BASE / "data/MJIH00201.xlsx"
    print("Absolute path:", xlsx_path)
    print("==字母==")
    records = load_mjih_00201_xlsx(xlsx_path, "jibo")
    print("Total records:", len(records))
    _print_first5_last5(records)
    
    xlsx_path = BASE / "data/MJIH00201.xlsx"
    print("Absolute path:", xlsx_path)
    print("==音価１==")
    records = load_mjih_00201_xlsx(xlsx_path, "onka")
    print("Total records:", len(records))
    _print_first5_last5(records)

def _print_first5_last5(items: list[GlyphRecord]):

    print("---- first 5 records ----")
    for i, rec in enumerate(items[:5]):
        print(f"[{i}] {rec.name}")
        print("  b      :", rec.b)
        print("  v      :", rec.v)
        print("  active :", rec.active)
        print("  comment:", rec.comment)
        print()

    print("---- last 5 records ----")
    last_items = items[-5:]
    start_index = len(items) - 5
    for offset, rec in enumerate(last_items):
        i = start_index + offset
        print(f"[{i}] {rec.name}")
        print("  b      :", rec.b)
        print("  v      :", rec.v)
        print("  active :", rec.active)
        print("  comment:", rec.comment)
        print()

if __name__ == "__main__":
    main()
