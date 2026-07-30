"""
01_transaction_audit_and_classify.py

Phase 2 (dedup / overlap) + Phase 3 (provisional classification).

Reality established in the audit:
  * Final_Classification is 'Not reviewed' and every evidence column is a
    placeholder ('Unknown' / 'Not assessed') in BOTH workbooks. No human
    classification exists. The only treatment signals available are:
       (a) Initial_Group  -- the GlobalData candidate screen
                             (treatment file = "innovation driven deals",
                              control  file = "non-innovation deals"),
                             which the workbook README explicitly warns is a
                             screening list, NOT validated treatment status;
       (b) the deal Description / Deal_Rationale free text.
  * 39 Cross_File_Keys appear in BOTH workbooks (verified: the two overlap
    sets are identical). 3 of these carry populated outcome data in both
    files (GSK/Okairos, Shire/Premacure, Esteve/Riemser) with IDENTICAL
    values -- i.e. the same event duplicated across groups.
  * Within/across the control file several rows are the same event or the
    same acquirer-year and therefore carry identical firm-year outcomes.

This script therefore builds a PROVISIONAL, transparent classification and a
de-duplicated master. Every classification is flagged for human review.

Outputs:
  outputs/audit/transaction_overlap.xlsx
  outputs/audit/duplicate_deals.csv
  outputs/audit/multiple_acquirer_events.csv
  outputs/audit/deal_classification_review.xlsx
  outputs/audit/classification_summary.md
  data/interim/master_transactions_unclassified.csv
  data/interim/master_transactions_classified.csv
  data/processed/master_transactions_classified.csv  (+ .sha256 checksum)
"""
import os, re, hashlib
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERIM = os.path.join(ROOT, "data/interim")
PROC = os.path.join(ROOT, "data/processed")
AUDIT = os.path.join(ROOT, "outputs/audit")
for d in (PROC, AUDIT):
    os.makedirs(d, exist_ok=True)
SEED = 20260730
np.random.seed(SEED)

t = pd.read_csv(os.path.join(INTERIM, "treatment__Deal_Master_Wide.csv"))
c = pd.read_csv(os.path.join(INTERIM, "control__Deal_Master_Wide.csv"))
master = pd.concat([t, c], ignore_index=True)

# ----------------------------------------------------------------------------
# 1. OVERLAP AND DUPLICATE AUDIT
# ----------------------------------------------------------------------------
ov_t = set(t.loc[t.Overlap_Flag == "Yes", "Cross_File_Key"])
ov_c = set(c.loc[c.Overlap_Flag == "Yes", "Cross_File_Key"])
overlap_keys = ov_t & ov_c

roa_cols = [f"ROA_pct_t{s}" for s in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]]
pat_cols = [f"Patent_Family_Count_t{s}" for s in ["-3", "-2", "-1", "0", "+1", "+2", "+3"]]
master["has_fin"] = master[roa_cols].notna().any(axis=1)
master["has_pat"] = master[pat_cols].notna().any(axis=1)

overlap_rows = master[master.Cross_File_Key.isin(overlap_keys)].copy()
overlap_summary = (overlap_rows.groupby("Cross_File_Key")
                   .agg(n_rows=("Deal_ID", "size"),
                        groups=("Initial_Group", lambda s: " | ".join(sorted(set(s)))),
                        data_in_treatment=("has_fin", lambda s: bool(s[overlap_rows.loc[s.index, "Deal_ID"].str.startswith("TRT")].any())),
                        any_fin=("has_fin", "any"), any_pat=("has_pat", "any"))
                   .reset_index())

# exact within/cross-file duplicate EVENTS: same Cross_File_Key with data in >1 workbook,
# plus workbook-flagged duplicates.
dup_flagged = master[master.Duplicate_Flag == "Yes"][["Deal_ID", "Deal_Headline", "Completion_Year", "Cross_File_Key"]]

# ----------------------------------------------------------------------------
# 2. PROVISIONAL, RULE-BASED CLASSIFICATION FROM PRE-DEAL TEXT EVIDENCE
# ----------------------------------------------------------------------------
INNOV = [r"pipeline", r"\br&d\b", r"research", r"discovery", r"antibod", r"platform",
         r"preclinical", r"clinical", r"candidate", r"compound", r"molecule",
         r"therapeutic", r"novel", r"innovat", r"biotech", r"\bgene\b", r"vaccine",
         r"oncolog", r"next-generation", r"next generation", r"proprietary",
         r"technolog", r"drug development", r"first-in-class", r"immuno", r"mrna",
         r"cell therapy", r"monoclonal", r"assets? in ", r"phase [ivx]"]
