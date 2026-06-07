import requests
from functools import lru_cache

_TOKEN = "adressevaelger123"  # TODO December 2026: check if KDS has launched user management and replace this token
_BASE_URL = "https://adressevaelger.dk"


@lru_cache(maxsize=1)
def _get_transformer():
    from pyproj import Transformer

    return Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)


def etrs89_to_wgs84(x, y):
    lon, lat = _get_transformer().transform(x, y)
    return lat, lon


def get_address_by_id(id_lokalid):
    response = requests.get(
        f"{_BASE_URL}/adresser/{id_lokalid}",
        params={"token": _TOKEN},
        timeout=10,
    )
    if response.status_code != 200:
        return None
    return response.json()


def search_address(text):
    """Search for an address by text. Returns the id_lokalid of the first adresse result."""
    response = requests.get(
        f"{_BASE_URL}/adresser/soeg",
        params={"tekst": text, "token": _TOKEN},
        timeout=10,
    )
    if response.status_code != 200:
        return None
    for result in response.json().get("fund", []):
        if result.get("type") == "adresse":
            return result["id"]
    return None


def apply_address_data(obj, parsed):
    """Apply parsed address fields to any model with the standard address fields."""
    obj.streetname = parsed["streetname"]
    obj.housenumber = parsed["housenumber"]
    obj.floor = parsed["floor"]
    obj.door = parsed["door"]
    obj.placename = parsed["placename"]
    obj.city = parsed["city"]
    obj.zipcode = parsed["zipcode"]
    obj.region = parsed["region"]
    obj.dawa_id = parsed["id_lokalid"]
    if parsed["latitude"] is not None:
        obj.latitude = parsed["latitude"]
        obj.longitude = parsed["longitude"]


def parse_address_data(data):
    """
    Extract a normalised dict from an Adressevælger /adresser/{id} response.
    Looks up region and municipality name from the Municipality table.
    """
    from members.models.municipality import Municipality

    adr = data["adresse"]
    husnummer = adr["husnummer"]
    kommunedel = husnummer.get("navngivenvejkommunedel") or {}
    suppl = husnummer.get("supplerendebynavn")
    koordinater = (husnummer.get("adgangspunkt") or {}).get("koordinater") or {}

    kommunekode = kommunedel.get("kommune", "")
    municipality_obj = None
    region = ""
    municipality_name = ""
    try:
        municipality_obj = Municipality.objects.get(dawa_id=kommunekode)
        region = municipality_obj.region
        municipality_name = municipality_obj.name
    except Municipality.DoesNotExist:
        pass

    latitude = longitude = None
    x = koordinater.get("x")
    y = koordinater.get("y")
    if x is not None and y is not None:
        latitude, longitude = etrs89_to_wgs84(x, y)

    return {
        "id_lokalid": adr["id_lokalid"],
        "streetname": husnummer.get("vejnavn", ""),
        "housenumber": husnummer.get("husnummertekst", ""),
        "floor": adr.get("etagebetegnelse") or "",
        "door": adr.get("doerbetegnelse") or "",
        "placename": (suppl.get("navn") or "") if suppl else "",
        "zipcode": husnummer["postnummer"]["postnr"],
        "city": husnummer["postnummer"]["navn"],
        "municipality_obj": municipality_obj,
        "municipality_name": municipality_name,
        "region": region,
        "latitude": latitude,
        "longitude": longitude,
    }
