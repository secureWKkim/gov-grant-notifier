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


def parse_kstartup(html: str) -> list[dict]:
    tree = HTMLParser(html)
    results = []

    for li in tree.css("li.notice"):
        title_node = li.css_first("p.tit")
        if not title_node:
            continue

        title = title_node.text(strip=True)

        link_node = li.css_first("a[href]")
        href = link_node.attributes.get("href", "") if link_node else ""
        m = re.search(r"go_view\((\d+)\)", href)
        if not m:
            continue
        pbanc_sn = m.group(1)

        flag_nodes = li.css("span.flag")
        field = ""
        for node in flag_nodes:
            if "day" not in node.attributes.get("class", ""):
                field = node.text(strip=True)
                break

        span_lists = li.css("span.list")
        inst = span_lists[1].text(strip=True) if len(span_lists) > 1 else ""

        date_str, deadline = "", ""
        for span in span_lists:
            text = span.text(strip=True)
            if "등록일자" in text:
                date_str = text.replace("등록일자", "").strip()
            elif "마감일자" in text:
                deadline = text.replace("마감일자", "").strip()

        url = (
            f"https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
            f"?schM=view&pbancSn={pbanc_sn}"
        )

        results.append({
            "title": title,
            "inst": inst,
            "date": date_str,
            "deadline": deadline,
            "field": field,
            "url": url,
        })

    return results


def filter_by_date(announcements: list[dict], target_date: date) -> list[dict]:
    target_str = target_date.strftime("%Y-%m-%d")
    return [a for a in announcements if a.get("date") == target_str]
