import json
from haversine import haversine, Unit

# from geopy.geocoders import Nominatim
from app.models.ivf_centers import IVF_Center
import requests
from beanie.operators import RegEx


# geolocator = Nominatim(user_agent="clinic_locator")


async def find_coordinates(postal_code: str):
    doc = await IVF_Center.find_one(IVF_Center.Pincode == int(postal_code))
    return doc


async def find_coordinates_by_city_name(city_name: str):
    city_name = city_name.strip().upper()
    doc = await IVF_Center.find_one(
        IVF_Center.District == city_name,
        IVF_Center.Latitude != 0,
        IVF_Center.Longitude != 0,
    )
    if doc is None:
        exact_regex = f"^{city_name}$"  # <-- exact match
        doc = await IVF_Center.find_one(
            {
                "$and": [
                    RegEx(
                        IVF_Center.Tehsil, exact_regex, options="i"
                    ),  # case-insensitive EXTACT match
                    {"Latitude": {"$ne": 0}},
                    {"Longitude": {"$ne": 0}},
                ]
            }
        )

        if doc is None:
            city_name = city_name.lower().capitalize()
            doc = await IVF_Center.find_one(
                {
                    "$and": [
                        RegEx(
                            IVF_Center.Tehsil, city_name, options="i"
                        ),  # case-insensitive EXTACT match
                        {"Latitude": {"$ne": 0}},
                        {"Longitude": {"$ne": 0}},
                    ]
                }
            )
    return doc


async def find_pincode_by_city_name(city_name: str):
    city_name = city_name.strip().upper()
    doc = await IVF_Center.find_one(IVF_Center.District == city_name)
    if doc is None:
        exact_regex = f"^{city_name}$"  # <-- exact match
        doc = await IVF_Center.find_one(
            {
                "$and": [
                    RegEx(
                        IVF_Center.Tehsil, exact_regex, options="i"
                    ),  # case-insensitive EXTACT match
                    {"Latitude": {"$ne": 0}},
                    {"Longitude": {"$ne": 0}},
                ]
            }
        )

        if doc is None:
            city_name = city_name.lower().capitalize()
            doc = await IVF_Center.find_one(
                {
                    "$and": [
                        RegEx(
                            IVF_Center.Tehsil, city_name, options="i"
                        ),  # case-insensitive EXTACT match
                        {"Latitude": {"$ne": 0}},
                        {"Longitude": {"$ne": 0}},
                    ]
                }
            )
    return doc.Pincode


# def get_coordinates(query):
#     """Geocode a query like postal code, city or address"""
#     try:
#         location = geolocator.geocode(query)
#         if location:
#             return (location.latitude, location.longitude)
#     except:
#         pass
#     return None


async def find_nearest_by_postal(postal_code, category, top_n=3):

    # with open("app/datasets/new_ivf_clinic.json", "r", encoding="utf-8") as f:
    #     clinics = json.load(f)
    url = "https://findmyiivfclinic.indiraivf.in/api/get-clinics"
    response = requests.get(url, verify=False)
    response.raise_for_status()  # raises error if request fails
    clinics = response.json()
    if category == "pincode":
        base_clinic = next(
            (c for c in clinics if str(c.get("Postal")) == str(postal_code)), None
        )

        if (
            base_clinic
            and base_clinic.get("Latitude") is not None
            and base_clinic.get("Longitude") is not None
        ):
            base_loc = (base_clinic["Latitude"], base_clinic["Longitude"])
        else:
            doc = await find_coordinates(postal_code)
            if doc and doc.Latitude and doc.Longitude:
                base_loc = (doc.Latitude, doc.Longitude)
                # base_loc = get_coordinates(postal_code)
                if not base_loc:
                    return []
            else:
                return []
    else:
        doc = await find_coordinates_by_city_name(postal_code)
        if doc and doc.Latitude and doc.Longitude:
            base_loc = (doc.Latitude, doc.Longitude)
            if not base_loc:
                return []
        else:
            return []

    results = []
    seen_names = set()
    for clinic in clinics:
        # lat, lon = clinic.get("latitude"), clinic.get("longitude")
        lat = float(clinic.get("latitude"))
        lon = float(clinic.get("longitude"))

        name = clinic.get("clinic_name")
        address = clinic.get("address")
        if lat is None or lon is None or address in seen_names:
            continue  # skip null coordinates or duplicates
        dist = haversine(base_loc, (lat, lon), unit=Unit.KILOMETERS)
        results.append(
            {
                "Clinic Name": name,
                "City": clinic.get("district"),
                "State": clinic.get("state"),
                "Address": clinic.get("address"),
                "Postal": clinic.get("pincode"),
                "Distance_km": round(dist, 2),
            }
        )
        seen_names.add(address)  # mark this clinic as added

    # Sort and return top_n nearest
    results = sorted(results, key=lambda x: x["Distance_km"])[:top_n]
    for result in results:
        url = f"https://www.google.com/maps/dir/{base_loc[0]},{base_loc[1]}/{result['Clinic Name']}"
        result["url"] = url
    return results
