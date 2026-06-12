# https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement/getStepGrp

STEPS = [
    {
        "stepGrpId": "1",
        "stepGrpName": "จัดทำร่าง TOR",
        "startDate": "2015-02-18T17:00:00.000+00:00",
        "lastDate": None,
        "stepWebName": "จัดทำ TOR",
    },
    {
        "stepGrpId": "2",
        "stepGrpName": "หน.ส่วนราชการเห็นชอบฯ",
        "startDate": "2015-02-18T17:00:00.000+00:00",
        "lastDate": None,
        "stepWebName": "รายงานขอซื้อขอจ้าง",
    },
    {
        "stepGrpId": "3",
        "stepGrpName": "ประกาศเชิญชวน",
        "startDate": "2015-02-18T17:00:00.000+00:00",
        "lastDate": None,
        "stepWebName": "หนังสือเชิญชวน/ประกาศเชิญชวน",
    },
    {
        "stepGrpId": "4",
        "stepGrpName": "หน.ส่วนราชการอนุมัติฯ",
        "startDate": "2015-02-18T17:00:00.000+00:00",
        "lastDate": None,
        "stepWebName": "อนุมัติสั่งซื้อสั่งจ้างและประกาศผู้ชนะการเสนอราคา",
    },
    {
        "stepGrpId": "5",
        "stepGrpName": "มูลค่าตามสัญญา",
        "startDate": "2015-02-18T17:00:00.000+00:00",
        "lastDate": None,
        "stepWebName": "จัดทำสัญญา/บริหารสัญญา",
    },
]

STEP_ID_MAPPING = {v["stepGrpName"]: v["stepGrpId"] for v in STEPS}
