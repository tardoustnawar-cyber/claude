"""Phase C+D: eligibility, canonical events, and evidence-based classification.

Classification is performed on PRE-COMPLETION EVIDENCE (GlobalData deal
descriptions + embedded announcement text), not on the source workbook.
Only the data-carrying deals (those that can enter H1 or H2) are individually
adjudicated, per the master-prompt priority rule. All other deals are marked
'Insufficient evidence (not data-carrying)'.

No network access was available in this environment, so evidence is limited to
the workbook-imported descriptions/rationales (hierarchy levels 1-2 embedded
announcement text, and level 5 GlobalData rationale). This is disclosed in the
classification summary.
"""
import hashlib
import json
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
PROC = ROOT / "data" / "processed"
AUDIT = ROOT / "outputs" / "audit"
PROC.mkdir(parents=True, exist_ok=True)

m = pd.read_csv(INTERIM / "deal_master_unclassified.csv")

# ---- canonical economic events (collapse within- and cross-file dups) ----
canon = (m.groupby("econ_key_date")
          .agg(member_deal_ids=("deal_event_id", lambda s: ";".join(sorted(s))),
               source_workbooks=("source_workbook", lambda s: ";".join(sorted(set(s)))),
               n_rows=("deal_event_id", "size"),
               acquirer=("Acquirer_Raw", "first"),
               target=("Target_Raw", "first"),
               completion_date=("Completion_Date", "first"),
               completion_year=("Completion_Year", "first"),
               subtype2=("Deal_Subtype_Level_2", lambda s: ";".join(sorted(set(s.astype(str))))),
               subtype3=("Deal_Subtype_Level_3", lambda s: ";".join(sorted(set(s.dropna().astype(str))))),
               ctrl_transfer=("Initial_Control_Transfer_Status", lambda s: ";".join(sorted(set(s.astype(str))))),
               fin_status=("Financial_Data_Status", lambda s: ";".join(sorted(set(s.astype(str))))),
               pat_status=("Patent_Data_Status", lambda s: ";".join(sorted(set(s.astype(str))))))
          .reset_index())
canon["completion_year"] = canon["completion_year"].astype(int)

def canon_id(key):
    return "EVT-" + hashlib.md5(key.encode()).hexdigest()[:8].upper()
canon["deal_event_id"] = canon["econ_key_date"].map(canon_id)

