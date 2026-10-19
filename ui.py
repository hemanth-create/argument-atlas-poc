"""Presentation helpers: design tokens, CSS, and escaped HTML fragments."""
from __future__ import annotations

import re
from datetime import date
from html import escape
from urllib.parse import quote

from core import source_link, tokenize_query

OUTCOMES = {
    "Denied": ("denied", "check", "Motion to exclude denied: the challenged testimony was not excluded on the "
               "grounds raised. The court may still limit its scope."),
    "Granted in part": ("partial", "half", "Motion to exclude granted in part: some challenged testimony was "
                        "excluded or limited."),
    "Granted": ("granted", "x", "Motion to exclude granted: the challenged opinion(s) were excluded."),
}

_PATHS = {
    "check": '<circle cx="12" cy="12" r="10"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "x": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "half": '<circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 0 20z" fill="currentColor"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>'
             '<path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "search-x": '<path d="m13.5 8.5-5 5"/><path d="m8.5 8.5 5 5"/><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "landmark": '<path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/><path d="M14 18v-7"/><path d="M18 18v-7"/>'
                '<path d="M12 2 20 7H4z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/>'
             '<path d="M12 17h.01"/>',
}


def _mask(name: str) -> str:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" '
           f'stroke-linecap="round" stroke-linejoin="round">{_PATHS[name].replace("currentColor", "#000")}</svg>')
    url = f'url("data:image/svg+xml,{quote(svg)}")'
    return f".aa-i-{name}{{-webkit-mask:{url} center/contain no-repeat;mask:{url} center/contain no-repeat}}"


def icon(name: str, size: int = 16) -> str:
    # st.html sanitizes inline <svg>, so icons are CSS masks tinted with currentColor.
    return f'<span class="aa-ico aa-i-{name}" style="width:{size}px;height:{size}px" aria-hidden="true"></span>'


def safe_url(url: str) -> str:
    return escape(url) if str(url).startswith("https://") else ""


def long_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d:%b} {d.day}, {d.year}"


def highlight(text: str, query: str) -> str:
    """Escape every fragment, then wrap whole-word query matches in <mark>."""
    terms = tokenize_query(query or "")
    if not terms:
        return escape(str(text))
    word = "(?:" + "|".join(map(re.escape, terms)) + ")"
    parts = re.split(rf"\b({word}(?:\s+{word})*)\b", str(text), flags=re.I)
    return "".join(f"<mark>{escape(p)}</mark>" if i % 2 else escape(p) for i, p in enumerate(parts))


def badge(outcome: str) -> str:
    cls, glyph, tip = OUTCOMES.get(outcome, ("partial", "info", outcome))
    return f'<span class="aa-badge aa-{cls}" title="{escape(tip)}">{icon(glyph, 14)}{escape(outcome)}</span>'


def source_anchor(r: dict, label: str | None = None) -> str:
    url = safe_url(source_link(r))
    text = escape(label or f"Open order, p. {int(r['source_page'])}")
    if not url:
        return f'<span class="aa-muted">{text} (link unavailable)</span>'
    return (f'<a class="aa-src" href="{url}" target="_blank" rel="noopener noreferrer">{text}'
            f'{icon("external", 14)}<span class="aa-sr"> (opens in new tab)</span></a>')


def masthead() -> str:
    pills = "".join(f"<li>{t}</li>" for t in ("Proof of concept", "No AI calls", "Public data"))
    return f"""<header class="aa-mast">
<div class="aa-brand"><span class="aa-mark">{icon("scale", 26)}</span>
<div><p class="aa-eyebrow">Rule 702 &middot; Daubert &middot; Public court orders</p>
<p class="aa-word" role="heading" aria-level="1">Argument Atlas</p>
<p class="aa-tag">Expert-challenge rulings from Missouri federal court orders, structured as argument,
opposition, and the court&rsquo;s reasoning.</p></div></div>
<ul class="aa-status" aria-label="Status">{pills}</ul></header>"""


def boundary() -> str:
    return f"""<aside class="aa-callout" aria-label="Evidence boundary">{icon("info", 20)}
<p><strong>Evidence boundary.</strong> Each record is manually curated from a public court <em>order</em>.
Arguments are the court&rsquo;s characterization, not quotations from the parties&rsquo; briefs, which are not
yet in this dataset.</p></aside>"""


