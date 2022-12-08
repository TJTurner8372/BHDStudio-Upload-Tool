import requests


def dupe_check(api_key: str, title: str, page: int = 0, resolution: str = None):
    """
    Checks BeyondHD for duplicate titles.

    :param api_key: API key from BeyondHD.
    :param title: Title of the movie to check.
    :param page: This returns 100 results by default, if for some reason there is more send a page number.
    :param resolution: Filters results by resolution. If left as None then it will return all results.
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
    try:
        run_check = requests.post(
            "https://beyond-hd.me/api/torrents/" + api_key, params=payload, timeout=60
        )
    except requests.exceptions.ConnectionError:
        return "Connection Error"

    # release dict
    release_dict = {}

    # if all 3 checks are successful, return all results in a list.
    if run_check.ok and run_check.json()["status_code"] and run_check.json()["success"]:
        for x in run_check.json()["results"]:
            if resolution:
                if resolution in str(x):
                    release_dict.update({x["name"]: x})
            elif not resolution:
                release_dict.update({x["name"]: x})

    return release_dict


if __name__ == "__main__":
    wow = dupe_check(api_key="KEYHERE", title="Gone In 60 Seconds")

    if wow and wow != "Connection Error":
        print(wow)
    else:
        print("Connection Error")
