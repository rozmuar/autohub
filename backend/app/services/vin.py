"""VIN decoder — year + manufacturer hint from VIN structure."""

import asyncio
import re
import httpx
from datetime import datetime
from typing import TypedDict

# VIN position 10 (index 9) encodes model year.
# The cycle repeats every 30 years: A=1980/2010/2040, B=1981/2011/2041, ...
# I, O, Q, U, Z are excluded from VIN alphabet.
_YEAR_CYCLE = "ABCDEFGHJKLMNPRSTVWXY123456789"  # 30 characters (no I,O,Q,U,Z)


def _decode_year_char(char: str) -> int | None:
    """Return the most recent plausible model year for a VIN year character."""
    char = char.upper()
    if char not in _YEAR_CYCLE:
        return None
    idx = _YEAR_CYCLE.index(char)
    current_year = datetime.now().year
    # Try each 30-year epoch (2010, 1980, 1950…) newest first
    for base in (2010, 1980, 1950):
        year = base + idx
        if year <= current_year + 1:
            return year
    return None


# WMI (first 3 chars) → brand name
_WMI: dict[str, str] = {
    # Toyota
    "JT2": "Toyota", "JT3": "Toyota", "JT4": "Toyota", "JTM": "Toyota",
    "JTD": "Toyota", "JTJ": "Toyota", "JTB": "Toyota", "JTK": "Toyota",
    "JTL": "Toyota", "JTN": "Toyota", "JTZ": "Toyota",
    # Lexus
    "JTH": "Lexus", "JT6": "Lexus", "JT8": "Lexus",
    # Honda
    "JHM": "Honda", "1HG": "Honda", "2HG": "Honda", "5FN": "Honda",
    # Nissan
    "JNK": "Nissan", "JN1": "Nissan", "JN8": "Nissan",
    "1N4": "Nissan", "3N1": "Nissan",
    # Mazda
    "JM1": "Mazda", "JM3": "Mazda", "4F2": "Mazda",
    # Mitsubishi
    "JA3": "Mitsubishi", "JA4": "Mitsubishi", "JA8": "Mitsubishi",
    # Subaru
    "JF1": "Subaru", "JF2": "Subaru",
    # Suzuki
    "JS1": "Suzuki", "JS2": "Suzuki", "JS3": "Suzuki",
    # Isuzu
    "JAC": "Isuzu", "4NB": "Isuzu",
    # BMW
    "WBA": "BMW", "WBS": "BMW", "WBX": "BMW", "WBY": "BMW",
    # Mercedes-Benz (Germany + global assembly plants)
    "WDB": "Mercedes-Benz", "WDD": "Mercedes-Benz", "WDC": "Mercedes-Benz",
    "WDF": "Mercedes-Benz", "WD4": "Mercedes-Benz",
    "WME": "Smart",
    "4JG": "Mercedes-Benz",   # MBUSI Alabama (USA)
    "LBE": "Mercedes-Benz",   # Beijing Benz (Китай)
    "NMB": "Mercedes-Benz",   # Mercedes-Benz Türk (Турция)
    "Z9M": "Mercedes-Benz",   # CIS/European assembly plant
    # Volkswagen
    "WVW": "Volkswagen", "1VW": "Volkswagen",
    "WV1": "Volkswagen", "WV2": "Volkswagen",
    "WV3": "Volkswagen", "WVG": "Volkswagen",
    # Audi
    "WAU": "Audi", "WA1": "Audi", "TRU": "Audi",
    # Porsche
    "WP0": "Porsche", "WP1": "Porsche",
    # Skoda
    "TMB": "Skoda",
    # SEAT
    "VSS": "SEAT", "VS6": "SEAT",
    # Renault / Dacia
    "VF1": "Renault", "VF3": "Renault", "VF4": "Renault",
    "VF6": "Renault", "UU1": "Dacia",
    # Peugeot
    "VF7": "Peugeot",
    # Citroën
    "VF9": "Citroën",
    # Volvo
    "YV1": "Volvo", "YV2": "Volvo",
    # Ford
    "1FA": "Ford", "1FB": "Ford", "1FC": "Ford", "1FD": "Ford",
    "1FM": "Ford", "1FT": "Ford", "3FA": "Ford", "WF0": "Ford",
    # Chevrolet / GMC / Cadillac / Buick
    "1G1": "Chevrolet", "1G4": "Buick",
    "1GY": "Cadillac", "1GT": "GMC", "KL1": "Chevrolet",
    # Kia
    "KNA": "Kia", "KNB": "Kia", "KNC": "Kia", "KND": "Kia",
    # Hyundai
    "KMH": "Hyundai", "KMF": "Hyundai", "KMC": "Hyundai",
    # Lada / VAZ (АВТОВАЗ)
    "XTA": "Lada",
    # GAZ
    "X9G": "GAZ",
    # UAZ
    "XTT": "UAZ",
    # Haval / Great Wall
    "LGW": "Haval", "LGT": "Haval",
    # Geely
    "LS5": "Geely", "L6T": "Geely", "LS6": "Geely", "LHP": "Geely",
    # Chery
    "LVV": "Chery", "L8X": "Chery", "LE4": "Chery",
    # EXEED (Chery premium)
    "LCK": "EXEED",
    # Omoda / Jetour (Chery)
    "LL8": "Omoda", "LJD": "Jetour",
    # BYD
    "LBN": "BYD", "LFV": "BYD", "LGX": "BYD",
    # Changan
    "LZZ": "Changan", "L6N": "Changan",
    # JAC
    "LHB": "JAC", "LJ1": "JAC",
    # BAIC
    "LB2": "BAIC",
    # GAC / Trumpchi
    "LG1": "GAC",
    # Dongfeng
    "LFP": "Dongfeng", "LDD": "Dongfeng",
    # MG / SAIC
    "LSH": "MG", "LDC": "MG",
    # FAW
    "LFB": "FAW", "LFA": "FAW",
    # NIO
    "LW2": "NIO",
    # Li Auto
    "LB8": "Lixiang",
    # Opel
    "W0L": "Opel",
    # Fiat
    "ZFA": "Fiat", "ZFF": "Ferrari",
    # Alfa Romeo
    "ZAR": "Alfa Romeo",
    # Land Rover / Jaguar
    "SAL": "Land Rover", "SAJ": "Jaguar",
    # Mini
    "WMW": "MINI",
    # Chevrolet / GM — Казахстан (Y3W, Y3C, Y3J, Y3N, Y3R)
    "Y3W": "Chevrolet", "Y3C": "Chevrolet", "Y3J": "Chevrolet",
    "Y3N": "Chevrolet", "Y3R": "Chevrolet",
    # Volkswagen — Россия (XW8 — Калуга)
    "XW8": "Volkswagen",
    # Skoda — Россия
    "XW9": "Skoda",
    # Hyundai — Казахстан
    "Y6D": "Hyundai",
    # Kia — Казахстан
    "Y6F": "Kia",
    # Renault — Россия (ABS plant Москва)
    "X7L": "Renault",
    # Toyota — Россия
    "X7T": "Toyota",
    # Mercedes-Benz — Россия (AvtoTor Калининград)
    "XUK": "Mercedes-Benz",
    # Hyundai — Россия (СПб)
    "X7E": "Hyundai",
    # Kia — Россия (Калуга)
    "X7F": "Kia",
    # Toyota — Казахстан (Алматы)
    "Y6T": "Toyota",
    # Nissan — Россия
    "X7N": "Nissan",
    # Mazda — Россия (Владивосток)
    "Z3N": "Mazda",
    # BMW — Россия (AvtoTor Калининград)
    "XUF": "BMW", "XUH": "BMW",
    # Lexus — Россия
    "X7S": "Lexus",
    # Mitsubishi — Россия (Калуга)
    "X7M": "Mitsubishi",
}


