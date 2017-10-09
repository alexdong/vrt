import logging
import time
from typing import List, Dict

import requests

from mtr.local_conf import BROWSER_STACK_ACCESS_KEY, SERVER

logger = logging.getLogger(__name__)


class InvalidRequestError(Exception):
    pass


def submit_request(path: str, targets: List[Dict]) -> str:
    """
    Request a set of screenshots to be generated for the specified `url` on `targets` devices.

    We first send a POST request to `POST /screenshots`, which will send back a `job_id`;

    :param path: path to the web page we are testing. For example: `"/products/collage-posters"`
    :param targets: a list of target OS and browser "descriptors". For example: [
            {
                "os": "Windows",
                "os_version": "XP",
                "browser": "ie",
                "browser_version": "7.0"
            },
            {
                "os": "ios",
                "os_version": "6.0",
                "device": "iPhone 4S (6.0)"
            }
        ]
    :return: the job_id against which we can poll to download images when the
        screen shots are ready.
    """
    # Request the screen shots
    request_payload = {"url": SERVER + path, "browsers": targets}
    headers = {'content-type': 'application/json', 'Accept': 'application/json'}
    logger.debug("Sending screen shot requests: %s", request_payload)
    r = requests.post('https://www.browserstack.com/screenshots',
                      json=request_payload,
                      headers=headers,
                      auth=BROWSER_STACK_ACCESS_KEY)
    if r.status_code != 200:
        logger.error("BrowserStack returns error code: %d", r.status_code)
        if r.status_code == 422 and 'job_id' in r.json():
            job_id = r.json()['job_id']
            logger.info("BrowserStack returns an existing job id %s, switching to it", job_id)
        else:
            logger.error("invalid request: %s", r.content)
            raise InvalidRequestError("BrowserStack returns status_code: %d", r.status_code)

    # Pull out the job id and start polling
    job_id = r.json()['job_id']
    logger.info("BrowserStack returns job id: %d", job_id)
    return job_id


def wait_and_fetch_all_urls(job_id: str) -> List[str]:
    """
    Poll to see whether the job is ready every 2 seconds.
    When all the screenshots are ready, pull the `full_url` out and
    return them.

    :param job_id: the screen shot job returned by BrowserStack.
    :return: List of urls to download
    """
    # Get grab all the links
    while True:
        r = requests.get('https://www.browserstack.com/screenshots/' + job_id + '.json', auth=BROWSER_STACK_ACCESS_KEY)
        logger.debug("Job returns: %d", r.status_code)
        logger.debug("    payload: %s", r.content)

        payload = r.json()
        if 'done' == payload['state']:
            return [screenshot['image_url'] for screenshot in payload['screenshots']]
        else:
            time.sleep(2)


if __name__ == "__main__":
    # print(submit_request("/products/collage-posters", [{
    #         "os": "android",
    #         "os_version": "5.0",
    #         "browser": "Android Browser",
    #         "device": "Google Nexus 6",
    #         "browser_version": "",
    #     }]))
    print(wait_and_fetch_all_urls('fdd01e6683e0474ede370b753f870542f364f8ba'))