# ============================================================================
# Evidence-based classification of DATA-CARRYING events.
# Keyed by a representative member Deal_ID. Fields:
#   klass  : final classification
#   conf   : confidence
#   asset  : target innovation asset (or commercial asset)
#   just   : concise justification (pre-completion evidence only)
# ============================================================================
DECISIONS = {
 # --- High-confidence innovation-driven (material pre-deal R&D asset central) ---
 "TRT-0010": ("High-confidence innovation-driven","High","Nanobody technology platform + late-stage caplacizumab (aTTP) pipeline",
   "Announcement/rationale: acquire Ablynx to strengthen R&D strategy with Nanobody technology platform and late-stage investigational caplacizumab. Platform + late-stage pipeline central."),
 "TRT-0028": ("High-confidence innovation-driven","High","Monoclonal-antibody discovery platform + preclinical checkpoint assets",
   "Aduro acquires BioNovion to expand immunotherapy capabilities to monoclonal antibodies incl. preclinical assets inhibiting validated checkpoint pathways. R&D capability + pipeline central."),
 "TRT-0043": ("High-confidence innovation-driven","High","Sustained-release drug-formulation platform (Q Chip)",
   "Midatech acquires Q Chip to add oncology/ophthalmology programs based on the sustained-release platform. Platform + development programs central."),
 "TRT-0045": ("High-confidence innovation-driven","High","Protein-replacement therapy; Phase II neonatology candidate (Premacure)",
   "Shire acquires Premacure to enter neonatology with a novel protein-replacement therapy and continue an ongoing Phase II study. Late-stage pipeline central."),
 "TRT-0038": ("High-confidence innovation-driven","High","Novel vaccine platform technology + early-stage pipeline (Okairos)",
   "GSK acquires Okairos for its novel vaccine platform technology and early-stage vaccine assets (RSV/HCV/malaria/TB/ebola/HIV). Platform + pipeline central."),
 "TRT-0031": ("High-confidence innovation-driven","High","Cardiology cell-therapy pipeline with active clinical trial (Coretherapix)",
   "TiGenix acquires Coretherapix to expand its cell-therapy pipeline into cardiology; ongoing clinical trial asset central."),
 "CTL-0005": ("High-confidence innovation-driven","High","Gene-therapy discovery/development capability (Handl Therapeutics)",
   "UCB acquires Handl Therapeutics to accelerate gene-therapy ambition and strengthen discovery/development capabilities. R&D capability central. (Screen false negative: sat in comparison extract.)"),
 "CTL-0071": ("High-confidence innovation-driven","High","Novel Treg-depleting antibody in preclinical development (Tusk)",
   "Roche acquires Tusk to develop its novel antibody (regulatory T-cell depletion). Pipeline asset central. (Screen false negative.)"),
 "CTL-0229": ("High-confidence innovation-driven","High","Bioconjugation vaccine platform + early-stage bacterial-vaccine pipeline (GlycoVaxyn)",
   "GSK acquires remaining stake in GlycoVaxyn to develop a new generation of bacterial-infection vaccines; early-stage pipeline central. (Screen false negative.)"),
 "CTL-0230": ("High-confidence innovation-driven","High","Translational-oncology genomics platform + NGS diagnostics R&D (Signature Diagnostics)",
   "Roche acquires Signature Diagnostics to expand genomic-signature portfolio and advance NGS-diagnostics translational research. Platform/R&D central. (Screen false negative.)"),
 "CTL-0234": ("High-confidence innovation-driven","High","Neurodegeneration pipeline: Phase I TRO40303 + preclinical assets (Trophos)",
   "Roche acquires Trophos for its neuromuscular pipeline (Phase I TRO40303 + preclinical) to develop SMA medicines. Pipeline central. (Screen false negative.)"),
 "CTL-0281": ("High-confidence innovation-driven","High","Botulinum-toxin technology platform + IP portfolio + Phase II asset (Syntaxin)",
   "Ipsen acquires Syntaxin to enhance its toxin technology platform and IP and strengthen neurology R&D; Phase II asset. Platform/IP/pipeline central. (Screen false negative.)"),
 "CTL-0263": ("High-confidence innovation-driven","High","Smart-nebuliser device platform + late-stage drug-device pipeline (Activaero)",
   "Vectura acquires Activaero for late-stage product development and to extend its technology platform into smart-nebuliser drug-device products. Platform + late-stage pipeline central. (Screen false negative.)"),

 # --- Alternative-rationale (scale / geography / mature products / services) ---
 "TRT-0034": ("Alternative-rationale","High","Mature ophthalmic product portfolio + French commercial infrastructure (Doliage)",
   "Nicox acquires Doliage to add an ophthalmic product portfolio and complement its French commercial infrastructure. Commercial/product/geographic. (Screen false positive.)"),
 "TRT-0039": ("Alternative-rationale","Medium","Contract genomic-testing services + Nordic footprint (AROS)",
   "Eurofins acquires AROS to reinforce its testing-services position, expand genomic-services footprint into the Nordics, and leverage scale. Services/scale/geographic dominate. (Screen false positive.)"),
 "TRT-0044": ("Alternative-rationale","High","Specialty/OTC product portfolio + manufacturing + hospital-market access (Riemser)",
   "Esteve acquires Riemser for a specialty product portfolio, a production facility and hospital-market access ('transformation into specialty pharma'). Commercial/manufacturing/market-access. (Screen false positive.)"),
 "TRT-0036": ("Alternative-rationale","High","European commercial platform + distribution for BRINAVESS (Correvio)",
   "Cardiome acquires Correvio for an operational European commercial platform, global distribution and complementary products to launch BRINAVESS. Commercial/distribution. (Screen false positive.)"),
 "CTL-0038": ("Alternative-rationale","High","Generic-drug portfolio + CEE market access (LaborMed)",
   "Zentiva acquires LaborMed to strengthen CEE position, enter new markets and add OTC/generics competences. Generics/geographic."),
 "CTL-0055": ("Alternative-rationale","Medium","Generic/specialist portfolio; growth acceleration (Creo Pharma)",
   "Zentiva acquires Creo Pharma to accelerate growth; no specific R&D-asset motive disclosed. Commercial growth."),
 "CTL-0064": ("Alternative-rationale","High","OTC self-medication brands (Tonipharm)",
   "Recordati acquires Tonipharm to enhance its self-medication portfolio with established OTC brands. Commercial/brands."),
 "CTL-0096": ("Alternative-rationale","High","Generic marketing authorisations + German market entry (Juta Pharma)",
   "USV acquires Juta Pharma (50+ generic marketing authorisations) for German/European market growth. Generics/geographic."),
 "CTL-0198": ("Alternative-rationale","High","UK commercial presence for CNS products (DB Ashbourne)",
   "Ethypharm acquires DB Ashbourne to build a direct commercial presence in Europe for CNS products. Commercial/geographic."),
 "CTL-0207": ("Alternative-rationale","Medium","Licensed respiratory/allergy commercial products (Nigaard)",
   "Zambon acquires Nigaard to speed commercialisation of Xadago for Parkinson's. Commercial/licensed products."),
 "CTL-0279": ("Alternative-rationale","High","Aesthetic-dermatology commercial portfolio + US market (Neocutis)",
   "Merz acquires Neocutis to strengthen its aesthetic-dermatology market position and expand US business. Commercial/market."),
 "CTL-0298": ("Alternative-rationale","High","Dietary-supplement/generic portfolio + CEE market (Farma-Projekt)",
   "Recordati acquires Farma-Projekt to grow in CEE markets. Generics/geographic."),

 # --- Mixed / borderline (excluded from primary) ---
 "TRT-0024": ("Mixed / borderline","Medium","Drug-delivery/formulation technology + development capabilities AND scale/commercial (Skyepharma)",
   "Vectura/Skyepharma combine complementary inhaled formulation, development, regulatory and device capabilities to build a specialty commercial airways business. Strong innovation AND scale/commercial framing in a merger of comparable firms."),

 # --- Ineligible transactions ---
 "CTL-0151": ("Ineligible transaction","High","Childcare nursery services (out of sector)",
   "Busy Bees acquires Teddy Bear Club Nursery — childcare services, outside the pharmaceutical/biotech sector scope. Ineligible."),
 "CTL-0186": ("Ineligible transaction","High","8.31% minority stake (Camurus)",
   "Swedbank Robur acquires an 8.31% minority stake in Camurus. No control transfer. Ineligible."),
 "CTL-0107": ("Mixed / borderline","Medium","Oral-vaccine delivery platform via a reverse merger (Aviragen/Vaxart)",
   "Aviragen reverse-merges with Vaxart (one-for-eleven reverse split; Vaxart holders own ~60%). Innovation platform on evidence but reverse-merger entity continuity is ambiguous; excluded from strict primary."),
}

