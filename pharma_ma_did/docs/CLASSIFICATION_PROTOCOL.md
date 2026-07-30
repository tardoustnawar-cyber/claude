# Classification protocol (provisional)

**Inputs available:** GlobalData `Initial_Group` (candidate screen only, per the workbook
README), deal Description and Deal_Rationale free text. No target patent portfolios,
pipeline tables, or manual assessments were present (all evidence columns were
placeholders; `Final_Classification`='Not reviewed' for every deal).

**Procedure**
1. Base axis = candidate screen (innovation-driven export vs alternative export).
2. Score announcement text: innovation keywords (pipeline, R&D, discovery, antibody,
   platform, clinical, candidate, compound, novel, biotech, gene, vaccine, oncology,
   proprietary, technology, phase I–III) vs alternative keywords (distribution,
   geographic, market access, commercial, generic, consolidation, manufacturing,
   capacity, footprint, CRO, cost, supply).
3. Screen + text agree → Medium confidence in that class. Screen with weak/absent text →
   Low confidence, class = screen. Screen and text conflict → **Borderline/mixed motive**
   (excluded from strict sample).
4. Three cross-file overlaps resolved manually from target descriptions
   (Okairos→innovation, Premacure→innovation, Riemser→alternative).

**Every deal is flagged `Requires_Human_Review = YES`.** The estimand is therefore
"deals classified innovation-driven under this observable protocol", not the effect of a
true managerial motive. Review table: `outputs/audit/deal_classification_review.xlsx`.
Frozen file SHA-256 recorded in `data/processed/master_transactions_classified.csv.sha256`.