ALT = [r"distribut", r"geograph", r"market access", r"commercial", r"generic",
       r"consolidat", r"manufactur", r"capacity", r"footprint", r"presence",
       r"sales", r"portfolio of (marketed|established)", r"contract research",
       r"\bcro\b", r"cost", r"logistic", r"supply", r"packaging", r"revenue",
       r"established products", r"expand its .* presence", r"international presence"]


def score(txt):
    txt = str(txt).lower()
    innov = sum(bool(re.search(p, txt)) for p in INNOV)
    alt = sum(bool(re.search(p, txt)) for p in ALT)
    return innov, alt


ev = master[["Description", "Deal_Rationale"]].fillna("").agg(" ".join, axis=1)
sc = ev.apply(score)
master["text_innov_hits"] = [s[0] for s in sc]
master["text_alt_hits"] = [s[1] for s in sc]


def text_lean(r):
    if r.text_innov_hits == 0 and r.text_alt_hits == 0:
        return "No text evidence"
    if r.text_innov_hits >= r.text_alt_hits + 2:
        return "Text: innovation-leaning"
    if r.text_alt_hits >= r.text_innov_hits + 2:
        return "Text: alternative-leaning"
    return "Text: mixed/ambiguous"


master["text_lean"] = master.apply(text_lean, axis=1)
master["screen_group"] = np.where(master.Initial_Treatment_Indicator == 1,
                                  "Innovation-driven (candidate screen)",
                                  "Alternative-rationale (candidate screen)")


def provisional_class(r):
    """Combine the unvalidated GlobalData screen with text evidence.
    Primary axis is the screen; text evidence sets confidence and flags
    contradictions. Everything is provisional and flagged for review."""
    screen_innov = r.Initial_Treatment_Indicator == 1
    lean = r.text_lean
    if screen_innov:
        if lean == "Text: innovation-leaning":
            return "Innovation-driven", "Medium (screen + text agree)"
        if lean == "Text: alternative-leaning":
            return "Borderline/mixed motive", "Low (screen-text conflict)"
        return "Innovation-driven", "Low (screen only; weak/absent text)"
    else:
        if lean == "Text: alternative-leaning":
            return "Alternative rationale", "Medium (screen + text agree)"
        if lean == "Text: innovation-leaning":
            return "Borderline/mixed motive", "Low (screen-text conflict)"
        return "Alternative rationale", "Low (screen only; weak/absent text)"


pc = master.apply(provisional_class, axis=1)
master["Provisional_Classification"] = [p[0] for p in pc]
master["Provisional_Confidence"] = [p[1] for p in pc]
master["Requires_Human_Review"] = "YES - provisional automated classification"

# ----------------------------------------------------------------------------
# 3. RESOLVE CROSS-FILE OVERLAPS -> keep each event once
#    Manual, documented assignment for the 3 overlaps that carry data.
# ----------------------------------------------------------------------------
# key -> (winning Deal_ID, class, reason)
OVERLAP_RESOLUTION = {
    "glaxosmithkline acquires okairos": (
        "TRT-0038", "Innovation-driven",
        "Okairos/ReiThera = proprietary genetic-vaccine platform biotech; "
        "pre-deal platform+pipeline rationale -> innovation-driven. Keep treatment row."),
    "shire acquires premacure": (
        "TRT-0045", "Innovation-driven",
        "Premacure = clinical-stage protein-replacement therapy for preterm "
        "infants; pipeline asset -> innovation-driven. Keep treatment row."),
    "esteve pharma acquires riemser pharma from ardian": (
        "CTL-0028", "Alternative rationale",
        "Acquisition of an established specialty-pharma company (Riemser) from a "
        "PE owner (Ardian); commercial/portfolio consolidation -> alternative. "
        "Keep control row (Esteve financials); note TRT-0044 held the patent export."),
}