# map decisions to canonical events by membership
def classify(row):
    ids = set(row["member_deal_ids"].split(";"))
    for did, dec in DECISIONS.items():
        if did in ids:
            return pd.Series(dec, index=["Final_Classification","Classification_Confidence","Innovation_or_Commercial_Asset","Classification_Justification"])
    return pd.Series(["Insufficient evidence (not data-carrying)","Not assessed","","Not individually adjudicated: no usable financial or patent data to enter H1/H2 (master-prompt priority rule); classify only if promoted to the analytical sample."],
                     index=["Final_Classification","Classification_Confidence","Innovation_or_Commercial_Asset","Classification_Justification"])

canon = pd.concat([canon, canon.apply(classify, axis=1)], axis=1)

# ---- eligibility / control transfer ----
def eligibility(row):
    ct = row["ctrl_transfer"]; s3 = row["subtype3"]; klass = row["Final_Classification"]
    yr = row["completion_year"]
    if klass == "Ineligible transaction":
        return pd.Series(["Ineligible", "Sector-scope or minority (see classification)"], index=["Eligibility","Exclusion_Reason"])
    if not (2012 <= yr <= 2020):
        return pd.Series(["Ineligible", f"Completion year {yr} outside 2012-2020"], index=["Eligibility","Exclusion_Reason"])
    if "Exclude - minority" in ct:
        return pd.Series(["Ineligible", "Minority stake — no control transfer"], index=["Eligibility","Exclusion_Reason"])
    if "Eligible - 100%" in ct or "100% Acquisition" in s3:
        return pd.Series(["Strict (100%)", ""], index=["Eligibility","Exclusion_Reason"])
    if "Review - majority" in ct or "Majority Acquisition" in s3:
        return pd.Series(["Broader (majority control-transfer)", ""], index=["Eligibility","Exclusion_Reason"])
    if "Review - merger" in ct:
        return pd.Series(["Broader (merger, surviving entity)", ""], index=["Eligibility","Exclusion_Reason"])
    if "Review - reverse acquisition" in ct:
        return pd.Series(["Ineligible", "Reverse acquisition without entity continuity"], index=["Eligibility","Exclusion_Reason"])
    return pd.Series(["Review", "Control-transfer status unresolved"], index=["Eligibility","Exclusion_Reason"])