# For non-US plants not registered in NHTSA (error 7), substitute with the
# closest US-registered WMI of the same brand so NHTSA can decode VDS/model.
_WMI_NHTSA_SUBST: dict[str, str] = {
    # GM Kazakhstan → nearest US Chevrolet WMI by body type
    "Y3W": "1GN",  # SUV (Tahoe / Suburban / Traverse)
    "Y3C": "1G1",  # Car (Cruze / Malibu)
    "Y3J": "1GC",  # Truck (Silverado)
    "Y3N": "1GC",
    "Y3R": "1G6",  # Cadillac
    # VW / Skoda Russia → German WMI
    "XW8": "WVW",
    "XW9": "TMB",
    # Hyundai / Kia Kazakhstan → Korean WMI
    "Y6D": "KMH",
    "Y6F": "KNA",
    # Toyota / Renault Russia → original WMI
    "X7T": "JT2",
    # Mercedes-Benz non-German plants → German WMI
    "Z9M": "WDD",
    "XUK": "WDD",
    "LBE": "WDD",
    "NMB": "WDB",
    # BMW AvtoTor → German WMI
    "XUF": "WBA",
    "XUH": "WBA",
    # Hyundai/Kia Russia → Korean WMI
    "X7E": "KMH",
    "X7F": "KNA",
    "X7M": "JA4",  # Mitsubishi
    "X7N": "JN1",  # Nissan
}

