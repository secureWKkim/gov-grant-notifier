import re
from datetime import date

from selectolax.parser import HTMLParser


def parse_iris(html: str) -> list[dict]:
    tree = HTMLParser(html)
    results = []

    for li in tree.css(".tstyle.list.biz_announce ul.dbody > li"):
        title_node = li.css_first("strong.title a")
        if not title_node:
            continue

        title = title_node.text(strip=True)
        onclick = title_node.attributes.get("onclick", "")
        ids = re.findall(r"'(\w+)'", onclick)
        if len(ids) < 2:
            continue
        anc_id, anc_prg = ids[0], ids[1]

        inst_node = li.css_first("span.inst_title")
        date_node = li.css_first("span.ancmDe")
        field_node = li.css_first("span.pbofrTpSeNmLst")

        inst = inst_node.text(strip=True) if inst_node else ""
        date_str = (
            date_node.text(strip=True).replace("공고일자 :", "").strip()
            if date_node else ""
        )
        field = (
            field_node.text(strip=True).replace("공모유형 :", "").strip()
            if field_node else ""
        )
        url = (
            f"https://www.iris.go.kr/contents/retrieveBsnsAncmView.do"
            f"?ancmId={anc_id}&ancmPrg={anc_prg}"
        )

        results.append({
            "title": title,
            "inst": inst,
            "date": date_str,
            "field": field,
            "url": url,
        })

    return results


def filter_by_date(announcements: list[dict], target_date: date) -> list[dict]:
    target_str = target_date.strftime("%Y-%m-%d")
    return [a for a in announcements if a.get("date") == target_str]
