import requests


def dupe_check(api_key: str, title: str, page: int = 0):
    """
    Checks BeyondHD for duplicate titles.

    :param api_key: API key from BeyondHD.
    :param title: Title of the movie to check.
    :param page: This returns 100 results by default, if for some reason there is more send a page number.
    :return: List with a dictionary in it of the first 100 results.
    """

    # payload to send to BeyondHD site API
    payload = {
        "action": "search",
        "search": title,
        "stream": 1,
        "internal": 1,
        "groups": "BHDStudio",
    }

    # if a page is specified add it to the payload
    if page >= 1:
        payload.update({"page": int(page)})

    # post to send the payload
    run_check = requests.post(
        "https://beyond-hd.me/api/torrents/" + api_key, params=payload
    )

    # if all 3 requirements are correctly returned, continue
    if run_check.ok and run_check.json()["status_code"] and run_check.json()["success"]:
        return [x for x in run_check.json()["results"]]
