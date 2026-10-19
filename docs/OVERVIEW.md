# Argument Atlas: Overview

Argument Atlas is a working proof of concept (POC) that turns court rulings on expert-witness challenges into structured, searchable, side-by-side records. It holds 10 hand-curated Rule 702 / Daubert rulings from 4 public Missouri federal court orders. It runs on a laptop with no AI calls and no firm data.

**The question it answers:** would structured records linking each challenge, response, court reasoning and ruling save attorneys time compared with searching raw filings?

**Status:** ready to demo. Scaling it up depends on the decisions in [Decisions needed](#decisions-needed).

For the technical design, see [ARCHITECTURE.md](ARCHITECTURE.md).

## What it does today

The app has three views, all working end to end.

| View | What an attorney can do |
| --- | --- |
| Research | Search by issue, expert or doctrine. Filter by court and ruling outcome. See the outcome breakdown of the results. Open each ruling's argument → opposition → court's reasoning. Jump to the cited page of the public order. |
| Compare | Put 2–4 rulings side by side in an aligned table. Export a marked DRAFT Word comparison or a CSV. |
| Sources & scope | See the 4 source orders and what the POC does and does not cover. Optionally check that a cited phrase appears on the cited PDF page. |

### Five-minute demo

1. Search `differential diagnosis`.
2. Compare Carla Sevin (motion denied) with Eric Norsworthy (motion granted). Both are from the same case.
3. Point out that two medical-causation opinions were treated differently, and open the public order pages that say why.
4. Search `accident severity` to show limits on expert testimony across cases.
5. Export the DRAFT Word comparison and open the source PDFs.

## Data and provenance

Every record is a manual summary of one expert challenge. Each one comes from a public court **order** and is tied to the exact PDF page it came from. The arguments are the court's description of each side, not quotations from the parties' briefs.

| Case | Court, year | Order | Experts covered | Rulings on motions to exclude |
| --- | --- | --- | --- | --- |
| Kyles v. Celadon Trucking Services | W.D. Missouri, 2017 | Doc. 270 | Bain, Sievers, Knox, Gaines | 2 denied, 1 granted, 1 granted in part |
| Scott v. Dyno Nobel | E.D. Missouri, 2021 | Doc. 231 | Morningstar, Sevin, Norsworthy | 1 denied, 1 granted, 1 granted in part |
| Deflecto v. Dundas Jafine | W.D. Missouri, 2015 | Doc. 176 | Vianello | 1 granted in part |
| Breuil v. White | W.D. Missouri, 2025 | Doc. 138 | Liggett, Bourdage | 2 denied |

**How to read an outcome:** each ruling is on a motion to *exclude* an expert's testimony.

- **Denied:** the testimony was not excluded on the grounds raised.
- **Granted:** it was excluded.
- **Granted in part:** some of it was excluded or limited.

**Not included:**

- The party-filed motions, oppositions and exhibits. One motion, Deflecto Doc. 130, is sealed.
- Any firm work product.
- Any AI-generated content.

The 10 rulings are a demo set, not a statistical sample.

## Key design decisions

Each choice keeps the POC cheap, safe to show, and honest about what it proves.

| Decision | Why | Trade-off |
| --- | --- | --- |
| No AI in this version | It tests the value of structured records before paying for extraction, and there is nothing to approve with IT or vendors. | Records are built by hand, so the set stays small. |
| Keyword search (SQLite FTS5) | It is built into Python, ranks by relevance, and needs no server. | It matches words, not meaning. |
| Streamlit for the interface | One Python codebase covers logic and UI, so the app is a few hundred lines. | It gives less layout control than a web framework. Fine for a demo, not a product. |
| Runs locally | It needs no hosting, accounts or firm systems. | It is not shared or multi-user yet. |
| Exports marked DRAFT | It makes clear that every output needs attorney review. | None; this is deliberate. |
| Public court orders only | There is no confidentiality risk, and anyone can check the source. | Orders summarize the briefs rather than include them. |

## Safeguards and limitations

**Safeguards**

- **Every claim links to its source.** Each claim points to a public order and PDF page.
- **The UI states its limits.** The interface says plainly that arguments are the court's characterization, not quotations.
- **Exports are marked.** Word exports carry a "DRAFT · not legal advice · requires attorney verification" banner.
- **PDF downloads are tightly restricted.** They are optional and limited to two public hosts (cases.justia.com, govinfo.gov), with a 20 MB size cap. They never follow redirects to other sites.
- **Text is displayed as plain text.** All record text and search input are escaped before display, so typed or stored text cannot inject code into the page.

**Limitations**

- **Small dataset.** It has only 10 rulings and 4 orders, all from Missouri federal courts.
- **Keyword search only.** It does not understand synonyms or meaning.
- **No citator.** It does not check later history or whether the law has changed.
- **Spot-check is narrow.** The PDF spot-check confirms a phrase is on the cited page. It does not confirm the legal summary is right.
- **Not production-ready.** It has no user accounts, hosting or firm-system integration.

## Roadmap if approved

1. **Fuller source sets.** Gather public motion, opposition and order sets from CourtListener RECAP and other public docket sources. Confirm reuse terms and avoid sealed records.
2. **Page-accurate text extraction.** Extract PDF text tied to page citations, using PyMuPDF or Azure Document Intelligence.
3. **AI-assisted extraction with attorney review.** Use an approved Azure Foundry / Claude endpoint to draft records, and keep the source and page for every field. Nothing enters the index until an attorney approves it.
4. **Measure quality.** Benchmark search and extraction accuracy against an attorney-approved test set.

## Decisions needed

- Is the time saved in the demo enough to fund step 1, building a larger, sourced dataset?
- Which practice group and jurisdictions should the next dataset cover?
- Which approved AI endpoint and review process should extraction use?
- Should the next version be hosted for a pilot group, or stay a local demo?
