# Live accuracy audit: illinois-benefit-access-program

- Date: 2026-11-25
- Auditor: ESCG worker, session cse_014eaiSarrUfj6PScmQNGxys (task ACQ-072, key audit:illinois-benefit-access-program)
- Page audited: main 4dc2468 (reviewed 2026-11-17)
- Quotation checker on main: 11 quotations, 11 FOUND; 2 short terms found; 3 cited pages, 0 unreadable.

## Sources (read 2026-11-25)

1. IDoA Benefit Access Program (benefitsaccess.html): "License Plate Discount Qualifications", "Income Requirements", "Important Notes".
2. IDoA Benefit Access, Eligibility and Frequently Asked Questions.
3. IDoA Benefit Access, Ride Free Transit Benefit.

## Scope table

| # | Guide's claim | Guide's scope | Source's scope (heading / context) | Result |
|---|---|---|---|---|
| 1 | Answer: "To qualify, a person must be 65 or older before January 1 … (or turning 65 this year), live in Illinois, and have had gross household income below…" | every applicant | Src 1 "Age Requirements": 65 before Jan 1; or become 65 this year; "or You must be 16 years of age or older before January 1 of the current year and qualify as disabled" | SCOPE DEFECT (person): the answer drops the disability route it mentions a sentence earlier. Corrected (C1). |
| 2 | Body: age rule and the alternative 16+ totally and permanently disabled route; FAQ "by December 31 of the current year" | applicants | Src 1, Src 2 | same |
| 3 | Proof of disability (SSA, VA, Civil Service, Railroad Retirement; Class 2 card; Attachment A) | disability route | Src 2 "Who qualifies as disabled?" | same |
| 4 | Income limits $33,562 / $44,533 / $55,500 by household of 1/2/3, last closed tax year; "income limit increase effective 1/1/2020" | Illinois applicants | Src 1 "Income Requirements"; Src 2; Src 3 | same |
| 5 | Spouse income counts if married and living together on Dec 31; QAR income excluded; QAR definition | households | Src 1, Src 2 | same |
| 6 | Not a citizen: eligible with a Social Security number | non-citizens | Src 2 | same |
| 7 | Online only, "Paper applications are not available"; joint application; separate if a nursing home or legally separated | applicants | Src 1, Src 2 | same |
| 8 | Status after 48 hours; up to 8 weeks; plate discount 10 business days after approval; Ride Free "the following day you are approved" | approved applicants | Src 1 "Important Notes"; Src 3 | same, each timeline tied to its benefit |
| 9 | Eligibility good for two years; reapply from 90 days before expiry; "every other year" | approved applicants | Src 2 "Expiration"; Src 3 | same |
| 10 | Senior HelpLine 1-800-252-8966 (711 TRS) | all | IDoA pages | same |
| 11 | No dollar value for the plate discount; no description of paratransit interaction | n/a | Srcs 1–3 | holds |

## Corrections

C1. Answer. Was: "To qualify, a person must be 65 or older before January 1 of the current year (or turning 65 this year), live in Illinois, and have had gross household income below a published limit…". Now: "… (or turning 65 this year) or be at least 16 and totally and permanently disabled before January 1, live in Illinois, and have had gross household income below a published limit…". Source (Src 1, Age Requirements): "65 years of age or older before January 1 of the current year; You must become 65 years of age this year; or You must be 16 years of age or older before January 1 of the current year and qualify as disabled." Src 1, Disability Requirements: "be determined totally and permanently disabled (as defined by program requirements) prior to January 1 of the current year."

Applied: branch claude/accuracy-20261125 commit ad00940, rolling review pull request #89 (not merged). Reviewed date updated to 2026-11-25.

Quotations checked: 11. Claims scope-checked: 11. Scope defects: 1. Corrections required: 1.

Verdict: corrections listed above (eligibility route missing from the short answer)

Corrections verified: 2026-11-25, main chat for Joseph (second reader): commit ad00940 read; the Department's page reads 'To qualify as disabled, you must be at least 16 years of age prior to January 1 of the current year and be determined totally and permanently disabled (as defined by program requirements) prior to January 1 of the current year'; quotecheck 11/11 found. Library date kept by 50fa120 ("listed": 2026-11-17).