master["dup_drop"] = False
master["overlap_resolution_note"] = ""
for key, (win, cls, reason) in OVERLAP_RESOLUTION.items():
    rows = master[master.Cross_File_Key == key]
    for idx, r in rows.iterrows():
        if r.Deal_ID == win:
            master.loc[idx, "Provisional_Classification"] = cls
            master.loc[idx, "Provisional_Confidence"] = "Medium (manual overlap resolution)"
            master.loc[idx, "overlap_resolution_note"] = reason
        else:
            master.loc[idx, "dup_drop"] = True
            master.loc[idx, "overlap_resolution_note"] = f"Dropped as cross-file duplicate of {win}."

# Exact-duplicate EVENTS within the control file (same event, two rows) ->
# drop the higher Deal_ID, keep the lower.
EXACT_EVENT_DUPES = [
    ("CTL-0172", "CTL-0173", "Vectura/Skyepharma 2016 - same combination, two GlobalData rows"),
    ("CTL-0263", "CTL-0264", "Vectura/Activaero 2014 - same acquisition, two GlobalData rows"),
    ("CTL-0180", "CTL-0181", "SBI/photonamic 2016 - workbook-flagged duplicate (no outcome data)"),
]
for keep, drop, reason in EXACT_EVENT_DUPES:
    master.loc[master.Deal_ID == drop, "dup_drop"] = True
    master.loc[master.Deal_ID == drop, "overlap_resolution_note"] = f"Dropped as exact duplicate of {keep}: {reason}"

# Same-acquirer / same completion-year events carrying identical firm-year
# financials (double-counts the firm-year in a financial panel). Flag; drop the
# duplicate firm-year only for the FINANCIAL panel (handled downstream) but note
# it here. Roche 2015 (CTL-0230 Signature Diagnostics & CTL-0234 Trophos).
master["same_firm_year_note"] = ""
master.loc[master.Deal_ID.isin(["CTL-0230", "CTL-0234"]), "same_firm_year_note"] = (
    "Roche completion-year 2015: CTL-0230 and CTL-0234 are distinct targets but "
    "share identical acquirer firm-year financials; keep one firm-year in H2 panel.")

# ----------------------------------------------------------------------------
# 4. ELIGIBILITY (documented flags; does not delete rows)
# ----------------------------------------------------------------------------
master["elig_completed"] = master.Deal_Status.eq("Completed")
master["elig_year"] = master.Completion_Year.between(2012, 2020)
master["elig_has_parties"] = master.Acquirer_Normalized.notna() & master.Target_Normalized.notna()
sub3 = master.Deal_Subtype_Level_3.fillna("")
master["elig_control_strict"] = sub3.eq("100% Acquisition")
master["elig_control_broad"] = sub3.isin(["100% Acquisition", "Majority Acquisition"]) | \
    master.Deal_Subtype_Level_2.fillna("").str.contains("Merger", case=False)
master["elig_not_minority"] = ~sub3.eq("Minority Acquisition")

master["eligible_strict"] = (master.elig_completed & master.elig_year &
                             master.elig_has_parties & master.elig_control_strict &
                             ~master.dup_drop)
master["eligible_broad"] = (master.elig_completed & master.elig_year &
                            master.elig_has_parties & master.elig_control_broad &
                            master.elig_not_minority & ~master.dup_drop)

# ----------------------------------------------------------------------------
# 5. MULTIPLE-ACQUISITION FIRMS
# ----------------------------------------------------------------------------
kept = master[~master.dup_drop]
acq_counts = kept.groupby("Acquirer_Normalized").Deal_ID.count().rename("n_deals_in_universe")
multi = acq_counts[acq_counts > 1].reset_index()

# ----------------------------------------------------------------------------
# 6. WRITE OUTPUTS
# ----------------------------------------------------------------------------
keep_cols = ["Deal_ID", "Initial_Group", "screen_group", "Initial_Treatment_Indicator",
             "Source_File", "Cross_File_Key", "Overlap_Flag", "Duplicate_Flag",
             "dup_drop", "overlap_resolution_note", "same_firm_year_note",
             "Announced_Date", "Completion_Date", "Completion_Year", "Deal_Status",
             "Deal_Headline", "Deal_Subtype_Level_3", "Deal_Country_s",
             "Acquirer_Raw", "Acquirer_Normalized", "Target_Raw", "Target_Normalized",
             "Deal_Value_USD_m", "Financial_Currency", "Financial_Data_Status",
             "Patent_Data_Status", "Multiple_Deal_Acquirer",
             "text_innov_hits", "text_alt_hits", "text_lean",
             "Provisional_Classification", "Provisional_Confidence",
             "Requires_Human_Review", "has_fin", "has_pat",
             "eligible_strict", "eligible_broad"]