PROVENANCE = """
- **Source type.** Ten records, manually curated from four public federal court orders (E.D. and W.D. Missouri).
  The party-filed motions, oppositions, and exhibits are **not** in the dataset; motion docket numbers are listed
  only to support future sourcing. One motion (Deflecto, Doc. 130) is sealed.
- **Characterization, not quotation.** "Argument" and "Opposition" summarize how the *court* described each side.
  An order may describe only part of what the parties argued.
- **No AI.** Summaries were assembled by hand, not extracted or generated by a model. No LLM calls are made.
- **Keyword search.** Search uses SQLite FTS5 keyword matching, **not semantic search**.
- **Not comprehensive.** This is a small proof-of-concept set, not a legal research database or a statistical sample.
- **What outcomes mean.** Each outcome is the ruling on a motion to exclude particular expert testimony, not a
  case outcome. *Denied*: the challenged testimony was not excluded on the grounds raised (the court may still
  limit it). *Granted in part*: some testimony was excluded or limited. *Granted*: the challenged opinion(s)
  were excluded.
- **No citator.** Orders reflect the law at their dates. Subsequent history and current law are not checked.
- **Prototype only.** Every entry requires attorney validation. Not filing-ready legal research.
"""


def overview(total: int, cases: int, hits: list[dict]) -> str:
    counts = {o: sum(r["outcome"] == o for r in hits) for o in OUTCOMES}
    n = len(hits) or 1
    bar = "".join(f'<span class="aa-seg aa-{OUTCOMES[o][0]}" style="flex-grow:{c}" title="{escape(o)}: {c}"></span>'
                  for o, c in counts.items() if c)
    legend = "".join(f'<li>{badge(o)}<span class="aa-count">{c}</span><span class="aa-pct">{round(100 * c / n)}%</span></li>'
                     for o, c in counts.items())
    kpis = "".join(f'<div class="aa-kpi"><span class="aa-kpi-n">{v}</span><span class="aa-kpi-l">{k}</span></div>'
                   for k, v in (("Curated rulings", total), ("Cases", cases), ("Matching", len(hits))))
    track = f'<div class="aa-bar" aria-hidden="true">{bar}</div>' if hits else '<div class="aa-bar aa-empty"></div>'
    return f"""<section class="aa-overview" aria-label="Overview">{kpis}
<div class="aa-dist"><p class="aa-label">Motion-to-exclude outcomes in current results</p>{track}
<ul class="aa-legend">{legend}</ul></div></section>"""


def results_head(count: int, query: str) -> str:
    if query.strip():
        return (f'<div class="aa-rhead"><h2>{count} {"ruling" if count == 1 else "rulings"} match '
                f'&ldquo;{escape(query.strip())}&rdquo;</h2><p>Ranked by keyword relevance (SQLite FTS5, not semantic)</p></div>')
    return f'<div class="aa-rhead"><h2>{count} curated {"ruling" if count == 1 else "rulings"}</h2><p>Newest first</p></div>'


def card(r: dict, query: str) -> str:
    h = lambda k: highlight(r[k], query)
    topics = "".join(f'<li>{highlight(t, query)}</li>' for t in r.get("topics", []))
    meta = " &middot; ".join(escape(x) for x in (
        r["docket"], f"Order Doc. {r['order_document']}", f"Motion Doc. {r['motion_document']}", f"PDF p. {r['source_page']}"))
    return f"""<article class="aa-card">
<div class="aa-top"><span class="aa-kicker">Motion to exclude</span>{badge(r["outcome"])}
<span class="aa-court">{icon("landmark", 14)}{escape(r["court"])} &middot; {escape(long_date(r["date"]))}</span></div>
<h3 class="aa-case">{h("case_name")}</h3>
<p class="aa-who">{icon("user", 15)}<span><b>{h("expert")}</b></span><span class="aa-dot">&middot;</span>
<span>Motion by <b>{escape(r["moving_party"])}</b></span></p>
<p class="aa-issue">{h("issue")}</p>
<ul class="aa-topics" aria-label="Topics">{topics}</ul>
<p class="aa-meta">{meta}</p></article>"""


