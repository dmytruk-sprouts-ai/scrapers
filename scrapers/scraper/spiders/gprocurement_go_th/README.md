
# Protection



## Pagination / filtering

facets 

```
https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement/getStepGrp
```
```json
{
    "response": {
        "responseCode": "0",
        "messageCode": null,
        "description": null
    },
    "data": [
        {
            "stepGrpId": "1",
            "stepGrpName": "จัดทำร่าง TOR",
            "startDate": "2015-02-18T17:00:00.000+00:00",
            "lastDate": null,
            "stepWebName": "จัดทำ TOR"
        },
        {
            "stepGrpId": "2",
            "stepGrpName": "หน.ส่วนราชการเห็นชอบฯ",
            "startDate": "2015-02-18T17:00:00.000+00:00",
            "lastDate": null,
            "stepWebName": "รายงานขอซื้อขอจ้าง"
        },
        {
            "stepGrpId": "3",
            "stepGrpName": "ประกาศเชิญชวน",
            "startDate": "2015-02-18T17:00:00.000+00:00",
            "lastDate": null,
            "stepWebName": "หนังสือเชิญชวน/ประกาศเชิญชวน"
        },
        {
            "stepGrpId": "4",
            "stepGrpName": "หน.ส่วนราชการอนุมัติฯ",
            "startDate": "2015-02-18T17:00:00.000+00:00",
            "lastDate": null,
            "stepWebName": "อนุมัติสั่งซื้อสั่งจ้างและประกาศผู้ชนะการเสนอราคา"
        },
        {
            "stepGrpId": "5",
            "stepGrpName": "มูลค่าตามสัญญา",
            "startDate": "2015-02-18T17:00:00.000+00:00",
            "lastDate": null,
            "stepWebName": "จัดทำสัญญา/บริหารสัญญา"
        }
    ]
}
```

https://process5.gprocurement.go.th/egp-rdb-service/listProcureMethod
{
    "response": {
        "responseCode": "0",
        "messageCode": "I0001",
        "description": "สำเร็จ"
    },
    "data": [
        {
            "methodId": "01",
            "methodName": "ตกลงราคา",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "02",
            "methodName": "สอบราคา",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "methodId": "03",
            "methodName": "ประกวดราคา",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "methodId": "04",
            "methodName": "พิเศษ",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "05",
            "methodName": "กรณีพิเศษ",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "06",
            "methodName": "ประกวดราคาด้วยวิธีการทางอิเล็กทรอนิกส์โดยผ่านผู้ให้บริการตลาดกลาง",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "methodId": "08",
            "methodName": "จ้างที่ปรึกษาโดยวิธีตกลง",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "09",
            "methodName": "จ้างที่ปรึกษาโดยวิธีคัดเลือก",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "10",
            "methodName": "จ้างออกแบบโดยวิธีตกลง",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "11",
            "methodName": "จ้างออกแบบโดยวิธีคัดเลือก",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "12",
            "methodName": "จ้างออกแบบโดยวิธีคัดเลือกแบบจำกัดข้อกำหนด",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "13",
            "methodName": "จ้างออกแบบโดยวิธีพิเศษ",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "15",
            "methodName": "ตลาดอิเล็กทรอนิกส์ (e-market)",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "methodId": "16",
            "methodName": "ประกวดราคาอิเล็กทรอนิกส์ (e-bidding)",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "methodId": "17",
            "methodName": "เฉพาะเจาะจง ผ่านบัตรพัสดุ",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "14",
            "methodName": "จ้างออกแบบโดยวิธีพิเศษประกวดแบบ",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "methodId": "18",
            "methodName": "คัดเลือก",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "19",
            "methodName": "เฉพาะเจาะจง",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "20",
            "methodName": "จ้างที่ปรึกษาโดยวิธีประกาศเชิญชวนทั่วไป",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "21",
            "methodName": "จ้างที่ปรึกษาโดยวิธีคัดเลือก",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "22",
            "methodName": "จ้างที่ปรึกษาโดยวิธีเฉพาะเจาะจง",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "23",
            "methodName": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีประกาศเชิญชวนทั่วไป",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "24",
            "methodName": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีคัดเลือก",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "25",
            "methodName": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีเฉพาะเจาะจง",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "26",
            "methodName": "จ้างออกแบบหรือควบคุมงานก่อสร้างโดยวิธีประกวดแบบ",
            "startDate": "2016-07-01",
            "lastDate": null
        },
        {
            "methodId": "28",
            "methodName": "ประกวดราคานานาชาติ",
            "startDate": "2018-07-01",
            "lastDate": null
        }
    ]
}


