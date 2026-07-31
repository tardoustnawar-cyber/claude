# Quality-Control Report — Chapters 5 and 6

**Deliverable:** `Nawar_TARDOUST_Complete_Thesis_Chapters_1_to_6.docx`
**Source (unchanged):** `VF_CH_1_3_4_ORIGINAL.docx` (a byte-identical copy of the uploaded `VF CH 1 3 4.docx`)
**Backup:** `VF_CH_1_3_4_BACKUP.docx` (MD5 identical to the original)

---

## 1. Insertion location
Chapters 5 and 6 were inserted **immediately after the end of Chapter 4** (which ends with section “4.11 Limitations of the empirical analysis”) and **immediately before the thesis-wide References heading**.

The document that was supplied already contained a short placeholder headed **“Chapter 5 — Discussion (opening bridge)”** consisting of three mini-sections (5.1 From estimates to interpretation; 5.2 Consistency with the mechanisms in the literature; 5.3 From associational to confirmatory evidence). This 8-paragraph stub was **replaced** by the full Chapter 5, so that the finished thesis does not contain two competing versions of Chapter 5. No other existing content was removed.

Verified body order in the output: **Chapter 4 — Empirical Results → Chapter 5 — Discussion → Chapter 6 — Conclusion → References.**

## 2. Word counts (body text only, excluding headings)
| Chapter | Words | Target | Status |
|---|---|---|---|
| Chapter 5 — Discussion | **4,003** | 3,500–4,500 | Within range |
| Chapter 6 — Conclusion | **1,155** | 1,000–1,500 | Within range |

Per-section counts (Chapter 5): 5.1 ≈ 356; 5.2 ≈ 622; 5.3 ≈ 601; 5.4 ≈ 596; 5.5 ≈ 581; 5.6 ≈ 346; 5.7 ≈ 380; 5.8 ≈ 521. Chapter 6: 6.1 ≈ 262; 6.2 ≈ 275; 6.3 ≈ 125; 6.4 ≈ 138; 6.5 ≈ 355 plus a closing paragraph. All sections are within, or reasonably close to, their recommended ranges.

## 3. Verified empirical values (source of truth: Chapter 4 of the Word document)
All values used in Chapters 5–6 were taken from Chapter 4 and match it exactly. The prompt’s expected headline values were checked against the document and agreed in every case.

**H1 — patent-family output**
- Estimated differential: **β = −0.46 patent families**
- 95% confidence interval: **[−4.52, 3.61]**
- Wild-bootstrap p-value: **0.82** (cluster-robust p = 0.83)
- Joint pre-trend test p-value: **0.96**
- Sample: **13 events, 13 acquirer clusters**
- Robustness: IHS β = 0.11 (p = 0.85); PPML β = 0.05 (p = 0.93)
- Decision: **not supported; imprecise null (not equivalence)**

**H2 — return on assets**
- Estimated differential: **β = +10.78 percentage points** (decomposition: +2.76 pp alternative, +13.53 pp innovation)
- 95% confidence interval: **[−13.69, 35.24]**
- Wild-bootstrap p-value: **0.40** (cluster-robust p = 0.39)
- Joint pre-trend test p-value: **0.57**
- Sample: **12 events, 12 acquirer clusters**
- Excluding **Biodexa → +0.43 pp**; excluding Roche → +14.33 pp; serial-acquirer specification → +6.43 pp
- Decision: **directionally consistent but not statistically supported and highly sensitive to influential firms**

No discrepancies were found between the prompt’s expected values and the Word document. No value was invented.

## 4. Citations used in Chapter 5 (all verified present in the thesis reference list)
Ahuja and Katila (2001); Arrow (1962); Barney (1991); Büssgen and Stargardt (2024); Cloodt et al. (2006); Cohen and Levinthal (1990); Cunningham et al. (2021); DiMasi et al. (2016); Gilbert and Newbery (1982); Grant (1996); Hall, Jaffe and Trajtenberg (2001); Haucap, Rasch and Stiebale (2019); Higgins and Rodriguez (2006); Jensen (1986); Nelson and Winter (1982); Ornaghi (2009); Teece (1986); Valentini (2012).

- **No new sources were introduced.** Every surname and year above was confirmed to exist in the document’s existing reference list.
- **Chapter 6 contains no citations**, consistent with the instruction that the conclusion should not introduce literature.
- No second reference list was created; the thesis-wide reference list is preserved unchanged.

