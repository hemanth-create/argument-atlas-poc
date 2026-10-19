from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import load_records, search, source_link, compare_rows, word_comparison, download_public_pdf, tokenize_query


def test_data_ids_and_real_source_shape():
    records = load_records()
    assert len(records) == 10
    assert len({r["case_id"] for r in records}) == 4
    assert all(r["source_url"].startswith("https://cases.justia.com/") for r in records)
    assert all(int(r["source_page"]) > 0 for r in records)


def test_search_relevant_results():
    result = search(load_records(), "differential diagnosis")
    ids = {r["id"] for r in result}
    assert "scott-sevin" in ids
    assert "scott-norsworthy" in ids


def test_search_filters_and_injection():
    recs = load_records()
    assert isinstance(search(recs, "' OR xyznotinrecord NOT opaqueunusedterm"), list)
    assert search(recs, "xyznotinrecord opaqueunusedterm") == []
    assert all(r["outcome"] == "Denied" for r in search(recs, outcome="Denied"))
    assert all(r["court"] == "E.D. Missouri" for r in search(recs, court="E.D. Missouri"))
    assert tokenize_query('"NOT" OR ()') == ["not", "or"]


def test_compare_selection_and_page_links():
    rows = compare_rows(load_records(), ["scott-sevin", "scott-norsworthy"])
    assert len(rows) == 2
    assert "#page=23" in source_link(rows[1])


def test_word_output():
    blob = word_comparison(load_records()[:2])
    assert blob[:2] == b"PK"
    assert len(blob) > 3000


def test_public_pdf_url_allowlist(tmp_path):
    with pytest.raises(ValueError):
        download_public_pdf("http://example.com/hack.pdf", tmp_path)
    with pytest.raises(ValueError):
        download_public_pdf("https://internal.company.com/secret.pdf", tmp_path)
