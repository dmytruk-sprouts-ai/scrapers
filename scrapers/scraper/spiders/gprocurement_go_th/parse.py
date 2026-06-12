"""Field parsing for Thai e-GP (gprocurement.go.th) detail records.

The detail spider (``gprocurement_details``) yields raw JSON in ``BaseItem``: ``content`` is the
``getProjectDetail`` response body and ``extra`` carries the sibling endpoints
(``getProcurementDetail``, ``greenBook``, ``infoDeptSub``) plus the fetched announcement documents.
This module turns one such raw record into the project's **canonical tender schema** plus an
``extra`` bag of everything the schema doesn't carry.

``parse_record(item)`` returns ``(canonical, extra)``:

* ``canonical`` — the agreed cross-portal fields (see ``CANONICAL_FIELDS``). Source country / currency
  are constants for TH; the English title/description are left ``None`` here (machine translation is
  a downstream step, not parsing).
* ``extra`` — every leftover source field, keyed by the same ``tender_id`` so the two JSONL files
  join cleanly.
"""

from __future__ import annotations

import json
from typing import Any

from .facets_translation import list_procure_method, list_procure_type

SOURCE_COUNTRY = "TH"
SOURCE_PORTAL = "gprocurement.go.th"
CURRENCY = "THB"

# The canonical field order, also used as the JSONL column order.
CANONICAL_FIELDS = [
    "tender_id",
    "source_country",
    "source_portal",
    "issuing_agency",
    "title_original",
    "title_english",
    "description_original",
    "description_english",
    "procurement_type",
    "budget_value",
    "currency",
    "publication_date",
    "submission_deadline",
    "procurement_method",
    "category_codes",
    "document_links",
]

# ``typeId`` (getProjectDetail/getProcurementDetail) -> (Thai name, normalized procurement type).
# The portal exposes the names via /egp-rdb-service/listProcureType but not the numeric ids; the
# id<->name order below is inferred from that list. The raw ``typeId`` is always preserved in the
# ``extra`` bag, so a wrong guess here is recoverable without re-scraping.
TYPE_ID_TO_THAI = {
    "01": "ซื้อ",
    "02": "จ้างก่อสร้าง",
    "03": "จ้างทำของ/จ้างเหมาบริการ",
    "04": "เช่า",
    "05": "จ้างที่ปรึกษา",
    "06": "จ้างออกแบบ",
    "07": "จ้างควบคุมงาน",
    "08": "จ้างออกแบบและควบคุมงานก่อสร้าง",
}
# Normalized Goods / Services / Works / Consulting bucket per type id.
TYPE_ID_TO_PROCTYPE = {
    "01": "Goods",
    "02": "Works",
    "03": "Services",
    "04": "Services",
    "05": "Consulting",
    "06": "Consulting",
    "07": "Services",
    "08": "Consulting",
}

# ``methodId`` (getProjectDetail/getProcurementDetail) -> Thai method name, straight from
# /egp-rdb-service/listProcureMethod. English names come from ``list_procure_method``.
METHOD_ID_TO_THAI = {
    "01": "ตกลงราคา",
    "02": "สอบราคา",
    "03": "ประกวดราคา",
    "04": "พิเศษ",
    "05": "กรณีพิเศษ",
    "06": "ประกวดราคาด้วยวิธีการทางอิเล็กทรอนิกส์โดยผ่านผู้ให้บริการตลาดกลาง",
    "08": "จ้างที่ปรึกษาโดยวิธีตกลง",
    "09": "จ้างที่ปรึกษาโดยวิธีคัดเลือก",
    "10": "จ้างออกแบบโดยวิธีตกลง",
    "11": "จ้างออกแบบโดยวิธีคัดเลือก",
    "12": "จ้างออกแบบโดยวิธีคัดเลือกแบบจำกัดข้อกำหนด",
    "13": "จ้างออกแบบโดยวิธีพิเศษ",
    "14": "จ้างออกแบบโดยวิธีพิเศษประกวดแบบ",
    "15": "ตลาดอิเล็กทรอนิกส์ (e-market)",
    "16": "ประกวดราคาอิเล็กทรอนิกส์ (e-bidding)",
    "17": "เฉพาะเจาะจง ผ่านบัตรพัสดุ",
    "18": "คัดเลือก",
    "19": "เฉพาะเจาะจง",
    "20": "จ้างที่ปรึกษาโดยวิธีประกาศเชิญชวนทั่วไป",
    "21": "จ้างที่ปรึกษาโดยวิธีคัดเลือก",
    "22": "จ้างที่ปรึกษาโดยวิธีเฉพาะเจาะจง",
    "23": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีประกาศเชิญชวนทั่วไป",
    "24": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีคัดเลือก",
    "25": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีเฉพาะเจาะจง",
    "26": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีประกวดแบบ",
    "28": "ประกวดราคานานาชาติ",
}


def _normalize_method(thai: str | None) -> str | None:
    """Collapse a Thai method name to the schema's coarse bucket (Open tender / Direct / ...)."""
    if not thai:
        return None
    if "e-bidding" in thai or "อิเล็กทรอนิกส์" in thai and "ตลาด" not in thai:
        return "e-Bidding"
    if "e-market" in thai or "ตลาดอิเล็กทรอนิกส์" in thai:
        return "e-Market"
    if "เฉพาะเจาะจง" in thai:
        return "Direct"
    if "คัดเลือก" in thai:
        return "Selection"
    if "ประกาศเชิญชวนทั่วไป" in thai or "ประกวดราคา" in thai:
        return "Open tender"
    if "สอบราคา" in thai:
        return "Quotation"
    if "ตกลง" in thai:
        return "Price Agreement"
    if "พิเศษ" in thai:
        return "Special"
    return None