https://process5.gprocurement.go.th/egp-rdb-service/listProcureType
{
    "response": {
        "responseCode": "0",
        "messageCode": "I0001",
        "description": "สำเร็จ"
    },
    "data": [
        {
            "typeId": "01",
            "typeName": "ซื้อ",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "typeId": "02",
            "typeName": "จ้างก่อสร้าง",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "typeId": "03",
            "typeName": "จ้างทำของ/จ้างเหมาบริการ",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "typeId": "04",
            "typeName": "เช่า",
            "startDate": "2008-04-01",
            "lastDate": null
        },
        {
            "typeId": "05",
            "typeName": "จ้างที่ปรึกษา",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "typeId": "06",
            "typeName": "จ้างออกแบบ",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "typeId": "07",
            "typeName": "จ้างควบคุมงาน",
            "startDate": "2012-02-01",
            "lastDate": null
        },
        {
            "typeId": "08",
            "typeName": "จ้างออกแบบและควบคุมงานก่อสร้าง",
            "startDate": "2012-02-01",
            "lastDate": null
        }
    ]
}


https://process5.gprocurement.go.th/egp-rdb-service/listGoods
{
    "response": {
        "responseCode": "0",
        "messageCode": "I0001",
        "description": "สำเร็จ"
    },
    "data": [
        {
            "goodsId": "1000",
            "goodsName": "วัสดุครุภัณฑ์"
        },
        {
            "goodsId": "1001",
            "goodsName": "วัสดุครุภัณฑ์สำนักงาน"
        },
        {
            "goodsId": "1002",
            "goodsName": "วัสดุครุภัณฑ์การศึกษา"
        },
        {
            "goodsId": "1003",
            "goodsName": "วัสดุครุภัณฑ์งานบ้านงานครัว"
        },
        {
            "goodsId": "1004",
            "goodsName": "ครุภัณฑ์ดนตรี"
        },
        {
            "goodsId": "1005",
            "goodsName": "วัสดุครุภัณฑ์กีฬา"
        },
        {
            "goodsId": "1006",
            "goodsName": "วัสดุครุภัณฑ์วิทยาศาสตร์และการแพทย์"
        },
        {
            "goodsId": "1007",
            "goodsName": "วัสดุครุภัณฑ์ไฟฟ้าและวิทยุ"
        },
        {
            "goodsId": "1008",
            "goodsName": "วัสดุครุภัณฑ์คอมพิวเตอร์"
        },
        {
            "goodsId": "1009",
            "goodsName": "วัสดุครุภัณฑ์สำรวจ"
        },
        {
            "goodsId": "1011",
            "goodsName": "วัสดุครุภัณฑ์โฆษณาและเผยแพร่"
        },
        {
            "goodsId": "1012",
            "goodsName": "วัสดุเชื้อเพลิงและหล่อลื่น"
        },
        {
            "goodsId": "1013",
            "goodsName": "วัสดุครุภัณฑ์ยานพาหนะและขนส่ง"
        },
        {
            "goodsId": "1014",
            "goodsName": "ครุภัณฑ์อาวุธ"
        },
        {
            "goodsId": "1015",
            "goodsName": "วัสดุครุภัณฑ์การเกษตร"
        },
        {
            "goodsId": "1016",
            "goodsName": "ครุภัณฑ์โรงงาน"
        },
        {
            "goodsId": "1017",
            "goodsName": "วัสดุครุภัณฑ์ก่อสร้าง"
        },
        {
            "goodsId": "1018",
            "goodsName": "วัสดุครุภัณฑ์อื่นๆ"
        },
        {
            "goodsId": "2000",
            "goodsName": "ที่ดินและสิ่งก่อสร้าง"
        },
        {
            "goodsId": "2001",
            "goodsName": "ที่ดิน"
        },
        {
            "goodsId": "2002",
            "goodsName": "ที่ดินและสิ่งก่อสร้าง"
        },
        {
            "goodsId": "3000",
            "goodsName": "จ้างก่อสร้าง"
        },
        {
            "goodsId": "3001",
            "goodsName": "จ้างก่อสร้างอาคาร"
        },
        {
            "goodsId": "3002",
            "goodsName": "จ้างก่อสร้างทางสะพานท่อเหลี่ยม"
        },
        {
            "goodsId": "3003",
            "goodsName": "จ้างก่อสร้างชลประทาน"
        },
        {
            "goodsId": "3004",
            "goodsName": "จ้างปรับปรุง ซ่อมแซมอาคาร"
        },
        {
            "goodsId": "3005",
            "goodsName": "จ้างปรับปรุง ซ่อมแซมทางสะพานท่อเหลี่ยม"
        },
        {
            "goodsId": "3006",
            "goodsName": "จ้างปรับปรุง ซ่อมแซมด้านชลประทาน"
        },
        {
            "goodsId": "4000",
            "goodsName": "จ้างเหมา"
        },
        {
            "goodsId": "4001",
            "goodsName": "จ้างเหมางานรักษาความปลอดภัย"
        },
        {
            "goodsId": "4002",
            "goodsName": "จ้างเหมาบริการงานทำความสะอาด"
        },
        {
            "goodsId": "4003",
            "goodsName": "จ้างเหมาบริการงานดูแลต้นไม้ สนามหญ้า"
        },
        {
            "goodsId": "4004",
            "goodsName": "จ้างเหมางานยานพาหนะ"
        },
        {
            "goodsId": "4005",
            "goodsName": "จ้างเหมางานศึกษาวิจัย"
        },
        {
            "goodsId": "4006",
            "goodsName": "จ้างเหมางานติดตามประเมินผล"
        },
        {
            "goodsId": "4007",
            "goodsName": "จ้างเหมางานจัดทำคำแปล"
        },
        {
            "goodsId": "4008",
            "goodsName": "จ้างเหมางานผลิตและพิมพ์เอกสาร"
        },
        {
            "goodsId": "4009",
            "goodsName": "จ้างเหมางานผลิตสื่อการประชาสัมพันธ์"
        },
        {
            "goodsId": "4010",
            "goodsName": "จ้างเหมางานพัฒนาระบบข้อมูลสารสนเทศ"
        },
        {
            "goodsId": "4011",
            "goodsName": "จ้างเหมางานบันทึกข้อมูล"
        },
        {
            "goodsId": "4012",
            "goodsName": "จ้างเหมางานซ่อมบำรุงยานพาหนะ"
        },
        {
            "goodsId": "4013",
            "goodsName": "จ้างเหมางานตรวจสอบและรับรองมาตรฐาน"
        },
        {
            "goodsId": "4014",
            "goodsName": "จ้างเหมางานทำของที่ระลึก"
        },
        {
            "goodsId": "4015",
            "goodsName": "จ้างเหมาอบรมและพัฒนาบุคลากร"
        },
        {
            "goodsId": "4016",
            "goodsName": "จ้างเหมาอื่นๆ"
        },
        {
            "goodsId": "5000",
            "goodsName": "เช่า"
        },
        {
            "goodsId": "5001",
            "goodsName": "เช่าอาคารสถานที่"
        },
        {
            "goodsId": "5002",
            "goodsName": "เช่ารถยนต์ที่ใช้ในราชการ"
        },
        {
            "goodsId": "5003",
            "goodsName": "เช่าใช้บริการอินเตอร์เน็ต"
        },
        {
            "goodsId": "5004",
            "goodsName": "เช่าเครื่องถ่ายเอกสาร"
        },
        {
            "goodsId": "5005",
            "goodsName": "เช่าอื่นๆ"
        },
        {
            "goodsId": "6020",
            "goodsName": "จ้างที่ปรึกษาสาขาการวิจัยและการประเมินผล"
        },
        {
            "goodsId": "6001",
            "goodsName": "จ้างที่ปรึกษาสาขาการเกษตรและพัฒนาชนบท"
        },
        {
            "goodsId": "6002",
            "goodsName": "จ้างที่ปรึกษาสาขาอุตสาหกรรมก่อสร้าง"
        },
        {
            "goodsId": "6003",
            "goodsName": "จ้างที่ปรึกษาสาขาการศึกษา"
        },
        {
            "goodsId": "6004",
            "goodsName": "จ้างที่ปรึกษาสาขาพลังงาน"
        },
        {
            "goodsId": "6005",
            "goodsName": "จ้างที่ปรึกษาสาขาสิ่งแวดล้อม"
        },
        {
            "goodsId": "6006",
            "goodsName": "จ้างที่ปรึกษาสาขาการเงิน"
        },
        {
            "goodsId": "6007",
            "goodsName": "จ้างที่ปรึกษาสาขาสาธารณสุข"
        },
        {
            "goodsId": "6008",
            "goodsName": "จ้างที่ปรึกษาสาขาอุตสาหกรรม"
        },
        {
            "goodsId": "6009",
            "goodsName": "จ้างที่ปรึกษาสาขาเบ็ดเตล็ด"
        },
        {
            "goodsId": "6010",
            "goodsName": "จ้างที่ปรึกษาสาขาประชากร"
        },
        {
            "goodsId": "6011",
            "goodsName": "จ้างที่ปรึกษาสาขาเทคโนโลยีสารสนเทศและการสื่อสาร"
        },
        {
            "goodsId": "6012",
            "goodsName": "จ้างที่ปรึกษาสาขาการท่องเที่ยว"
        },
        {
            "goodsId": "6013",
            "goodsName": "จ้างที่ปรึกษาสาขาการคมนาคมขนส่ง"
        },
        {
            "goodsId": "6014",
            "goodsName": "จ้างที่ปรึกษาสาขาการพัฒนาเมือง"
        },
        {
            "goodsId": "7000",
            "goodsName": "จ้างออกแบบและควบคุมงาน"
        },
        {
            "goodsId": "3012",
            "goodsName": "จ้างปรับปรุง ซ่อมแซมทาง"
        },
        {
            "goodsId": "3013",
            "goodsName": "จ้างปรับปรุง ซ่อมแซมสะพานท่อเหลี่ยม"
        },
        {
            "goodsId": "3010",
            "goodsName": "จ้างก่อสร้างทาง"
        },
        {
            "goodsId": "3011",
            "goodsName": "จ้างก่อสร้างสะพานท่อเหลี่ยม"
        },
        {
            "goodsId": "3008",
            "goodsName": "จ้างก่อสร้างอื่นๆนอกเหนือหลักเกณฑ์"
        },
        {
            "goodsId": "6015",
            "goodsName": "จ้างที่ปรึกษาสาขาการประปาและสุขาภิบาล"
        },
        {
            "goodsId": "6016",
            "goodsName": "จ้างที่ปรึกษาสาขากฎหมาย"
        },
        {
            "goodsId": "6017",
            "goodsName": "จ้างที่ปรึกษาสาขามาตรฐานคุณภาพ"
        },
        {
            "goodsId": "6018",
            "goodsName": "จ้างที่ปรึกษาสาขาการบริหารและการพัฒนาองค์กร"
        },
        {
            "goodsId": "6019",
            "goodsName": "จ้างที่ปรึกษาสาขาการประชาสัมพันธ์"
        },
        {
            "goodsId": "6000",
            "goodsName": "จ้างที่ปรึกษา"
        },
        {
            "goodsId": "7007",
            "goodsName": "งานสถาปัตยกรรม"
        },
        {
            "goodsId": "7008",
            "goodsName": "งานขนส่งระบบราง"
        },
        {
            "goodsId": "7009",
            "goodsName": "งานถนน"
        },
        {
            "goodsId": "7010",
            "goodsName": "งานสะพานหรือทางถนนที่มีมาตรฐานสูง"
        },
        {
            "goodsId": "7011",
            "goodsName": "งานเขื่อน"
        },
        {
            "goodsId": "7012",
            "goodsName": "งานชลประทาน"
        },
        {
            "goodsId": "7013",
            "goodsName": "งานท่าเรือหรือโครงสร้างริมน้ำหรือในน้ำ"
        },
        {
            "goodsId": "7014",
            "goodsName": "งานระบบสาธารณูปโภคใต้ดิน"
        },
        {
            "goodsId": "7015",
            "goodsName": "งานประปา"
        },
        {
            "goodsId": "7016",
            "goodsName": "งานระบบรวบรวมและบำบัดน้ำเสีย"
        },
        {
            "goodsId": "7017",
            "goodsName": "งานระบบระบายน้ำและการป้องกันน้ำท่วม"
        },
        {
            "goodsId": "7018",
            "goodsName": "งานสนามบิน"
        }
    ]
}