# Country by WMI prefix (overrides first-char for non-standard cases)
_WMI_COUNTRY: dict[str, str] = {
    "Y3W": "Казахстан", "Y3C": "Казахстан",
    "Y3J": "Казахстан", "Y3N": "Казахстан", "Y3R": "Казахстан",
    "Y6D": "Казахстан", "Y6F": "Казахстан", "Y6T": "Казахстан",
    "XW8": "Россия", "XW9": "Россия",
    "X7L": "Россия", "X7T": "Россия", "X7E": "Россия",
    "X7F": "Россия", "X7N": "Россия", "X7M": "Россия", "X7S": "Россия",
    "XUF": "Россия", "XUH": "Россия", "XUK": "Россия",
    # Z9M: CIS/European Mercedes assembly — показываем страну бренда
    "Z9M": "Германия",
    "Z3N": "Россия",
    # Chinese assembly plants for known brands
    "LBE": "Китай",
    # Turkey
    "NMB": "Турция",
    # USA
    "4JG": "США",
}


def _map_fuel_type(nhtsa_fuel: str) -> str:
    """Map NHTSA FuelTypePrimary to engine_type enum."""
    f = nhtsa_fuel.lower()
    if "diesel" in f:
        return "diesel"
    if "electric" in f:
        return "electric"
    if "hybrid" in f or "plug-in" in f:
        return "hybrid"
    if "natural gas" in f or "cng" in f or "lng" in f or "propane" in f:
        return "gas"
    return "gasoline"


def _map_transmission(nhtsa_trans: str) -> str:
    """Map NHTSA TransmissionStyle to enum."""
    t = nhtsa_trans.lower()
    if "manual" in t and "automated" not in t:
        return "manual"
    if "continuously variable" in t or "cvt" in t:
        return "cvt"
    if "automated" in t or "dual-clutch" in t or "dct" in t:
        return "robot"
    return "automatic"


class VinInfo(TypedDict):
    vin: str
    valid: bool
    year: int | None
    brand: str | None
    model: str | None
    country: str | None
    engine_type: str | None
    transmission: str | None
    body_class: str | None
    image_url: str | None


def _country_from_vin(vin: str, nhtsa_country: str | None = None) -> str | None:
    # 1. NHTSA PlantCountry (if available and not empty)
    if nhtsa_country and nhtsa_country.strip():
        return nhtsa_country.strip()
    wmi = vin[:3].upper()
    # 2. WMI-level override (e.g. Kazakhstan GM plants under Y3W)
    if wmi in _WMI_COUNTRY:
        return _WMI_COUNTRY[wmi]
    # 3. 2-char prefix for ambiguous first chars
    prefix2 = vin[:2].upper()
    two_char = {
        # Nordic — Y1-Y3 = Финляндия, Y4-Y5 = Швеция, Y6 = Норвегия
        "Y1": "Финляндия", "Y2": "Швеция", "Y3": "Финляндия",
        "Y4": "Швеция", "Y5": "Швеция",
        "Y6": "Норвегия",
        "YK": "Швеция", "YS": "Швеция", "YV": "Швеция",
        # UK variants
        "SA": "Великобритания", "SB": "Великобритания",
        "SC": "Великобритания", "SD": "Великобритания",
        # Turkey
        "TA": "Турция", "TB": "Турция", "TC": "Турция",
    }
    if prefix2 in two_char:
        return two_char[prefix2]
    # 4. First-char fallback
    table = {
        "A": "Южная Африка", "B": "Ангола",
        "J": "Япония",
        "K": "Южная Корея",
        "L": "Китай",
        "M": "Индия",
        "S": "Великобритания",
        "T": "Чехия",
        "U": "Румыния",
        "V": "Франция",
        "W": "Германия",
        "X": "Россия",
        "Y": "Швеция/Финляндия",
        "Z": "Италия",
        "1": "США", "4": "США", "5": "США",
        "2": "Канада",
        "3": "Мексика",
        "6": "Австралия",
        "9": "Бразилия",
    }
    return table.get(vin[0].upper())


async def _get_wikipedia_image(
    make: str, model: str | None, year: int | None = None
) -> str | None:
    """Search Wikipedia for a car photo (year-specific when available)."""
    queries: list[str] = []
    if model and year:
        queries.append(f"{make} {model} {year}")  # most specific
    if model:
        queries.append(f"{make} {model} automobile")
    queries.append(f"{make} automobile")
    _UA = "AutoHub/1.0 (vin-decoder; contact@autohub.app)"
    async with httpx.AsyncClient() as client:
        for query in queries:
            try:
                # Step 1: search for the best matching article
                sr = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={"action": "query", "list": "search",
                            "srsearch": query, "format": "json", "srlimit": 1},
                    timeout=4.0,
                    headers={"User-Agent": _UA},
                )
                hits = sr.json().get("query", {}).get("search", [])
                if not hits:
                    continue
                title = hits[0]["title"]
                # Step 2: get the page thumbnail
                pr = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={"action": "query", "titles": title,
                            "prop": "pageimages", "format": "json",
                            "pithumbsize": 500},
                    timeout=4.0,
                    headers={"User-Agent": _UA},
                )
                pages = pr.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    thumb = page.get("thumbnail", {})
                    if thumb.get("source"):
                        return thumb["source"]
            except Exception:
                pass
    return None


