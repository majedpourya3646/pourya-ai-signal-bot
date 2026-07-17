import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Session(requests.Session):
    def __init__(self):
        super().__init__()

        self.timeout = 15

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retries)

        self.mount("https://", adapter)
        self.mount("http://", adapter)


session = Session()
