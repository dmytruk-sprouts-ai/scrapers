"""Canonical Pydantic model for LKPP ``TenderUmumPublik`` records.

The spider captures the endpoint's JSON verbatim (one array per year+LPSE). This module turns one
raw row into a validated :class:`IsbTender`:

* the **canonical** cross-portal fields the downstream schema wants are exposed as
  ``@computed_field`` properties (``tender_id``, ``procurement_type``, ``procurement_method``,
  ``status``, ``submission_deadline``, ``issuing_agency`` …), derived via validators/mappings;
* **every source field** is kept too — the richer nested ones (agencies, budgets, locations,
  schedules, counts, evaluation/payment method, consolidation, spse version) are modelled
  explicitly rather than collapsed, and anything unmodelled (English-keyed variants seen on other
  SPSE versions) is retained via ``extra="allow"``.

Translation (English title/description) is intentionally out of scope here.

Indonesian source keys carry spaces (``"Kode Tender"``, ``"Nama Paket"``), so fields use
``alias=``; ``populate_by_name=True`` lets you also build by field name.

Usage::

    from .models import IsbTender, parse_tender_payload
    tenders = parse_tender_payload(item["content"])      # list[IsbTender]
    tenders[0].model_dump(by_alias=False)                # canonical + rich, JSON-ready
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
)

SOURCE_COUNTRY = "ID"
CURRENCY = "IDR"


# --------------------------------------------------------------------------- enums
class ProcurementType(str, Enum):
    GOODS = "Goods"
    WORKS = "Works"
    SERVICES = "Services"
    CONSULTING = "Consulting"
    OTHER = "Other"


class ProcurementMethod(str, Enum):
    OPEN_TENDER = "Open tender"
    E_BIDDING_FAST = "e-Bidding (fast)"
    SELECTION = "Selection (consulting)"
    DIRECT_APPOINTMENT = "Direct appointment"
    DIRECT_PROCUREMENT = "Direct procurement"
    OTHER = "Other"


class TenderStatus(str, Enum):
    ONGOING = "Ongoing"  # "Tender Sedang Berjalan" — open / not closed
    CLOSED = "Closed"  # "Tender Ditutup"
    UNKNOWN = "Unknown"


# Kategori Pekerjaan -> ProcurementType. Matched by keyword so the many consulting variants
# ("Jasa Konsultansi Badan Usaha / Perorangan, Konstruksi / Non Konstruksi") all collapse.
def _procurement_type(work_category: str | None) -> ProcurementType:
    c = (work_category or "").lower()
    if "konsultan" in c:  # konsultansi / konsultan (perorangan & badan usaha)
        return ProcurementType.CONSULTING
    if "konstruksi" in c:  # "Pekerjaan Konstruksi" (consulting-konstruksi caught above)
        return ProcurementType.WORKS
    if "barang" in c:  # "Pengadaan Barang"
        return ProcurementType.GOODS
    if "jasa lainnya" in c:
        return ProcurementType.SERVICES
    return ProcurementType.OTHER


# Metode Pemilihan -> ProcurementMethod.
def _procurement_method(selection_method: str | None) -> ProcurementMethod:
    m = (selection_method or "").strip().lower()
    if m == "tender cepat":
        return ProcurementMethod.E_BIDDING_FAST
    if m == "tender":
        return ProcurementMethod.OPEN_TENDER
    if m == "seleksi":
        return ProcurementMethod.SELECTION
    if "penunjukan langsung" in m:
        return ProcurementMethod.DIRECT_APPOINTMENT
    if "pengadaan langsung" in m:
        return ProcurementMethod.DIRECT_PROCUREMENT
    return ProcurementMethod.OTHER


def _status(status_raw: str | None) -> TenderStatus:
    s = (status_raw or "").strip().lower()
    if s == "tender sedang berjalan":
        return TenderStatus.ONGOING
    if s == "tender ditutup":
        return TenderStatus.CLOSED
    return TenderStatus.UNKNOWN


# --------------------------------------------------------------------------- sub-models
class _Sub(BaseModel):
    # Keep unmodelled keys (SPSE-version drift) instead of dropping them.
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class AgencyUnit(_Sub):
    """One entry of ``Instansi dan Satker`` — the agency + work unit behind the package."""

    rup_id: int | None = None
    package_id: int | None = Field(default=None, alias="pkt_id")
    lpse_id: int | None = None
    agency_type: str | None = Field(default=None, alias="jenis_instansi")
    agency_name: str | None = Field(default=None, alias="nama_instansi")
    work_unit: str | None = Field(default=None, alias="stk_nama")


class BudgetLine(_Sub):
    """One entry of ``anggaran`` — a funding source + value + budget account code."""

    rup_id: int | None = None
    fund_source: str | None = Field(default=None, alias="sbd_id")
    value: Decimal | None = Field(default=None, alias="ang_nilai")
    year: int | None = Field(default=None, alias="ang_tahun")
    account_code: str | None = Field(default=None, alias="ang_koderekening")


class LocationDetail(_Sub):
    city: str | None = Field(default=None, alias="kbp_nama")
    province: str | None = Field(default=None, alias="prp_nama")
    address: str | None = Field(default=None, alias="pkt_lokasi")


class PackageLocation(_Sub):
    """One entry of ``lokasi_paket`` — wraps a ``lokasi`` detail object."""

    lokasi: LocationDetail | None = None


class Schedule(_Sub):
    """A ``jadwal_*`` stage window (announcement / bidding)."""

    start: date | None = Field(default=None, alias="tanggal_mulai")
    end: date | None = Field(default=None, alias="tanggal_akhir")

    @field_validator("start", "end", mode="before")
    @classmethod
    def _blank_to_none(cls, v: Any) -> Any:
        return None if v in ("", None) else v


# --------------------------------------------------------------------------- main model
class IsbTender(_Sub):
    """A single ``TenderUmumPublik`` package, validated.

    Build with ``IsbTender.model_validate(raw_row)``. ``model_dump()`` yields the rich source
    fields plus the canonical ``@computed_field`` projection.
    """

    # --- identity / source -------------------------------------------------
    tender_code: int = Field(alias="Kode Tender")
    lpse_repo_id: int | None = Field(default=None, alias="Repo id LPSE")
    lpse_name: str | None = Field(default=None, alias="LPSE")
    status_raw: str | None = Field(default=None, alias="Status_Tender")

    # --- descriptive -------------------------------------------------------
    title: str = Field(alias="Nama Paket")
    work_category: str | None = Field(default=None, alias="Kategori Pekerjaan")

    # --- money -------------------------------------------------------------
    ceiling: Decimal | None = Field(default=None, alias="Pagu")  # Pagu
    hps: Decimal | None = Field(default=None, alias="HPS")  # estimate

    # --- dates -------------------------------------------------------------
    created_date: date | None = Field(default=None, alias="tanggal paket dibuat")
    published_at: datetime | None = Field(default=None, alias="tanggal paket tayang")
    announcement_schedule: Schedule | None = Field(
        default=None, alias="jadwal_pengumuman"
    )
    bidding_schedule: Schedule | None = Field(default=None, alias="jadwal_penawaran")

    # --- method / process --------------------------------------------------
    selection_method: str | None = Field(default=None, alias="Metode Pemilihan")
    procurement_method_detail: str | None = Field(
        default=None, alias="Metode Pengadaan"
    )
    evaluation_method: str | None = Field(default=None, alias="Metode Evaluasi")
    payment_method: str | None = Field(default=None, alias="Cara Pembayaran")
    winner_determination: str | None = Field(
        default=None, alias="Jenis Penetapan Pemenang"
    )

    # --- consolidation -----------------------------------------------------
    is_consolidation: bool | None = Field(default=None, alias="Apakah paket konsolidasi")
    consolidation_packages: Any | None = Field(
        default=None, alias="daftar paket konsolidasi"
    )

    # --- nested collections ------------------------------------------------
    agencies: list[AgencyUnit] = Field(default_factory=list, alias="Instansi dan Satker")
    budgets: list[BudgetLine] = Field(default_factory=list, alias="anggaran")
    locations: list[PackageLocation] = Field(default_factory=list, alias="lokasi_paket")

    # --- stats -------------------------------------------------------------
    num_registrants: int | None = Field(default=None, alias="Jumlah Pendaftar")
    num_bidders: int | None = Field(default=None, alias="Jumlah Penawar")
    num_qualifications: int | None = Field(default=None, alias="jumlah_kirim_kualifikasi")
    duration_days: int | None = Field(default=None, alias="Durasi Tender")
    spse_version: str | None = Field(default=None, alias="Versi_spse_paket")

    # ----------------------------------------------------------------- validators
    @field_validator("published_at", mode="before")
    @classmethod
    def _parse_published(cls, v: Any) -> Any:
        # "2024-02-05 15:00:00" (space separator) or a plain date; "" -> None.
        if v in ("", None):
            return None
        if isinstance(v, str) and " " in v and "T" not in v:
            return v.replace(" ", "T", 1)
        return v

    @field_validator(
        "spse_version",
        "work_category",
        "selection_method",
        "procurement_method_detail",
        "evaluation_method",
        "payment_method",
        "winner_determination",
        "status_raw",
        "lpse_name",
        mode="before",
    )
    @classmethod
    def _blank_str_to_none(cls, v: Any) -> Any:
        return None if isinstance(v, str) and not v.strip() else v

    @field_validator("agencies", "budgets", "locations", mode="before")
    @classmethod
    def _null_to_empty_list(cls, v: Any) -> Any:
        # These arrays are sometimes serialised as null rather than [] (varies by year/LPSE).
        return [] if v is None else v

    @field_validator("is_consolidation", mode="before")
    @classmethod
    def _yesno_to_bool(cls, v: Any) -> Any:
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("ya", "yes", "y", "true", "1"):
                return True
            if s in ("tidak", "no", "n", "false", "0", ""):
                return False
        return v

    # ----------------------------------------------------------------- canonical projection
    @computed_field  # type: ignore[prop-decorator]
    @property
    def tender_id(self) -> str:
        # Kode Tender already encodes the LPSE id (…119), but prefix the country so the id is
        # unambiguous once records from MY/TH land in the same table.
        return f"{SOURCE_COUNTRY}-{self.tender_code}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def source_country(self) -> str:
        return SOURCE_COUNTRY

    @computed_field  # type: ignore[prop-decorator]
    @property
    def currency(self) -> str:
        return CURRENCY

    @computed_field  # type: ignore[prop-decorator]
    @property
    def procurement_type(self) -> ProcurementType:
        return _procurement_type(self.work_category)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def procurement_method(self) -> ProcurementMethod:
        return _procurement_method(self.selection_method)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status(self) -> TenderStatus:
        return _status(self.status_raw)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_open(self) -> bool:
        return self.status is TenderStatus.ONGOING

    @computed_field  # type: ignore[prop-decorator]
    @property
    def budget_value(self) -> Decimal | None:
        # Canonical "est. value": HPS (owner's estimate) when present, else the Pagu ceiling.
        return self.hps if self.hps is not None else self.ceiling

    @computed_field  # type: ignore[prop-decorator]
    @property
    def publication_date(self) -> date | None:
        if self.published_at is not None:
            return self.published_at.date()
        if self.announcement_schedule and self.announcement_schedule.start:
            return self.announcement_schedule.start
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def submission_deadline(self) -> date | None:
        return self.bidding_schedule.end if self.bidding_schedule else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def issuing_agency(self) -> str | None:
        return self.agencies[0].agency_name if self.agencies else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def work_unit(self) -> str | None:
        return self.agencies[0].work_unit if self.agencies else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def province(self) -> str | None:
        loc = self.locations[0].lokasi if self.locations else None
        return loc.province if loc else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def city(self) -> str | None:
        loc = self.locations[0].lokasi if self.locations else None
        return loc.city if loc else None


def parse_tender_payload(content: str | bytes | list) -> list[IsbTender]:
    """Validate a whole ``TenderUmumPublik`` response body into a list of tenders.

    Accepts the raw JSON text (the spider's ``item["content"]``), bytes, or an already-decoded
    list. Each array element is one package.
    """
    rows = content if isinstance(content, list) else json.loads(content)
    return [IsbTender.model_validate(row) for row in rows]
