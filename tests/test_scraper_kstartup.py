from pathlib import Path
from datetime import date

from src.scraper import parse_kstartup, filter_by_date

FIXTURE = Path("tests/fixtures/kstartup_sample.html").read_text(encoding="utf-8")


# ── parse_kstartup ────────────────────────────────────────────────────────────

def test_parse_kstartup_returns_four_items():
    assert len(parse_kstartup(FIXTURE)) == 4


def test_parse_kstartup_first_item_title():
    items = parse_kstartup(FIXTURE)
    assert items[0]["title"] == "2026년 정부 첫 실증·구매 프로젝트(스마트도시) 창업기업 모집공고"


def test_parse_kstartup_first_item_institution():
    items = parse_kstartup(FIXTURE)
    assert items[0]["inst"] == "창업진흥원"


def test_parse_kstartup_first_item_field():
    items = parse_kstartup(FIXTURE)
    assert items[0]["field"] == "사업화"


def test_parse_kstartup_first_item_reg_date():
    items = parse_kstartup(FIXTURE)
    assert items[0]["date"] == "2026-07-01"


def test_parse_kstartup_first_item_deadline():
    items = parse_kstartup(FIXTURE)
    assert items[0]["deadline"] == "2026-07-22"


def test_parse_kstartup_first_item_url():
    items = parse_kstartup(FIXTURE)
    assert items[0]["url"] == (
        "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
        "?schM=view&pbancSn=178335"
    )


def test_parse_kstartup_all_items_have_required_keys():
    required = {"title", "inst", "date", "deadline", "field", "url"}
    for item in parse_kstartup(FIXTURE):
        assert required <= item.keys()


# ── filter_by_date (reuse) ────────────────────────────────────────────────────

def test_filter_by_date_returns_one_item_for_july_1():
    items = parse_kstartup(FIXTURE)
    filtered = filter_by_date(items, date(2026, 7, 1))
    assert len(filtered) == 1


def test_filter_by_date_returns_two_items_for_june_30():
    items = parse_kstartup(FIXTURE)
    filtered = filter_by_date(items, date(2026, 6, 30))
    assert len(filtered) == 2
