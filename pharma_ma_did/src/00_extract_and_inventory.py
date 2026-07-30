"""
00_extract_and_inventory.py
Extract every sheet of the two DiD data workbooks to interim CSVs and
produce the Phase-1 file inventory. Raw workbooks are never modified.

Inputs : data/raw/Treatment_Group_DiD_Data_Workbook.xlsx
         data/raw/Control_Group_DiD_Data_Workbook.xlsx
Outputs: data/interim/<group>__<sheet>.csv
         outputs/audit/file_inventory.csv / .xlsx / .md
"""
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = {
    "treatment": os.path.join(ROOT, "data/raw/Treatment_Group_DiD_Data_Workbook.xlsx"),
    "control": os.path.join(ROOT, "data/raw/Control_Group_DiD_Data_Workbook.xlsx"),
}
INTERIM = os.path.join(ROOT, "data/interim")
AUDIT = os.path.join(ROOT, "outputs/audit")
os.makedirs(INTERIM, exist_ok=True)
os.makedirs(AUDIT, exist_ok=True)

# Sheets whose real header sits on the given 0-indexed row.
HEADER_ROW = {
    "Deal_Master_Wide": 1,          # row 0 = section banners
    "Panel_DiD": 0,
    "Financial_Long_Raw": {"treatment": 1, "control": 0},
    "Financial_Import_Log": {"treatment": 1, "control": 0},
    "Patent_Import_Log": 1,
    "Patent_Year_Summary": 1,
    "Patent_Family_Long": 1,
}


def header_row(sheet: str, group: str) -> int:
    spec = HEADER_ROW.get(sheet, 0)
    return spec[group] if isinstance(spec, dict) else spec


inventory = []
for group, path in RAW.items():
    xl = pd.ExcelFile(path)
    for sheet in xl.sheet_names:
        if sheet in ("README", "Summary", "Variable_Dictionary", "Lists"):
            df = pd.read_excel(path, sheet_name=sheet, header=None)
            use = "documentation / dropdown lists"
        else:
            df = pd.read_excel(path, sheet_name=sheet, header=header_row(sheet, group))
            df = df.dropna(how="all")
            use = {
                "Deal_Master_Wide": "master deal table, one row per deal, event-window data",
                "Panel_DiD": "pre-reshaped deal-year panel (formula-derived)",
                "Financial_Import_Log": "Bloomberg file-to-deal mapping log",
                "Financial_Long_Raw": "Bloomberg firm-year historical actuals (long)",
                "Patent_Import_Log": "Lens file-to-deal mapping log",
                "Patent_Year_Summary": "patent families & citations by priority year",
                "Patent_Family_Long": "one row per deduplicated simple patent family",
            }.get(sheet, "")
        out = os.path.join(INTERIM, f"{group}__{sheet}.csv")
        df.to_csv(out, index=False)
        inventory.append({
            "file_path": path,
            "workbook": os.path.basename(path),
            "group": group,
            "sheet": sheet,
            "n_rows": len(df),
            "n_cols": df.shape[1],
            "inferred_source": ("GlobalData" if sheet == "Deal_Master_Wide"
                                 else "Bloomberg" if "Financial" in sheet
                                 else "Lens.org" if "Patent" in sheet
                                 else "workbook documentation"),
            "intended_use": use,
            "interim_csv": os.path.relpath(out, ROOT),
        })

inv = pd.DataFrame(inventory)
inv.to_csv(os.path.join(AUDIT, "file_inventory.csv"), index=False)
inv.to_excel(os.path.join(AUDIT, "file_inventory.xlsx"), index=False)
with open(os.path.join(AUDIT, "file_inventory.md"), "w") as fh:
    fh.write("# File inventory\n\n")
    fh.write("Two uploaded workbooks; all other source files (GlobalData exports, "
             "Bloomberg per-company workbooks, Lens CSV exports) exist only as "
             "already-imported content inside these workbooks.\n\n")
    fh.write(inv.to_markdown(index=False))
print(inv[["group", "sheet", "n_rows", "n_cols"]].to_string(index=False))
print("\nInventory written.")
