# Quality-Assurance Report — Academic Humanisation

**Revised document:** `Nawar_TARDOUST_Academically_Humanised.docx`
**Original (unchanged):** `Thesis_TARGET.docx` / backup `Thesis_ORIGINAL_BACKUP.docx`

| Check | Result |
|---|---|
| Document reopened successfully | ✅ opens; OOXML schema validation passes with **0 new errors** |
| Paragraph count (before → after) | 478 → **478** (unchanged) |
| Table count | 17 → **17** |
| Figure/image count (embedded) | 11 → **11** |
| Reference entries | 34 → **34** |
| Headings preserved | ✅ all heading and bold-heading paragraphs unchanged |
| Equations preserved | ✅ Equations (3.1) and (3.2) and their definitions unchanged |
| Numbers in **unedited** paragraphs | ✅ identical multiset (automated diff) |
| Numbers/statistics in edited paragraphs | ✅ preserved verbatim (3 documented non-substantive exceptions) |
| Coefficients / CIs / p-values | ✅ unchanged (Chapters 4–6 untouched; methodology values verbatim) |
| Citations preserved | ✅ document-wide year-token multiset unchanged; no citation moved from its claim |
| No unsupported source introduced | ✅ none added; one pre-existing unsupported trio **flagged** at P68 |
| No long text copied from external papers | ✅ all revised prose written originally; no external corpus ingested |
| No original paragraph deleted | ✅ paragraph count constant; only text within 73 prose paragraphs revised |
| Markdown symbols in prose | ✅ none introduced |
| Original file overwritten? | ❌ No — MD5 identical to backup |

## Documented non-substantive numeric exceptions
1. **P125** — removed the erroneous digit in the typo `biotech0industry` → “biotechnology industry”.
2. **P88** — removed an orphan footnote-marker digit “7” sitting between two sentences.
3. **P75 / P113** — spelled out two small counts for style (“3-year” → “three-year”; “2 types” → “two types”).

None of these alters a coefficient, confidence interval, p-value, sample size, date, or year.

## Scope of revision
- **Deeply revised:** Introduction and literature review (paras 24–113) and ~20 rough
  paragraphs of the methodology (Chapter 3) — 73 paragraphs in total.
- **Left unchanged (already at target quality):** Chapters 4–6 (results, discussion,
  conclusion), all tables, captions, notes, the reference list, and all front matter.
  Their statistics are therefore preserved trivially.

## Flag requiring author action
**P68:** the in-text citations *Aghion et al. (2009); Azoulay and Crémieux (2006);
Blanes-Vidal and Ciocco (2012)* do not appear in the reference list. They were retained
and marked `[SOURCE OR AUTHOR VERIFICATION REQUIRED …]`. The author should either add
these works to the reference list or delete the citations.

## Deliverables
- `Nawar_TARDOUST_Academically_Humanised.docx` — revised thesis (primary deliverable).
- `Nawar_TARDOUST_Academic_Editing_Report.md` — detailed editing report.
- `Nawar_TARDOUST_Academic_Style_Profile.md` — style profile.
- `Nawar_TARDOUST_Revision_Log.xlsx` — 73-row before/after log with level, problem,
  rationale, meaning-preserved, and verification columns.
- `Nawar_TARDOUST_QA_Report.md` — this report.

## PDF preview
Not produced: LibreOffice in this environment cannot load the document for PDF conversion
(the same limitation affects the original), and the brief marks the PDF as optional. The
DOCX is the primary deliverable and validates successfully.
