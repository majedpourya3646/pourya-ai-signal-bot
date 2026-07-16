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

        ],

        raise_on_status=False

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


    # Default timeout
    session.timeout = REQUEST_TIMEOUT


    # Headers عمومی
    session.headers.update({

        "User-Agent": "Pourya-Trader-AI/1.0",

        "Accept": "application/json"

    })


    return session



# Global Session

session = create_session()
