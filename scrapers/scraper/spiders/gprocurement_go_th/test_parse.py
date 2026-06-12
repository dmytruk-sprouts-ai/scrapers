"""Offline field-parsing tests for the Thai e-GP detail records (no network)."""

import json

from .parse import parse_record


def _envelope(data: dict) -> str:
    return json.dumps({"response": {"responseCode": "0"}, "data": data})


def _item() -> dict:
    """A raw detail BaseItem shaped exactly like the detail spider emits one."""
    return {
        "content": _envelope(
            {
                "projectId": "69069212137",
                "methodId": "19",
                "typeId": "03",
                "projectName": "จ้างเหมารถตู้โดยสารไม่ประจำทาง โดยวิธีเฉพาะเจาะจง",
                "goodsId": "4004",
                "deptSubName": "ศูนย์ส่งเสริมการเรียนรู้อำเภอหนองแซง",
                "publishTypeName": "(ข) ไม่เกินวงเงิน",
                "announceType": "W0",
            }
        ),
        "extra": {
            "project_id": "69069212137",
            "getProcurementDetail": _envelope(
                {
                    "projectId": "69069212137",
                    "deptId": "2033",
                    "deptSubId": "203310000849",
                    "methodId": "19",
                    "typeId": "03",
                    "projectMoney": 5500.0,
                    "priceBuild": 5500.0,
                    "announceDate": "2026-06-11T17:00:00.000+00:00",
                    "reportDate": "2026-06-10T17:00:00.000+00:00",
                }
            ),
            "greenBook": _envelope({"greenBookAnnouncementTypeLinkDto": []}),
            "infoDeptSub": _envelope(
                {
                    "deptId": "2033                ",
                    "deptName": "กรมส่งเสริมการเรียนรู้",
                    "provinceName": "สระบุรี",
                }
            ),
            "documents": [
                {
                    "announceType": "W0",
                    "seqNo": 1,
                    "url": "https://process3.gprocurement.go.th/doc?pid=69069212137",
                    "status": 200,
                    "content": "<html></html>",
                }
            ],
        },
    }


def test_canonical_fields():
    canonical, _ = parse_record(_item())
    assert canonical["tender_id"] == "69069212137"
    assert canonical["source_country"] == "TH"
    assert canonical["currency"] == "THB"
    assert canonical["issuing_agency"] == "กรมส่งเสริมการเรียนรู้"
    assert canonical["title_original"].startswith("จ้างเหมารถตู้")
    assert canonical["procurement_type"] == "Services"
    assert canonical["procurement_method"] == "Direct"
    assert canonical["budget_value"] == 5500.0
    assert canonical["publication_date"] == "2026-06-11T17:00:00.000+00:00"
    assert canonical["category_codes"] == ["4004", "03"]
    assert canonical["document_links"][0]["url"].endswith("pid=69069212137")
    # Machine-translation / unavailable fields stay empty rather than guessed.
    assert canonical["title_english"] is None
    assert canonical["submission_deadline"] is None


def test_extra_keyed_by_tender_id_and_carries_raw():
    canonical, extra = parse_record(_item())
    assert extra["tender_id"] == canonical["tender_id"]
    assert extra["method_thai"] == "เฉพาะเจาะจง"
    assert extra["type_english"] == "Hire of Work / Service Outsourcing"
    assert extra["raw"]["getProjectDetail"]["projectId"] == "69069212137"


def test_tolerates_missing_and_malformed_payloads():
    canonical, extra = parse_record({"content": "not json", "extra": {}})
    assert canonical["tender_id"] is None
    assert canonical["source_country"] == "TH"
    assert canonical["document_links"] == []