canon = pd.concat([canon, canon.apply(eligibility, axis=1)], axis=1)

# treatment indicator for the evidence-based model
canon["InnovationDeal"] = canon["Final_Classification"].isin(
    ["High-confidence innovation-driven","Medium-confidence innovation-driven"]).astype(int)
canon["is_primary_innovation"] = (canon["Final_Classification"] == "High-confidence innovation-driven").astype(int)
canon["is_alternative"] = (canon["Final_Classification"] == "Alternative-rationale").astype(int)

canon.to_csv(PROC / "deal_master_classified.csv", index=False)

# ---- checksum freeze ----
checksum = hashlib.sha256(open(PROC / "deal_master_classified.csv", "rb").read()).hexdigest()
open(PROC / "deal_master_classified.SHA256", "w").write(checksum + "\n")

# ---- review workbook + summary ----
review_cols = ["deal_event_id","member_deal_ids","source_workbooks","acquirer","target",
               "completion_date","completion_year","subtype2","subtype3","ctrl_transfer",
               "Final_Classification","Classification_Confidence","Innovation_or_Commercial_Asset",
               "Classification_Justification","Eligibility","Exclusion_Reason",
               "InnovationDeal","fin_status","pat_status"]
adjudicated = canon[canon["Final_Classification"] != "Insufficient evidence (not data-carrying)"]
with pd.ExcelWriter(AUDIT / "deal_classification_review.xlsx") as xw:
    adjudicated[review_cols].sort_values(["Final_Classification","completion_year"]).to_excel(xw, sheet_name="adjudicated", index=False)
    canon[review_cols].to_excel(xw, sheet_name="all_canonical_events", index=False)

# unresolved data-carrying: events with data but not cleanly in a primary cell
canon["has_any_data"] = ~((canon["fin_status"].str.contains("Not collected")) & (canon["pat_status"].str.contains("Not collected|Not imported|No event-window", regex=True)))
unresolved = canon[(canon["has_any_data"]) & (canon["Final_Classification"].isin(["Mixed / borderline","Insufficient evidence (not data-carrying)","Ineligible transaction"]))]
unresolved[review_cols + ["has_any_data"]].to_excel(AUDIT / "unresolved_data_carrying_deals.xlsx", index=False)

# ---- console + summary md ----
counts = canon["Final_Classification"].value_counts()
elig = canon["Eligibility"].value_counts()
adj_elig = adjudicated.groupby(["Final_Classification","Eligibility"]).size()
summary = f"""# Classification summary

Classification freeze checksum (SHA-256 of deal_master_classified.csv):
`{checksum}`

## Method and evidence constraint
Classification uses **pre-completion evidence only** — the GlobalData deal
descriptions and rationales imported into the workbooks, which embed
contemporaneous announcement text (evidence-hierarchy levels 1-2) plus the
GlobalData rationale (level 5). **No network access** was available, so no
external company announcements or filings could be archived. Per the master
prompt, only the **data-carrying** deals (those with usable financial or patent
data, able to enter H1/H2) were individually adjudicated; all other deals are
'Insufficient evidence (not data-carrying)'.

Classification is by **evidence, not source workbook**. The GlobalData
innovation/alternative extracts are first-stage screens only. The adjudication
identified **screen false positives** (commercial deals in the treatment
extract: Nicox/Doliage, Eurofins/AROS, Esteve/Riemser, Cardiome/Correvio) and
**screen false negatives** (clear R&D/pipeline deals in the comparison extract:
Roche/Trophos, Roche/Tusk, Ipsen/Syntaxin, GSK/GlycoVaxyn, Roche/Signature,
UCB/Handl, Vectura/Activaero). Both directions are reassigned on evidence.

## Final classification counts (canonical events)
{counts.to_string()}

## Eligibility (canonical events)
{elig.to_string()}

## Adjudicated deals: classification x eligibility
{adj_elig.to_string()}
"""
open(AUDIT / "classification_summary.md", "w").write(summary)
print(summary)
print("\nunique canonical events:", len(canon))
print("data-carrying adjudicated:", len(adjudicated))