def _substitute_vin_wmi(vin: str) -> str | None:
    """Return a VIN with the WMI replaced by its US NHTSA-registered equivalent."""
    new_wmi = _WMI_NHTSA_SUBST.get(vin[:3])
    if not new_wmi:
        return None
    return new_wmi + vin[3:]


async def _fetch_nhtsa(vin: str) -> dict:
    """Call NHTSA vPIC and return a dict with decoded fields (empty if failed)."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json",
                timeout=7.0,
                headers={"User-Agent": "AutoHub/1.0"},
            )
            if resp.status_code != 200:
                return {}
            result = resp.json().get("Results", [{}])[0]
            error_codes = str(result.get("ErrorCode", "")).split(",")
            # Error 7 = manufacturer not in NHTSA — retry with US WMI substitution
            if "7" in error_codes:
                subst = _substitute_vin_wmi(vin)
                if subst:
                    resp2 = await client.get(
                        f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{subst}?format=json",
                        timeout=7.0,
                        headers={"User-Agent": "AutoHub/1.0"},
                    )
                    if resp2.status_code == 200:
                        result = resp2.json().get("Results", [{}])[0]
                if "7" in str(result.get("ErrorCode", "")).split(","):
                    return {}
            out: dict = {}
            make_raw = result.get("Make", "").strip()
            model_raw = result.get("Model", "").strip()
            fuel_raw = result.get("FuelTypePrimary", "").strip()
            trans_raw = result.get("TransmissionStyle", "").strip()
            body_raw = result.get("BodyClass", "").strip()
            plant_country = result.get("PlantCountry", "").strip()
            if make_raw:
                out["brand"] = make_raw.title()
            if model_raw:
                out["model"] = model_raw
            if fuel_raw:
                out["engine_type"] = _map_fuel_type(fuel_raw)
            if trans_raw and trans_raw.lower() not in ("not applicable", ""):
                out["transmission"] = _map_transmission(trans_raw)
            if body_raw and body_raw.lower() != "not applicable":
                out["body_class"] = body_raw
            if plant_country:
                out["plant_country"] = plant_country
            return out
    except Exception:
        return {}


async def decode_vin_extended(vin: str) -> VinInfo:
    """Decode VIN via NHTSA vPIC API (free, no key) with local WMI fallback."""
    vin = vin.strip().upper()
    pattern = r"^[A-HJ-NPR-Z0-9]{17}$"
    valid = bool(re.match(pattern, vin))

    if not valid:
        return VinInfo(
            vin=vin, valid=False, year=None, brand=None, model=None,
            country=None, engine_type=None, transmission=None,
            body_class=None, image_url=None,
        )

    local_brand = _WMI.get(vin[:3])
    year = _decode_year_char(vin[9])

    # Run NHTSA and Wikipedia (using local WMI brand + year) in parallel
    nhtsa_task = asyncio.ensure_future(_fetch_nhtsa(vin))
    wiki_task = asyncio.ensure_future(
        _get_wikipedia_image(local_brand, None, year)
    ) if local_brand else None

    nhtsa = await nhtsa_task

    brand = nhtsa.get("brand") or local_brand
    model = nhtsa.get("model")
    engine_type = nhtsa.get("engine_type")
    transmission = nhtsa.get("transmission")
    body_class = nhtsa.get("body_class")
    plant_country = nhtsa.get("plant_country")

    # year already decoded locally above NHTSA call
    country = _country_from_vin(vin, plant_country)

    # If NHTSA gave us a model, get a year-specific image; else use parallel task
    if model and brand:
        if wiki_task:
            wiki_task.cancel()
        image_url = await _get_wikipedia_image(brand, model, year)
    elif wiki_task:
        image_url = await wiki_task
    elif brand:
        image_url = await _get_wikipedia_image(brand, None, year)
    else:
        image_url = None

    return VinInfo(
        vin=vin,
        valid=True,
        year=year,
        brand=brand,
        model=model,
        country=country,
        engine_type=engine_type,
        transmission=transmission,
        body_class=body_class,
        image_url=image_url,
    )


def decode_vin(vin: str) -> dict:
    """Synchronous local-only VIN decode (legacy, no network)."""
    vin = vin.strip().upper()
    pattern = r"^[A-HJ-NPR-Z0-9]{17}$"
    valid = bool(re.match(pattern, vin))
    if not valid:
        return {"vin": vin, "valid": False, "year": None, "brand": None, "country": None}
    return {
        "vin": vin,
        "valid": True,
        "year": _decode_year_char(vin[9]),
        "brand": _WMI.get(vin[:3]),
        "country": _country_from_vin(vin),
    }

