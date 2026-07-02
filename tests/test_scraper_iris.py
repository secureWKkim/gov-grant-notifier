from pathlib import Path
from datetime import date

import pytest

from src.scraper import parse_iris, filter_by_date

FIXTURE = Path("tests/fixtures/iris_sample.html").read_text(encoding="utf-8")


# ── parse_iris ────────────────────────────────────────────────────────────────

def test_parse_iris_returns_ten_items():
    assert len(parse_iris(FIXTURE)) == 10


def test_parse_iris_first_item_title():
    items = parse_iris(FIXTURE)
    assert items[0]["title"] == "2026년 휴먼프론티어과학프로그램(HFSP) 협력사업(사전지원) 신규과제 공고"


def test_parse_iris_first_item_institution():
    items = parse_iris(FIXTURE)
    assert items[0]["inst"] == "과학기술정보통신부 > 한국연구재단"


def test_parse_iris_first_item_date():
    items = parse_iris(FIXTURE)
    assert items[0]["date"] == "2026-06-30"


def test_parse_iris_first_item_field():
    items = parse_iris(FIXTURE)
    assert items[0]["field"] == "자유공모"


def test_parse_iris_first_item_url():
    items = parse_iris(FIXTURE)
    assert items[0]["url"] == (
        "https://www.iris.go.kr/contents/retrieveBsnsAncmView.do"
        "?ancmId=022737&ancmPrg=ancmIng"
    )


def test_parse_iris_all_items_have_required_keys():
    required = {"title", "inst", "date", "field", "url"}
    for item in parse_iris(FIXTURE):
        assert required <= item.keys()


# ── filter_by_date ────────────────────────────────────────────────────────────

def test_filter_by_date_returns_three_items_for_june_30():
    items = parse_iris(FIXTURE)
    filtered = filter_by_date(items, date(2026, 6, 30))
    assert len(filtered) == 3


def test_filter_by_date_returns_empty_for_unmatched_date():
    items = parse_iris(FIXTURE)
    assert filter_by_date(items, date(2025, 1, 1)) == []
