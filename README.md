# SHB Argument Atlas — Public Court Research POC v0.1

**Prototype only · Public case data · No AI model calls · No firm integrations**

**Docs:** [Overview](docs/OVERVIEW.md) (what it is, why, roadmap) · [Architecture](docs/ARCHITECTURE.md) (components, data flow, security, testing)

## What works

- Search 10 curated **expert challenges** from **four real public federal court orders**, in Missouri.
- Filter by federal district and outcome.
- Compare 2–4 expert challenges side by side, including challenges, court reasoning, and limitations.
- Open the publicly hosted court-order PDF on a cited page.
- Export a marked **DRAFT** Word comparison and CSV.
- Optionally download PDFs from an allowlisted public source and check whether an anchor phrase appears on the cited PDF page (not proof of the analysis).

## Critical provenance limitation

The seed dataset includes **orders**, not party-filed motions, opposition briefs, or exhibits. **Arguments are summarized as described by the courts in the orders.** The motion docket numbers are included only to facilitate future sourcing. This is *not* a full motion/opposition/order corpus. One identified motion (Deflecto Doc. 130) was sealed. No case is SHB work product; no attorney involvement should be inferred.

The seed summaries were manually assembled from specific publicly available orders, not automatically extracted by an AI model. There is no live AI analysis or generation in this version. All entries require attorney validation. Search uses SQLite FTS5, **not semantic search**.

## Run on your machine

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit should show a localhost URL (usually `http://localhost:8501`).

**No installs yet?** With Python alone you can test the offline search logic:

```bash
python cli_demo.py "differential diagnosis"
```

To test:

```bash
python -m pytest tests -q
```

## Public source documents

| Case | Public court order PDF | Docket / order document | Relevant issues |
|---|---|---|---|
| Kyles v. Celadon Trucking Services | https://cases.justia.com/federal/district-courts/missouri/mowdce/6:2015cv03193/121720/270/0.pdf | 6:15-cv-03193, Doc. 270 | Bain, Sievers, Knox, Gaines |
| Scott v. Dyno Nobel | https://cases.justia.com/federal/district-courts/missouri/moedce/4:2016cv01440/148802/231/0.pdf | 4:16-cv-01440, Doc. 231 | Morningstar, Sevin, Norsworthy |
| Deflecto v. Dundas Jafine | https://cases.justia.com/federal/district-courts/missouri/mowdce/4:2013cv00116/107837/176/0.pdf | 4:13-cv-00116, Doc. 176 | Vianello |
| Breuil v. White | https://cases.justia.com/federal/district-courts/missouri/mowdce/3:2023cv05048/170753/138/0.pdf | 3:23-cv-05048, Doc. 138 | Liggett, Bourdage |

The actual PDFs are **not bundled**, and online access is optional for searching the seed records. Browser links to public orders do require internet.

## Show this to the team

1. Search `differential diagnosis`.
2. Compare `Carla Sevin` (denied) and `Eric Norsworthy` (granted), **within the same case**.
3. Point out that the two medical causation opinions received different treatment and show the public opinion pages.
4. Search `accident severity` to show boundaries on expert testimony across matters.
5. Export a draft Word comparison and open the source PDFs.

**Demo question:** Would structured records connecting each legal challenge, response, rationale, and ruling save attorneys time over searching raw filings alone?

## Next version, if approved

1. Obtain public **motion, opposition, and order** triplets (CourtListener RECAP and public docket repositories). Confirm document relationships, accessibility, and reuse terms. Avoid sealed records.
2. Add extraction of PDF pages and citation-aligned text with PyMuPDF / Document Intelligence where needed.
3. Add typed AI extraction with SHB-approved Azure Foundry / Claude Sonnet endpoint; preserve attribution to source type and page, and use an attorney-review queue before writing to the knowledge index.
4. Benchmark issue search quality and extraction correctness on a lawyer-approved test set.
5. Only after access/governance approval explore integrating permission-scoped firm knowledge; SHB's current per-matter ethical walls must not be weakened.

## Security and accuracy notes

- Public seed cases only. Don't load private matters into this local demo without IT approval.
- Optional download code restricts network fetches to `cases.justia.com` and `www.govinfo.gov`, with file-size caps.
- PDF anchor checks confirm literal text presence only, **not legal validity or claim correctness**.
- Case outcomes are *motions about particular expert opinions*; they are not final case outcomes or measures of legal strategy success.
- The orders were decided under the law applicable at their dates. This tool does not check subsequent history, current law, or whether the authority remains good law.
- Local Streamlit has **no user authentication**. For a firm deployment use Entra, proper authorization, secure storage, logging, and governance review.