def steps(r: dict, query: str) -> str:
    rows = (("Moving party&rsquo;s argument", f"{escape(r['moving_party'])}, as described by the court", "argument"),
            ("Opposition", "as described by the court", "opposition"),
            ("Court&rsquo;s reasoning", f"{escape(r['outcome'])}", "court_reasoning"))
    items = "".join(f'<li><span class="aa-node" aria-hidden="true">{i}</span><div><p class="aa-step-k">{k} '
                    f'<span>{sub}</span></p><p class="aa-step-v">{highlight(r[key], query)}</p></div></li>'
                    for i, (k, sub, key) in enumerate(rows, 1))
    return (f'<ol class="aa-steps">{items}</ol><p class="aa-foot"><b>Scope.</b> {highlight(r["scope_note"], query)}'
            f' &middot; {source_anchor(r)}</p>')


def empty_state(title: str, body: str) -> str:
    return (f'<div class="aa-empty-state">{icon("search-x", 34)}<h3>{escape(title)}</h3>'
            f'<p>{escape(body)}</p></div>')


def compare_grid(rows: list[dict]) -> str:
    fields = (
        ("Outcome", lambda r: f'<span class="aa-kicker">Motion to exclude</span><br>{badge(r["outcome"])}'),
        ("Court &amp; date", lambda r: f'{escape(r["court"])}<br><span class="aa-muted">{escape(long_date(r["date"]))}</span>'),
        ("Moving party", lambda r: escape(r["moving_party"])),
        ("Docket", lambda r: f'<span class="aa-mono">{escape(r["docket"])}<br>Order Doc. {escape(r["order_document"])}'
                             f' &middot; Motion Doc. {escape(r["motion_document"])}</span>'),
        ("Issue", lambda r: f'<b>{escape(r["issue"])}</b>'),
        ("Challenge <small>as described by the court</small>", lambda r: escape(r["argument"])),
        ("Opposition <small>as described by the court</small>", lambda r: escape(r["opposition"])),
        ("Court&rsquo;s reasoning", lambda r: escape(r["court_reasoning"])),
        ("Scope note", lambda r: f'<span class="aa-muted">{escape(r["scope_note"])}</span>'),
        ("Source", lambda r: source_anchor(r, f"Order Doc. {r['order_document']}, p. {int(r['source_page'])}")),
    )
    head = "".join(f'<th scope="col"><span class="aa-cmp-exp">{escape(r["expert"])}</span>'
                   f'<span class="aa-cmp-case">{escape(r["case_name"])}</span></th>' for r in rows)
    body = "".join(f'<tr><th scope="row">{label}</th>{"".join(f"<td>{fn(r)}</td>" for r in rows)}</tr>'
                   for label, fn in fields)
    return (f'<div class="aa-cmp-wrap" role="region" aria-label="Side-by-side comparison" tabindex="0">'
            f'<table class="aa-cmp" style="min-width:{150 + 250 * len(rows)}px"><thead><tr>'
            f'<th scope="col"><span class="aa-sr">Field</span></th>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def case_cards(records: list[dict]) -> str:
    cases: dict[str, list[dict]] = {}
    for r in records:
        cases.setdefault(r["case_id"], []).append(r)
    out = []
    for group in cases.values():
        r = group[0]
        experts = ", ".join(escape(x["expert"].split()[-1]) for x in group)
        out.append(f"""<article class="aa-case-card"><p class="aa-court">{icon("landmark", 14)}{escape(r["court"])}
&middot; decided {escape(long_date(r["date"]))}</p><h3 class="aa-case">{escape(r["case_name"])}</h3>
<p class="aa-meta">{escape(r["docket"])} &middot; Order Doc. {escape(r["order_document"])}</p>
<p class="aa-n"><b>{len(group)}</b> curated {"ruling" if len(group) == 1 else "rulings"}: {experts}</p>
<div class="aa-mini">{"".join(badge(x["outcome"]) for x in group)}</div>
{source_anchor(r, f"Court order, Doc. {r['order_document']} (PDF)").replace(f"#page={int(r['source_page'])}", "")}</article>""")
    return f'<div class="aa-cases">{"".join(out)}</div>'


SCOPE = """<div class="aa-scope"><div><p class="aa-label">In this proof of concept</p><ul>
<li>10 rulings on motions to exclude expert testimony, from 4 public Missouri federal court orders (2015&ndash;2025)</li>
<li>Manual summaries tied to an order document and PDF page</li>
<li>Keyword search (SQLite FTS5), filters, side-by-side comparison, DRAFT Word and CSV export</li>
<li>No firm data and no model-provider credentials required</li></ul></div>
<div><p class="aa-label">Not included</p><ul>
<li>Party-filed motions, oppositions, and exhibits</li>
<li>AI/LLM extraction or generation, semantic search, OCR</li>
<li>Legal citator, subsequent-history, or current-law checks</li>
<li>Comprehensive coverage: this is not a legal research database</li></ul></div></div>"""


def footer() -> str:
    return ('<footer class="aa-footer">Argument Atlas &middot; Proof of concept on public court orders &middot; '
            'Not legal advice &middot; Not filing-ready; every entry requires attorney validation.</footer>')


CSS = """<style>
:root{
  --aa-primary:#1E3A8A; --aa-primary-hover:#1E40AF; --aa-accent:#B45309;
  --aa-bg:#F8FAFC; --aa-card:#FFFFFF; --aa-fg:#0F172A; --aa-muted-bg:#EEF2F7; --aa-muted-bg-2:#E9EEF5;
  --aa-muted:#475569; --aa-border:#CBD5E1; --aa-border-soft:#E2E8F0;
  --aa-denied-fg:#115E59; --aa-denied-bg:#CCFBF1; --aa-denied:#0F766E;
  --aa-granted-fg:#9F1239; --aa-granted-bg:#FFE4E6; --aa-granted:#BE123C;
  --aa-partial-fg:#92400E; --aa-partial-bg:#FEF3C7; --aa-partial:#D97706;
  --aa-serif:"EB Garamond",Georgia,"Times New Roman",serif; --aa-sans:"Lato",system-ui,sans-serif;
  --aa-mono:"JetBrains Mono",ui-monospace,Consolas,monospace;
  --aa-radius:14px; --aa-shadow:0 1px 2px rgba(15,23,42,.05),0 1px 3px rgba(15,23,42,.06);
  --aa-shadow-hover:0 4px 14px rgba(15,23,42,.08); --aa-ease:180ms ease;
}
[data-testid="stMainBlockContainer"]{max-width:1180px;padding:1.25rem 1.5rem 3rem}
header[data-testid="stHeader"]{background:transparent}
.aa-ico{display:inline-block;flex:none;vertical-align:-.15em;background:currentColor}
ul.aa-status,ul.aa-legend,ul.aa-topics,ol.aa-steps{padding-left:0}
.aa-status li,.aa-legend li,.aa-topics li,.aa-steps li{margin:0}
.st-key-searchpanel [data-testid="stButtonGroup"] > div{flex-wrap:wrap;row-gap:.35rem}
.aa-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.aa-muted{color:var(--aa-muted)}
.aa-mono,.aa-meta{font-family:var(--aa-mono);font-size:.78rem;letter-spacing:-.01em;color:var(--aa-muted)}
.aa-label{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--aa-muted);margin:0 0 .5rem}
mark{background:#FDE68A;color:inherit;padding:0 .12em;border-radius:3px}
a:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--aa-accent);outline-offset:2px;border-radius:4px}

.aa-mast{display:flex;justify-content:space-between;align-items:flex-end;gap:1.25rem;flex-wrap:wrap;
  padding:.5rem 0 1.1rem;border-bottom:2px solid var(--aa-accent)}
.aa-brand{display:flex;gap:1rem;align-items:center}
.aa-mark{display:grid;place-items:center;width:52px;height:52px;border-radius:12px;background:var(--aa-primary);color:#fff;flex:none}
.aa-eyebrow{font-variant:small-caps;letter-spacing:.09em;font-size:.95rem;font-weight:700;color:var(--aa-accent);margin:0}
.aa-word{font-family:var(--aa-serif);font-weight:600;font-size:2.6rem;line-height:1.02;color:var(--aa-fg);margin:.05rem 0 .3rem;letter-spacing:-.01em}
.aa-tag{margin:0;color:var(--aa-muted);font-size:.95rem;max-width:62ch}
.aa-status{display:flex;gap:.4rem;flex-wrap:wrap;list-style:none;margin:0;padding:0}
.aa-status li{font-size:.75rem;font-weight:700;letter-spacing:.03em;color:var(--aa-primary);background:var(--aa-card);
  border:1px solid var(--aa-border);padding:.28rem .7rem;border-radius:999px}
.aa-status li:first-child{background:var(--aa-primary);border-color:var(--aa-primary);color:#fff}

.aa-callout{display:flex;gap:.75rem;align-items:flex-start;background:var(--aa-card);border:1px solid var(--aa-border-soft);
  border-left:4px solid var(--aa-primary);border-radius:10px;padding:.85rem 1rem;color:var(--aa-fg);margin-top:.25rem}
.aa-callout .aa-ico{color:var(--aa-primary);margin-top:.15rem}
.aa-callout p{margin:0;line-height:1.55;max-width:96ch}

.aa-badge{display:inline-flex;align-items:center;gap:.32rem;font-size:.78rem;font-weight:700;line-height:1;
  padding:.32rem .6rem .32rem .45rem;border-radius:999px;border:1px solid transparent;white-space:nowrap}
.aa-badge.aa-denied{color:var(--aa-denied-fg);background:var(--aa-denied-bg);border-color:#99F6E4}
.aa-badge.aa-granted{color:var(--aa-granted-fg);background:var(--aa-granted-bg);border-color:#FECDD3}
.aa-badge.aa-partial{color:var(--aa-partial-fg);background:var(--aa-partial-bg);border-color:#FDE68A}
.aa-kicker{font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--aa-muted)}

.aa-overview{display:grid;grid-template-columns:repeat(3,minmax(0,1fr)) minmax(0,2.4fr);gap:.75rem}
.aa-kpi,.aa-dist{background:var(--aa-card);border:1px solid var(--aa-border-soft);border-radius:12px;padding:.85rem 1rem;box-shadow:var(--aa-shadow)}
.aa-kpi{display:flex;flex-direction:column;justify-content:center}
.aa-kpi-n{font-family:var(--aa-serif);font-size:2.1rem;font-weight:600;line-height:1;color:var(--aa-primary)}
.aa-kpi-l{font-size:.78rem;color:var(--aa-muted);margin-top:.3rem;font-weight:700;letter-spacing:.02em}
.aa-dist .aa-label{margin-bottom:.45rem}
.aa-bar{display:flex;gap:3px;height:10px;border-radius:999px;overflow:hidden;background:var(--aa-muted-bg)}
.aa-seg{min-width:6px}
.aa-seg.aa-denied{background:var(--aa-denied)} .aa-seg.aa-granted{background:var(--aa-granted)}
.aa-seg.aa-partial{background:var(--aa-partial);background-image:repeating-linear-gradient(135deg,rgba(255,255,255,.35) 0 3px,transparent 3px 6px)}
.aa-legend{display:flex;flex-wrap:wrap;gap:.35rem 1.1rem;list-style:none;margin:.6rem 0 0;padding:0}
.aa-legend li{display:flex;align-items:center;gap:.4rem;font-size:.85rem}
.aa-count{font-weight:700;color:var(--aa-fg)} .aa-pct{color:var(--aa-muted);font-size:.78rem}

.aa-rhead{display:flex;align-items:baseline;justify-content:space-between;gap:.5rem 1rem;flex-wrap:wrap;
  border-bottom:1px solid var(--aa-border);padding-bottom:.4rem;margin-top:.4rem}
.aa-rhead h2{font-family:var(--aa-serif);font-weight:600;font-size:1.55rem;margin:0;padding:0;color:var(--aa-fg)}
.aa-rhead p{margin:0;color:var(--aa-muted);font-size:.82rem}

[class*="st-key-rec_"]{background:var(--aa-card);border:1px solid var(--aa-border-soft);border-radius:var(--aa-radius);
  padding:1.1rem 1.35rem 1rem;box-shadow:var(--aa-shadow);transition:border-color var(--aa-ease),box-shadow var(--aa-ease)}
[class*="st-key-rec_"]:hover{border-color:var(--aa-border);box-shadow:var(--aa-shadow-hover)}
[class*="st-key-rec_"][class*="--sel"]{border-left:4px solid var(--aa-primary)}
.aa-card{color:var(--aa-fg)}
.aa-top{display:flex;align-items:center;gap:.5rem .6rem;flex-wrap:wrap}
.aa-court{display:inline-flex;align-items:center;gap:.35rem;color:var(--aa-muted);font-size:.85rem;margin:0}
.aa-top .aa-court{margin-left:auto}
.aa-case{font-family:var(--aa-serif);font-weight:600;font-size:1.5rem;line-height:1.2;margin:.55rem 0 .2rem;padding:0;color:var(--aa-fg)}
.aa-who{display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;margin:0 0 .45rem;color:var(--aa-fg);font-size:.98rem}
.aa-who .aa-ico{color:var(--aa-primary)} .aa-dot{color:var(--aa-border)}
.aa-issue{font-size:1.08rem;line-height:1.5;margin:0 0 .55rem;max-width:70ch;color:var(--aa-fg);
  border-left:3px solid var(--aa-accent);padding-left:.65rem}
.aa-topics{display:flex;flex-wrap:wrap;gap:.35rem;list-style:none;margin:0 0 .55rem;padding:0}
.aa-topics li{font-size:.76rem;color:var(--aa-primary);background:var(--aa-muted-bg-2);padding:.2rem .55rem;border-radius:6px;font-weight:700}
.aa-meta{margin:0}

.aa-steps{list-style:none;margin:.2rem 0 0;padding:0;position:relative}
.aa-steps li{display:grid;grid-template-columns:28px minmax(0,1fr);gap:.8rem;position:relative;padding-bottom:1rem}
.aa-steps li:not(:last-child)::before{content:"";position:absolute;left:13px;top:28px;bottom:2px;width:2px;background:var(--aa-border-soft)}
.aa-node{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--aa-muted-bg-2);
  color:var(--aa-primary);font-weight:700;font-size:.8rem;border:1px solid var(--aa-border)}
.aa-steps li:last-child .aa-node{background:var(--aa-primary);color:#fff;border-color:var(--aa-primary)}
.aa-step-k{margin:.2rem 0 .2rem;font-weight:700;font-size:.92rem;color:var(--aa-fg)}
.aa-step-k span{font-weight:400;color:var(--aa-muted);font-size:.82rem;margin-left:.3rem}
.aa-step-v{margin:0;line-height:1.6;max-width:70ch;color:var(--aa-fg)}
.aa-foot{margin:.1rem 0 0;padding-top:.65rem;border-top:1px dashed var(--aa-border);font-size:.85rem;color:var(--aa-muted);line-height:1.5}
.aa-src{display:inline-flex;align-items:center;gap:.3rem;font-weight:700;color:var(--aa-primary);text-decoration:none;
  border-bottom:1px solid transparent;transition:border-color var(--aa-ease),color var(--aa-ease)}
.aa-src:hover{color:var(--aa-primary-hover);border-bottom-color:currentColor}

.aa-empty-state{text-align:center;background:var(--aa-card);border:1px dashed var(--aa-border);border-radius:var(--aa-radius);padding:2rem 1.25rem 1.25rem;color:var(--aa-muted)}
.aa-empty-state .aa-ico{color:var(--aa-primary)}
.aa-empty-state h3{font-family:var(--aa-serif);font-weight:600;font-size:1.4rem;color:var(--aa-fg);margin:.5rem 0 .3rem;padding:0}
.aa-empty-state p{margin:0 auto;max-width:56ch}

.aa-cmp-wrap{overflow-x:auto;border:1px solid var(--aa-border-soft);border-radius:var(--aa-radius);background:var(--aa-card);box-shadow:var(--aa-shadow)}
.aa-cmp{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed;font-size:.93rem;line-height:1.55}
.aa-cmp th,.aa-cmp td{padding:.8rem 1rem;vertical-align:top;text-align:left;border-bottom:1px solid var(--aa-border-soft);color:var(--aa-fg)}
.aa-cmp tr:last-child th,.aa-cmp tr:last-child td{border-bottom:0}
.aa-cmp thead th{background:var(--aa-muted-bg);border-bottom:2px solid var(--aa-accent);position:sticky;top:0}
.aa-cmp tbody th{width:150px;font-size:.76rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--aa-muted);background:#FBFCFE}
.aa-cmp thead th:first-child{width:150px}
.aa-cmp th:first-child{position:sticky;left:0;z-index:1;border-right:1px solid var(--aa-border-soft)}
.aa-cmp tbody th small{display:block;text-transform:none;letter-spacing:0;font-weight:400;font-size:.75rem;margin-top:.15rem}
.aa-cmp td+td{border-left:1px solid var(--aa-border-soft)}
.aa-cmp-exp{display:block;font-family:var(--aa-serif);font-size:1.3rem;font-weight:600;line-height:1.15}
.aa-cmp-case{display:block;font-weight:400;font-size:.82rem;color:var(--aa-muted);margin-top:.15rem}

.aa-cases{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem}
.aa-case-card{background:var(--aa-card);border:1px solid var(--aa-border-soft);border-radius:var(--aa-radius);padding:1rem 1.2rem;
  box-shadow:var(--aa-shadow);transition:border-color var(--aa-ease),box-shadow var(--aa-ease)}
.aa-case-card:hover{border-color:var(--aa-border);box-shadow:var(--aa-shadow-hover)}
.aa-case-card .aa-case{font-size:1.35rem;margin:.35rem 0 .2rem}
.aa-n{margin:.5rem 0 .4rem;font-size:.92rem}
.aa-mini{display:flex;gap:.3rem;flex-wrap:wrap;margin-bottom:.7rem}
.aa-scope{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;background:var(--aa-card);border:1px solid var(--aa-border-soft);
  border-radius:var(--aa-radius);padding:1rem 1.25rem}
.aa-scope ul{margin:0;padding-left:1.1rem;line-height:1.6;font-size:.94rem} .aa-scope li{margin-bottom:.2rem}
.aa-footer{margin-top:2rem;padding-top:.9rem;border-top:1px solid var(--aa-border);color:var(--aa-muted);font-size:.8rem;text-align:center}

.aa-sec{font-family:var(--aa-serif);font-weight:600;font-size:1.45rem;margin:.2rem 0 .1rem;color:var(--aa-fg)}
.aa-sub{color:var(--aa-muted);margin:0 0 .4rem;max-width:80ch;line-height:1.55}
.st-key-searchpanel,.st-key-exportpanel,.st-key-spotpanel,.st-key-tray{background:var(--aa-card);border:1px solid var(--aa-border-soft);
  border-radius:var(--aa-radius);padding:1.1rem 1.25rem;box-shadow:var(--aa-shadow)}
.st-key-tray{background:var(--aa-muted-bg-2);box-shadow:none;padding:.6rem .6rem .6rem 1rem;border-color:var(--aa-border)}
.st-key-searchpanel input{font-size:1.05rem}
[data-testid="stWidgetLabel"] p{font-weight:700;font-size:.8rem;letter-spacing:.04em;color:var(--aa-muted)}
[data-testid="stTabs"] [role="tablist"]{gap:.25rem}
[data-testid="stTabs"] button[role="tab"] p{font-size:1rem;font-weight:700}
[data-testid="stExpander"] details{background:var(--aa-card)}
[data-testid="stExpander"] summary p{font-weight:700;color:var(--aa-primary)}
button,a,[role="tab"],[data-testid="stExpander"] summary{transition:background-color var(--aa-ease),border-color var(--aa-ease),color var(--aa-ease),box-shadow var(--aa-ease)}

@media (max-width:900px){
  .aa-overview{grid-template-columns:repeat(3,minmax(0,1fr))}
  .aa-dist{grid-column:1/-1}
  .aa-cases,.aa-scope{grid-template-columns:1fr}
}
@media (max-width:640px){
  [data-testid="stMainBlockContainer"]{padding:1rem 1rem 2.5rem}
  .aa-mast{align-items:flex-start}
  .aa-word{font-size:2.05rem} .aa-mark{width:44px;height:44px}
  .aa-top .aa-court{margin-left:0;width:100%}
  [class*="st-key-rec_"]{padding:.95rem 1rem .9rem}
  .aa-case{font-size:1.3rem}
  .aa-kpi{padding:.7rem .75rem} .aa-kpi-n{font-size:1.7rem}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
</style>"""
CSS = CSS.replace("</style>", "\n".join(map(_mask, _PATHS)) + "\n</style>")
