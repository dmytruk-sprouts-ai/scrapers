

https://inaproc.id/satudata#modalKlpd


https://isb.lkpp.go.id/isb-2/api/satudata/MasterKLPD
API Name/Service Name
Daftar KLPD
API Format
JSON
Path URL
https://isb.lkpp.go.id/isb-2/api/satudata/MasterKLPD
Parameter
-
Field API
Field Name	Data Type
kd_klpd	varchar
klpd_name	varchar
type_klpd	varchar
kd_province	int
kd_kabupaten	int
One Example of Request Results
[{"kd_klpd":"D1", "klpd_name":"Aceh", "klpd_type":"PROVINCE", "kd_province":1, "kd_regency":14638}, {"kd_klpd":"D10", "klpd_name":"Bireuen Regency", "klpd_type":"REGENCY", "kd_province":1, "kd_regency":14646}]



API Name/Service Name
Daftar LPSE
API Format
JSON
Path URL
https://isb.lkpp.go.id/isb-2/api/satudata/MasterLPSE
Parameter
-
Field API
Field Name	Data Type	Information
repoId	int	repository ID for each LPSE
LPSE Name	varchar	-
LPSE Version	varchar	SPSE version when data was generated
One Example of Request Results
[{"kd_lpse":10, "lpse_name":"LPSE Surabaya City"}, {"kd_lpse":11, "lpse_name":"LPSE Ministry of Finance"}, {"kd_lpse":12, "lpse_name":"LPSE Central Kalimantan Province"}]

License
CC-BY-NC-SA 4.0

Last Update API/Service



