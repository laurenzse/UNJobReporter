from cachepy import FileCache
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pycountry_convert as pc

from src.data.Job import UNJobStub

# create cache-to-file decorator to avoid unnecessary API calls for geocoding
filecache = FileCache("continent_file_cache.dat")


@filecache
def get_continent_code_from_cities_countries(cities_countries: str) -> str:
    # check if empty string passed
    if cities_countries == "":
        return ""

    locator = Nominatim(user_agent="UNJobReporter")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    location = geocode(cities_countries, addressdetails=True)

    if location is None:
        return ""

    # extract country code
    address = location.raw["address"]
    country_code = address["country_code"].upper()

    # get continent code from country code
    try:
        continent_code = pc.country_alpha2_to_continent_code(country_code)
    except KeyError:
        return ""

    return continent_code


def filter_jobs(
    jobs: list[UNJobStub], config: dict
) -> (list[UNJobStub], list[UNJobStub]):
    filter_out_continent_codes = config["continent_filter"]

    pass_jobs = []
    deny_jobs = []

    for job in jobs:
        if (
            get_continent_code_from_cities_countries(job.cities_countries)
            in filter_out_continent_codes
        ):
            deny_jobs.append(job)
        else:
            pass_jobs.append(job)

    return pass_jobs, deny_jobs
