# Classification summary

Classification freeze checksum (SHA-256 of deal_master_classified.csv):
`e5dc6541e7e5e7166a397b506b159d596299e177221ab47da0969c5b611c6d8f`

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
Final_Classification
Insufficient evidence (not data-carrying)    277
High-confidence innovation-driven             13
Alternative-rationale                         12
Ineligible transaction                         2
Mixed / borderline                             2

## Eligibility (canonical events)
Eligibility
Strict (100%)                          170
Broader (majority control-transfer)     67
Ineligible                              42
Broader (merger, surviving entity)      27

## Adjudicated deals: classification x eligibility
Final_Classification               Eligibility                        
Alternative-rationale              Broader (majority control-transfer)    3
                                   Strict (100%)                          9
High-confidence innovation-driven  Broader (majority control-transfer)    7
                                   Strict (100%)                          6
Ineligible transaction             Ineligible                             2
Mixed / borderline                 Broader (merger, surviving entity)     1
                                   Strict (100%)                          1
