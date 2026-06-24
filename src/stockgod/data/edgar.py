"""Read-only SEC EDGAR provider client, normalizers, and Form 4 helpers."""

from __future__ import annotations

from typing import Any

from stockgod.data._http import UrlLibSession, request_json, utc_now
from stockgod.data.config import ProviderConfig, load_provider_config
from stockgod.data.errors import MissingApiKeyError, ProviderNotImplementedError, ProviderResponseError


def normalize_edgar_company_submissions(raw: dict, cik_or_ticker: str) -> dict:
    cik = str(raw.get("cik") or _normalize_cik(cik_or_ticker))
    recent = raw.get("filings", {}).get("recent", {}) if isinstance(raw.get("filings"), dict) else {}
    data = {"cik": cik, "symbol": _first(raw.get("tickers"), str(cik_or_ticker).upper()), "name": raw.get("name"), "recent_filings": recent}
    return {"provider": "sec_edgar", "cik": cik, "symbol": data["symbol"], "ticker": data["symbol"], "as_of": _first(recent.get("filingDate"), utc_now()), "data": data, "raw": raw}


def normalize_edgar_form4_filings(raw: dict, cik_or_ticker: str) -> dict:
    envelope = normalize_edgar_company_submissions(raw, cik_or_ticker)
    recent = envelope["data"].get("recent_filings", {})
    forms = recent.get("form", []) if isinstance(recent, dict) else []
    filings = []
    for index, form_type in enumerate(forms):
        if form_type != "4":
            continue
        filings.append({"cik": envelope["cik"], "accession_number": _at(recent.get("accessionNumber"), index), "filing_date": _at(recent.get("filingDate"), index), "form_type": form_type, "reporting_owner": _at(recent.get("reportingOwner"), index)})
    return {**envelope, "data": {"cik": envelope["cik"], "symbol": envelope.get("symbol"), "form4_filings": filings}}


def classify_form4_transaction_code(transaction_code: str | None) -> str:
    code = (transaction_code or "").strip().upper()
    if code == "P":
        return "potential_purchase"
    if code == "A":
        return "grant_or_award"
    if code == "M":
        return "option_exercise_or_conversion"
    if code == "F":
        return "tax_or_payment_related"
    if code in {"S", "D"}:
        return "sale_or_disposition"
    return "unknown_or_unverified"


def is_potential_form4_purchase(transaction_code: str | None) -> bool:
    return classify_form4_transaction_code(transaction_code) == "potential_purchase"


def is_qualifying_purchase_code(transaction_code: str | None) -> bool:
    return is_potential_form4_purchase(transaction_code)


class EdgarClient:
    provider = "sec_edgar"

    def __init__(self, config: ProviderConfig | None = None, session: Any | None = None, base_url: str = "https://data.sec.gov") -> None:
        self.config = config or load_provider_config()
        self.session = session or UrlLibSession()
        self.base_url = base_url.rstrip("/")

    def get_company_submissions(self, cik_or_ticker: str) -> dict:
        self._require_user_agent()
        cik = _normalize_cik(cik_or_ticker)
        if not cik.isdigit():
            raise ProviderResponseError("EDGAR requests require numeric CIK until ticker mapping is added")
        raw = request_json(self.session, f"{self.base_url}/submissions/CIK{cik}.json", headers=self._headers())
        return normalize_edgar_company_submissions(raw, cik_or_ticker)

    def get_form4_filings(self, cik_or_ticker: str) -> dict:
        self._require_user_agent()
        cik = _normalize_cik(cik_or_ticker)
        if not cik.isdigit():
            raise ProviderResponseError("EDGAR Form 4 requests require numeric CIK until ticker mapping is added")
        raw = request_json(self.session, f"{self.base_url}/submissions/CIK{cik}.json", headers=self._headers())
        return normalize_edgar_form4_filings(raw, cik_or_ticker)

    def fetch_form4_raw(self, accession_url: str) -> dict:
        raise ProviderNotImplementedError("Form 4 raw filing parsing is not implemented in Phase 4A")

    def _require_user_agent(self) -> None:
        if not self.config.sec_user_agent:
            raise MissingApiKeyError("SEC_USER_AGENT is required for EDGAR requests")

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": self.config.sec_user_agent}


def _normalize_cik(cik_or_ticker: str) -> str:
    value = str(cik_or_ticker).strip().upper()
    if not value.isdigit():
        return value
    return value.zfill(10)


def _first(value: Any, fallback: Any = None) -> Any:
    return value[0] if isinstance(value, list) and value else fallback


def _at(value: Any, index: int) -> Any:
    return value[index] if isinstance(value, list) and len(value) > index else None
