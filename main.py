"""
Phone Number Lookup API
Powered by Google's libphonenumber. Offline, zero cost, no API keys.
Returns: validity, country, carrier, number type, formatted output.
"""

from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import phonenumbers
from phonenumbers import carrier, geocoder, phonenumberutil

app = FastAPI(title="Phone Number Lookup API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

class PhoneResult(BaseModel):
    phone: str
    valid: bool
    country: Optional[str] = None
    country_code: Optional[int] = None
    location: Optional[str] = None
    carrier: Optional[str] = None
    number_type: Optional[str] = None
    e164: Optional[str] = None
    international: Optional[str] = None
    national: Optional[str] = None
    possible: bool = False

TYPE_MAP = {
    phonenumberutil.PhoneNumberType.MOBILE: "Mobile",
    phonenumberutil.PhoneNumberType.FIXED_LINE: "Fixed Line",
    phonenumberutil.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
    phonenumberutil.PhoneNumberType.TOLL_FREE: "Toll Free",
    phonenumberutil.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    phonenumberutil.PhoneNumberType.SHARED_COST: "Shared Cost",
    phonenumberutil.PhoneNumberType.VOIP: "VoIP",
    phonenumberutil.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    phonenumberutil.PhoneNumberType.PAGER: "Pager",
    phonenumberutil.PhoneNumberType.UAN: "UAN",
    phonenumberutil.PhoneNumberType.VOICEMAIL: "Voicemail",
    phonenumberutil.PhoneNumberType.UNKNOWN: "Unknown",
}

@app.get("/")
async def root():
    return {"service": "Phone Number Lookup API", "version": "1.0.0"}

@app.get("/lookup", response_model=PhoneResult)
async def lookup(
    phone: str = Query(..., description="Phone number in international format, e.g. +14155552671 or +8613800138000"),
    country_hint: str = Query("CN", description="Default country code if number has no prefix"),
):
    try:
        num = phonenumbers.parse(phone, country_hint)
    except phonenumberutil.NumberParseException:
        return PhoneResult(phone=phone, valid=False)

    return PhoneResult(
        phone=phone,
        valid=phonenumbers.is_valid_number(num),
        possible=phonenumbers.is_possible_number(num),
        country=geocoder.description_for_number(num, "en") or None,
        country_code=num.country_code,
        location=geocoder.description_for_number(num, "en") or None,
        carrier=carrier.name_for_number(num, "en") or None,
        number_type=TYPE_MAP.get(phonenumberutil.number_type(num), "Unknown"),
        e164=phonenumberutil.format_number(num, phonenumberutil.PhoneNumberFormat.E164),
        international=phonenumberutil.format_number(num, phonenumberutil.PhoneNumberFormat.INTERNATIONAL),
        national=phonenumberutil.format_number(num, phonenumberutil.PhoneNumberFormat.NATIONAL),
    )