https://process5.gprocurement.go.th/egp-rdb-service/rdbsysm011/listProvince
{
    "response": {
        "responseCode": "0",
        "messageCode": "I0001",
        "description": "สำเร็จ"
    },
    "data": [
        {
            "provinceMoiId": "810000",
            "provinceName": "กระบี่",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "100000",
            "provinceName": "กรุงเทพมหานคร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "710000",
            "provinceName": "กาญจนบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "460000",
            "provinceName": "กาฬสินธุ์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "620000",
            "provinceName": "กำแพงเพชร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "400000",
            "provinceName": "ขอนแก่น",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "220000",
            "provinceName": "จันทบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "240000",
            "provinceName": "ฉะเชิงเทรา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "200000",
            "provinceName": "ชลบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "180000",
            "provinceName": "ชัยนาท",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "360000",
            "provinceName": "ชัยภูมิ",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "860000",
            "provinceName": "ชุมพร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "570000",
            "provinceName": "เชียงราย",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "500000",
            "provinceName": "เชียงใหม่",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "920000",
            "provinceName": "ตรัง",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "230000",
            "provinceName": "ตราด",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "630000",
            "provinceName": "ตาก",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "260000",
            "provinceName": "นครนายก",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "730000",
            "provinceName": "นครปฐม",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "480000",
            "provinceName": "นครพนม",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "300000",
            "provinceName": "นครราชสีมา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "800000",
            "provinceName": "นครศรีธรรมราช",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "600000",
            "provinceName": "นครสวรรค์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "120000",
            "provinceName": "นนทบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "960000",
            "provinceName": "นราธิวาส",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "550000",
            "provinceName": "น่าน",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "380000",
            "provinceName": "บึงกาฬ",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "310000",
            "provinceName": "บุรีรัมย์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "130000",
            "provinceName": "ปทุมธานี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "770000",
            "provinceName": "ประจวบคีรีขันธ์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "250000",
            "provinceName": "ปราจีนบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "940000",
            "provinceName": "ปัตตานี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "140000",
            "provinceName": "พระนครศรีอยุธยา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "560000",
            "provinceName": "พะเยา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "820000",
            "provinceName": "พังงา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "930000",
            "provinceName": "พัทลุง",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "660000",
            "provinceName": "พิจิตร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "650000",
            "provinceName": "พิษณุโลก",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "760000",
            "provinceName": "เพชรบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "670000",
            "provinceName": "เพชรบูรณ์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "540000",
            "provinceName": "แพร่",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "830000",
            "provinceName": "ภูเก็ต",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "440000",
            "provinceName": "มหาสารคาม",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "490000",
            "provinceName": "มุกดาหาร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "580000",
            "provinceName": "แม่ฮ่องสอน",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "350000",
            "provinceName": "ยโสธร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "950000",
            "provinceName": "ยะลา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "450000",
            "provinceName": "ร้อยเอ็ด",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "850000",
            "provinceName": "ระนอง",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "210000",
            "provinceName": "ระยอง",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "700000",
            "provinceName": "ราชบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "160000",
            "provinceName": "ลพบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "520000",
            "provinceName": "ลำปาง",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "510000",
            "provinceName": "ลำพูน",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "420000",
            "provinceName": "เลย",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "330000",
            "provinceName": "ศรีสะเกษ",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "470000",
            "provinceName": "สกลนคร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "900000",
            "provinceName": "สงขลา",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "910000",
            "provinceName": "สตูล",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "110000",
            "provinceName": "สมุทรปราการ",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "750000",
            "provinceName": "สมุทรสงคราม",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "740000",
            "provinceName": "สมุทรสาคร",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "270000",
            "provinceName": "สระแก้ว",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "190000",
            "provinceName": "สระบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "170000",
            "provinceName": "สิงห์บุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "640000",
            "provinceName": "สุโขทัย",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "720000",
            "provinceName": "สุพรรณบุรี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "840000",
            "provinceName": "สุราษฎร์ธานี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "320000",
            "provinceName": "สุรินทร์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "430000",
            "provinceName": "หนองคาย",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "390000",
            "provinceName": "หนองบัวลำภู",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "150000",
            "provinceName": "อ่างทอง",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "370000",
            "provinceName": "อำนาจเจริญ",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "410000",
            "provinceName": "อุดรธานี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "530000",
            "provinceName": "อุตรดิตถ์",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "610000",
            "provinceName": "อุทัยธานี",
            "provinceNameEng": null
        },
        {
            "provinceMoiId": "340000",
            "provinceName": "อุบลราชธานี",
            "provinceNameEng": null
        }
    ]
}