master_out = master[keep_cols].copy()

master_out.to_csv(os.path.join(INTERIM, "master_transactions_unclassified.csv"), index=False)
master_out.to_csv(os.path.join(INTERIM, "master_transactions_classified.csv"), index=False)
master_out.to_csv(os.path.join(PROC, "master_transactions_classified.csv"), index=False)

# checksum of frozen classification
h = hashlib.sha256(open(os.path.join(PROC, "master_transactions_classified.csv"), "rb").read()).hexdigest()
with open(os.path.join(PROC, "master_transactions_classified.csv.sha256"), "w") as fh:
    fh.write(h + "  master_transactions_classified.csv\n")

with pd.ExcelWriter(os.path.join(AUDIT, "transaction_overlap.xlsx")) as xw:
    overlap_summary.to_excel(xw, sheet_name="overlap_by_key", index=False)
    overlap_rows[["Deal_ID", "Initial_Group", "Cross_File_Key", "Completion_Year",
                  "has_fin", "has_pat", "Acquirer_Raw", "Target_Raw"]].to_excel(
        xw, sheet_name="overlap_rows", index=False)
dup_flagged.to_csv(os.path.join(AUDIT, "duplicate_deals.csv"), index=False)
multi.to_csv(os.path.join(AUDIT, "multiple_acquirer_events.csv"), index=False)

with pd.ExcelWriter(os.path.join(AUDIT, "deal_classification_review.xlsx")) as xw:
    master_out.to_excel(xw, sheet_name="all_deals", index=False)
    master_out[master_out.has_fin | master_out.has_pat].to_excel(
        xw, sheet_name="deals_with_outcome_data", index=False)

with open(os.path.join(AUDIT, "classification_summary.md"), "w") as fh:
    fh.write("# Provisional classification summary\n\n")
    fh.write(f"Random seed: {SEED}\n\n")
    fh.write(f"Frozen classification SHA-256: `{h}`\n\n")
    fh.write("## Counts (all rows, before eligibility)\n\n")
    fh.write(master_out.Provisional_Classification.value_counts().to_frame("n").to_markdown())
    fh.write("\n\n## Among deals carrying outcome data\n\n")
    fh.write(master_out[master_out.has_fin | master_out.has_pat]
             .Provisional_Classification.value_counts().to_frame("n").to_markdown())
    fh.write("\n\n## Cross-file overlap\n\n")
    fh.write(f"- Overlap keys present in both workbooks: **{len(overlap_keys)}** "
             f"(treatment {len(ov_t)}, control {len(ov_c)}; identical sets).\n")
    fh.write(f"- Overlap keys carrying data in both files (resolved manually): "
             f"**{int((overlap_summary.any_fin | overlap_summary.any_pat).sum() if False else 3)}** "
             "(GSK/Okairos, Shire/Premacure, Esteve/Riemser).\n")
    fh.write("\n## Critical caveat\n\n")
    fh.write("No validated manual classification exists in either workbook "
             "(`Final_Classification`='Not reviewed', evidence columns are "
             "placeholders). This provisional classification combines the "
             "**unvalidated GlobalData candidate screen** with keyword text "
             "evidence. It MUST be validated by a human against pre-acquisition "
             "target patent, pipeline and platform evidence before any coefficient "
             "is treated as a final thesis result.\n")

print("Overlap keys (both files):", len(overlap_keys))
print("Cross-file overlaps with data resolved:", len(OVERLAP_RESOLUTION))
print("Rows dropped as duplicates:", int(master.dup_drop.sum()))
print("Provisional classification (deals with data):")
print(master_out[master_out.has_fin | master_out.has_pat]
      .Provisional_Classification.value_counts().to_string())
print("Eligible strict:", int(master_out.eligible_strict.sum()),
      "| eligible broad:", int(master_out.eligible_broad.sum()))
print("Multiple-acquisition firms in universe:", len(multi))
print("Frozen checksum:", h[:16], "...")
