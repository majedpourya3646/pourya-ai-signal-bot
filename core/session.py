import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    REQUEST_TIMEOUT,
    MAX_RETRIES
)


def create_session():

    session = requests.Session()

    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[
            429,
            500,
            502,
            503,
            504
        ],
        allowed_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE"
        ]
    )

    adapter = HTTPAdapter(
        max_retries=retry
    )

    session.mount(
        "https://",
        adapter
    )

    session.mount(
        "http://",
        adapter
    )

    session.request_timeout = REQUEST_TIMEOUT

    return session


session = create_session()