## 5. Preservation checks (original → output)
| Item | Original | Output | Status |
|---|---|---|---|
| Original file MD5 | 92ecade4… | unchanged | Not modified |
| Tables | 17 | 17 | Preserved |
| Embedded images (drawing references) | 11 | 11 | Preserved |
| Reference-list entries | 34 | 34 | Preserved |
| Chapters 1–4 headings (spot-checked) | present | present | Preserved |
| Paragraph count | 424 | 478 | +62 new − 8 stub removed |

Spot-checked headings confirmed present in the output: “1. Theoretical foundations and mechanisms”, “3.14 Baseline Difference-in-Differences specification”, “Chapter 4 — Empirical Results”, “4.6 H1 — Differential patent output”, “4.7 H2 — Differential financial performance (ROA)”.

## 6. Formatting checks
- **Chapter titles** (“Chapter 5 — Discussion”, “Chapter 6 — Conclusion”): bold, 16 pt, Times New Roman, with a **page break before** each — identical to the “Chapter 4 — Empirical Results” title.
- **Section headings** (5.1–5.8, 6.1–6.5): bold, 14 pt, Times New Roman — identical to Chapter 4 section headings (e.g. 4.6, 4.7).
- **Body text:** 47/47 inserted body paragraphs are justified and set in Times New Roman (12 pt), matching Chapter 4.
- **No Markdown symbols** (`#`, `**`, backticks, horizontal rules, `](`) appear in the inserted chapters.
- **No empty headings, no duplicated paragraphs, no broken characters** in the inserted region (en/em dashes and the “≈”, “β”, “δ”, “–” glyphs render as intended).
- Document passes **Office Open XML schema validation** (`validate.py`): no new validation errors versus the original.

## 7. Interpretation-safety checks
- H2 is **never** described as “confirmed” or “partially confirmed”; it is described as directionally consistent but statistically unsupported and fragile.
- Statistical insignificance is **not** equated with equivalence; both results are explicitly framed as imprecise/associational, and “neither result demonstrates equivalence” is stated.
- The forbidden term “proves” does not occur as a standalone word (the only match was the substring inside “improves”); “control group” is not used in a sense implying non-acquiring firms; no causal-proof language is used.
- The estimand is restated as a **differential between two completed-acquisition types**, not acquisition versus non-acquisition.
- Chapter 5 is analytical (interpretation, comparison, theory, alternatives, limitations); Chapter 6 is concise (answer, contributions, brief managerial note, brief limitations, future research, closing paragraph).

## 8. Table of contents
- The existing TOC field and its structured-document-tag wrapper are preserved unchanged.
- `w:updateFields` was set to **true** in `word/settings.xml` (in schema-valid position), so Word will offer to refresh the TOC and all fields when the document is opened.
- **Heading-style note / one deliberate trade-off:** In the source document, Chapter 4’s headings use **direct bold formatting** (bold Times New Roman 16/14/12 pt) rather than Word’s built-in Heading styles, and Chapter 4 is therefore **not represented in the field-based table of contents**. To keep Chapters 5–6 visually and structurally identical to the adjacent Chapter 4 (a repeatedly stated requirement), the new headings replicate that same direct-bold formatting. A consequence is that, like Chapter 4, Chapters 5–6 will not auto-populate the field TOC unless the results-and-discussion block is converted to heading styles. This was chosen deliberately so as not to reformat the protected Chapters 1–4 and to avoid a TOC that lists Chapters 5–6 while omitting Chapter 4. If preferred, the same heading-style (or invisible outline-level) treatment can be applied uniformly to Chapters 4–6 on request so that all three appear in the TOC.

## 9. PDF preview
A PDF preview was **not** produced: LibreOffice in this environment fails to load the DOCX for conversion, and the **same failure occurs on the original file**, confirming an environment limitation rather than a defect in the output. The prompt marks the PDF as optional (“only if reliable conversion is available”). The DOCX remains the primary deliverable and opens and validates correctly.

## 10. Unresolved discrepancies
- **None affecting content.** All expected empirical values matched the Word document; all citations were found in the reference list; the original file is unchanged.
- One environment limitation (PDF conversion unavailable) is noted above; it does not affect the DOCX deliverable.
- One deliberate, documented editorial decision: the “opening bridge” Chapter 5 stub was replaced by the full Chapter 5 (Section 1 above).
