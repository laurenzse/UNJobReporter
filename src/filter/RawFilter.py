from functools import cache

from cachepy import FileCache
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pycountry_convert as pc

from src.data.Job import UNJobStub

# create cache-to-file decorator to avoid unnecessary API calls for geocoding
filecache = FileCache('africa_lookups.dat')


def job_is_in_africa(job: UNJobStub) -> bool:
    return city_country_in_africa(job.cities_countries)

@filecache
def city_country_in_africa(cities_countries: str) -> bool:
    # check if empty string passed
    if cities_countries == "":
        return False

    locator = Nominatim(user_agent="UNJobReporter")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    location = geocode(cities_countries, addressdetails=True)

    if location is None:
        return False

    # extract country code
    address = location.raw["address"]
    country_code = address["country_code"].upper()

    # get continent code from country code
    try:
        continent_code = pc.country_alpha2_to_continent_code(country_code)
    except KeyError:
        return False

    return continent_code == "AF"


def filter_jobs(jobs: list[UNJobStub]) -> (list[UNJobStub], list[UNJobStub]):
    pass_jobs = []
    deny_jobs = []

    for job in jobs:
        if job_is_in_africa(job):
            deny_jobs.append(job)
        else:
            pass_jobs.append(job)

    return pass_jobs, deny_jobs
