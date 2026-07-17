import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    REQUEST_TIMEOUT,
    MAX_RETRIES
)


class Session(requests.Session):

    def __init__(self):

        super().__init__()

        self.timeout = REQUEST_TIMEOUT


        retries = Retry(
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
                "POST"
            ]
        )


        adapter = HTTPAdapter(
            max_retries=retries
        )


        self.mount(
            "https://",
            adapter
        )

        self.mount(
            "http://",
            adapter
        )


    def request(
        self,
        method,
        url,
        **kwargs
    ):

        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        return super().request(
            method,
            url,
            **kwargs
        )



session = Session()