def _loads(value: Any) -> dict:
    """Parse a stored endpoint body (a JSON string) into a dict; tolerate junk/empties."""
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _data(body: Any) -> dict:
    """Unwrap the ``{"response": ..., "data": ...}`` envelope to its ``data`` dict."""
    data = _loads(body).get("data")
    return data if isinstance(data, dict) else {}


def parse_record(item) -> tuple[dict, dict]:
    """Map one raw detail ``BaseItem`` to ``(canonical, extra)``.

    ``canonical`` holds the cross-portal schema fields; ``extra`` holds every leftover source
    field. Both are keyed by ``tender_id`` so the two output files join on it.
    """
    extra_in = dict(item.get("extra") or {})
    project = _data(item.get("content"))
    procurement = _data(extra_in.get("getProcurementDetail"))
    dept = _data(extra_in.get("infoDeptSub"))
    green = _data(extra_in.get("greenBook"))

    tender_id = (
        project.get("projectId")
        or procurement.get("projectId")
        or extra_in.get("project_id")
    )

    type_id = project.get("typeId") or procurement.get("typeId")
    method_id = project.get("methodId") or procurement.get("methodId")
    method_thai = METHOD_ID_TO_THAI.get(method_id) if method_id else None

    # Agency: the infoDeptSub parent department is the cleanest "ministry/department" value; fall
    # back to the procuring sub-unit name carried on the project/procurement records.
    issuing_agency = (
        (dept.get("deptName") or "").strip()
        or (procurement.get("deptSubName") or project.get("deptSubName") or "").strip()
        or None
    )

    budget = procurement.get("projectMoney")
    if budget is None:
        budget = procurement.get("priceBuild")

    canonical = {
        "tender_id": tender_id,
        "source_country": SOURCE_COUNTRY,
        "source_portal": SOURCE_PORTAL,
        "issuing_agency": issuing_agency,
        "title_original": project.get("projectName") or procurement.get("projectName"),
        # Machine translation is a downstream step; parsing leaves the English fields empty.
        "title_english": None,
        # TH detail carries no distinct free-text description at this stage (depth varies).
        "description_original": None,
        "description_english": None,
        "procurement_type": TYPE_ID_TO_PROCTYPE.get(type_id) if type_id else None,
        "budget_value": budget,
        "currency": CURRENCY,
        "publication_date": procurement.get("announceDate")
        or procurement.get("reportDate"),
        # No bid-closing date is exposed on the TH detail endpoints.
        "submission_deadline": None,
        "procurement_method": _normalize_method(method_thai),
        "category_codes": [c for c in (project.get("goodsId"), type_id) if c],
        "document_links": _document_links(extra_in, green),
    }

    extra = {
        "tender_id": tender_id,
        "type_id": type_id,
        "type_thai": TYPE_ID_TO_THAI.get(type_id) if type_id else None,
        "type_english": list_procure_type.get(TYPE_ID_TO_THAI.get(type_id, "")),
        "method_id": method_id,
        "method_thai": method_thai,
        "method_english": list_procure_method.get(method_thai or ""),
        "publish_type_name": project.get("publishTypeName"),
        "announce_type": project.get("announceType"),
        "step_id": project.get("stepId"),
        "project_status": project.get("projectStatus"),
        "price_build": procurement.get("priceBuild"),
        "price_agree": procurement.get("priceAgree"),
        "dept_id": procurement.get("deptId") or dept.get("deptId", "").strip() or None,
        "dept_sub_id": procurement.get("deptSubId"),
        "dept_name": (dept.get("deptName") or "").strip() or None,
        "dept_sub_name": procurement.get("deptSubName") or project.get("deptSubName"),
        "province_name": dept.get("provinceName"),
        "district_name": dept.get("districtName"),
        "report_date": procurement.get("reportDate"),
        "announce_date": procurement.get("announceDate"),
        # Whole raw payloads, so nothing is lost to the schema's lossy projection.
        "raw": {
            "getProjectDetail": project,
            "getProcurementDetail": procurement,
            "greenBook": green,
            "infoDeptSub": dept,
            "documents": extra_in.get("documents", []),
        },
    }
    return canonical, extra


def _document_links(extra_in: dict, green: dict) -> list[dict]:
    """Announcement document links: the fetched ShowHTMLFile docs plus any greenBook file paths."""
    links: list[dict] = []
    for doc in extra_in.get("documents") or []:
        links.append(
            {
                "url": doc.get("url"),
                "announce_type": doc.get("announceType"),
                "seq_no": doc.get("seqNo"),
                "status": doc.get("status"),
            }
        )
    for entry in green.get("greenBookAnnouncementTypeLinkDto") or []:
        file_path = entry.get("filePath")
        if file_path:
            links.append(
                {
                    "url": file_path,
                    "announce_type": entry.get("announceType"),
                    "seq_no": entry.get("seqNo"),
                    "status": None,
                }
            )
    return links