Public Blacklist
API Name/Service Name
Daftar Hitam Publik
API Format
JSON
Path URL
https://isb.lkpp.go.id/isb-2/api/satudata/SanksiDaftarHitam/{tahun}/{kd_klpd}
Parameter
Parameter	Example Value	Information
kd_klpd	K1	KLPD code, taken from the KLPD List
year	2023	fiscal year
Field API
Field Name	Data Type	Information
Decree of Determination	varchar	Decree on the Determination of the Broadcast of the Black List
Blacklist Date Created	timestamp	The Blacklist Air Date
Blacklisted Broadcast Status	varchar	Aired/Revoked/Down due to sanction period
Provider's Taxpayer Identification Number	varchar	-
Provider Name	varchar	-
Provider Province	varchar	Provider's Domicile Province
Provider Regency/City	varchar	Regency/City of Provider's Domicile
Provider Address	varchar	-
Agency	varchar	Origin of the Agency that publishes the Blacklist
Work unit	varchar	Origin of the Work Unit that published the Blacklist
Type of Violation	varchar	Types of Violations based on LKPP Regulations
Description of Type of Violation	varchar	Description of violations based on LKPP Regulations
Decree of Determination	varchar	Decree on the Determination of the Broadcast of the Black List
Sanction Period	jsonb	Consists of the SK number, the start date of the sanction, and the end date of the sanction.
Revocation Decree	varchar	Decree on Revocation of Blacklist Broadcast
Revocation Date	timestamp	Blacklist airing date
One Example of Request Results
https://isb.lkpp.go.id/isb-2/api/satudata/SanksiDaftarHitam/2023/K1
[{"budget_year":"2023", "kd_klpd":"K1", "klpd_name":"Ministry of Religion", "kd_satker":"9286", "satker_name":"IAIN PONOROGO 423821", "kd_lpse":"241", "kd_provider":"xxxx241", "provider_name":"CV.MIxxxx", "provider_NPWP":"02.015.xxx.x-xxx.000", "violation_description":"

Providers who do not carry out the contract, do not complete the work, or whose contract is terminated unilaterally by the PPK due to an error by the Goods/Services Provider

", "revocation_no_sk":"", "revocation_date":"", "correspondent_name":null, "correspondent_email":null, "status":"shown"}]
License
CC-BY-NC-SA 4.0

Last Update API/Service



Public Tender
API Name/Service Name
Tender Umum Publik
API Format
CSV
Path URL
https://isb.lkpp.go.id/isb-2/api/satudata/TenderUmumPublik/{tahun}/{kd_lpse}

Parameter
Parameter	Example Value	Information
kd_lpse	119	LPSE code, taken from the LPSE List
year	2021	the budget year when the tender was conducted
Field API
Field Name	Data Type	Information
Tender Code	int	Tender package code
LPSE ID Repo	int	repository ID for each LPSE
LPSE	varchar	LPSE Name
Tender Status	varchar	Tender status is active or closed
Package Name	varchar	-
Ceiling	numeric	-
HPS	numeric	-
Package Created Date	timestamp	Date the package was first created
Package Release Date	timestamp	Public release date of the package
Job Category	varchar	-
Selection Method	varchar	-
Procurement Method	varchar	-
Evaluation Method	varchar	-
Payment method	varchar	-
Types of Winner Determination	varchar	-
Agencies and Work Units	jsonb	Consists of the rup ID, type of agency, name of agency, and name of work unit.
What is a Consolidation Package?	varchar	Is the tender consolidated with other packages?
Consolidation Package List	jsonb	Consolidation Level List
Budget	jsonb	Consists of funding sources, budget values, and budget account codes.
Package Location	jsonb	Consists of province, district, and other location information
Number of Registrants	int	The large number of applicants for this tender
Number of Bidders	int	The large number of bidders in this tender
Number of Qualification Submissions	int	The large number of Business Actors who submitted qualifications for this tender
Tender Duration	int	Tender duration from initial stage to final stage
SPSE package version	varchar	SPSE version when the tender was created
Announcement Schedule	Date	Announcement Start and End Date
Offer Schedule	Date	Bid Submission Start and End Dates
One Example of Request Results
https://isb.lkpp.go.id/isb-2/api/satudata/TenderUmumPublik/2024/119
[{"Tender Code":9537119, "LPSE Repo id":119, "LPSE":"LPSE Government Goods/Services Procurement Policy Institute", "Tender_Status":"Active", "Package Name":"Individual Consulting Services for Head of Engineering", "Ceiling":1057308000, "HPS":1057308000, "package creation date":"2023-10-11T11:52:42.49", "package broadcast date":"2023-10-17T22:08:00.607", "Work Category":"Individual Consulting Services", "Selection Method":"Selection", "Procurement Method":"Post Two Quality Files", "Evaluation Method":"Quality", "Payment Method":"Assignment Time", "Winner Determination Type":"Non-Itemized Tender", "Agency and Work Unit":[{"rup_id":44604827, "stk_nama":"PRE-EMPLOYMENT CARD PROGRAM IMPLEMENTATION MANAGEMENT", "agency_name":"State Treasury (Ministry of Finance)", "agency_type":"MINISTRY"}], "Is the consolidation package":"NO", "consolidation package list":null, "budget":[{"rup_id":44604827, "sbd_id":"OTHER", "value_number":1057308000, "year_number":2024, "account_code":"-"}], "package_location":[{"kbp_name":"Central Jakarta (City)", "prp_name":"DKI Jakarta", "pkt_location":"Kolega Coworking Space, Park Tower Building, 10th Floor, MNC Center, Jl. Kebon Sirih No.17-19, RT.15/RW.7, Kebon Sirih, Menteng District, Central Jakarta City, DKI Jakarta 10340"}], "Number of Applicants":3, "Number of Bidders":1, "number_of_qualifications_submitted":1, "Tender Duration":77, "Package_spse_version":"Version 4.5","announcement_schedule":{"end_date": "2023-10-30", "start_date": "2023-10-17"},"bidding_schedule":{"end_date": "2023-10-30", "start_date": "2023-10-23"}}]

License
CC-BY-NC-SA 4.0

Last Update API/Service
