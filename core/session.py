# core/session.py

import requests

from requests.adapters import HTTPAdapter

from urllib3.util.retry import Retry

from core.logger import logger

from config import (
    MAX_RETRIES,
    REQUEST_TIMEOUT
)








def create_session():

    try:


        session = requests.Session()





        retry_strategy = Retry(

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

            max_retries=retry_strategy

        )





        session.mount(

            "https://",

            adapter

        )



        session.mount(

            "http://",

            adapter

        )





        return session



    except Exception as e:


        logger.exception(e)


        return requests.Session()










session = create_session()







def request(
    method,
    url,
    **kwargs
):

    try:


        kwargs.setdefault(

            "timeout",

            REQUEST_TIMEOUT

        )



        response = session.request(

            method,

            url,

            **kwargs

        )



        return response



    except Exception as e:


        logger.exception(e)


        return None
