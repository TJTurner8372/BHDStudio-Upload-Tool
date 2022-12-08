import re


def edition_title_extractor(name_to_check):
    """function to check edition and get title of movie only"""
    check_for_edition_lst = re.findall(
        "director(?:'s)?(?:.cut)?|extended(?:.cut)?|theatrical(?:.cut)?|unrated",
        name_to_check,
        flags=re.IGNORECASE,
    )

    extracted_editions = ""
    movie_input_filtered = name_to_check

    # extracted edition(s)
    if check_for_edition_lst:
        if len(check_for_edition_lst) == 1:
            extracted_editions = check_for_edition_lst[0]
        elif len(check_for_edition_lst) > 1:
            for edition in check_for_edition_lst:
                extracted_editions = extracted_editions + edition + " "
            # strip away extra white space on the right side and remove periods
            extracted_editions = extracted_editions.rstrip().replace(".", " ")

    # clean up edition names
    if any(
        re.findall(
            r"director|extended|theatrical|unrated", extracted_editions, re.IGNORECASE
        )
    ):
        extracted_editions = re.sub(
            r"director(?:'s)?(?:.cut)?",
            "Director's Cut",
            extracted_editions,
            flags=re.IGNORECASE,
        )
        extracted_editions = re.sub(
            r"extended(?:.cut)?",
            "Extended Cut",
            extracted_editions,
            flags=re.IGNORECASE,
        )
        extracted_editions = re.sub(
            r"theatrical(?:.cut)?",
            "Theatrical Cut",
            extracted_editions,
            flags=re.IGNORECASE,
        )
        extracted_editions = re.sub(
            r"unrated",
            "Unrated",
            extracted_editions,
            flags=re.IGNORECASE,
        )

    # if edition is detected remove it from the name
    if extracted_editions != "":
        for x in check_for_edition_lst:
            movie_input_filtered = re.sub(x, "", movie_input_filtered)

    # detect as much extra stuff from title as possible
    remove_extra_stuff = re.findall(
        r"\brepack\b|\b2160p\b|\b1080p\b|\bdts.?hd.?ma\b|\btrue.?hd\b|\batmos\b|\bhybrid\b"
        r"|\bavc\b|\bvc.?.?\b|\b5\.1\b|\b7\.1\b|\b2\.0\b|\b1\.0\b|\bremux\b|\buhd\b|\bdv\b"
        r"|\bflac\b|\bdovi\b|\b.?pcm\b|\bmpeg.?.?\b|\bhevc\b|\b1080i\b|\bproper\b",
        movie_input_filtered,
        flags=re.IGNORECASE,
    )

    # if extra stuff is detected loop through and remove it from the string
    if remove_extra_stuff:
        for rem in remove_extra_stuff:
            movie_input_filtered = re.sub(rem, "", movie_input_filtered)

    # change all variants of bluray to a basic bluray string
    movie_input_filtered = re.sub(
        r"blu.?ray", "bluray", movie_input_filtered, flags=re.IGNORECASE
    )

    # remove all non word characters
    movie_input_filtered = re.sub(r"\W", ".", movie_input_filtered)

    # remove all spaces
    movie_input_filtered = re.sub(r"\s", ".", movie_input_filtered)

    # remove extra '.'s
    movie_input_filtered = re.sub(r"\.{2,}", ".", movie_input_filtered)

    # attempt to get only the movie title year
    collect_year = re.findall(r"(?<!\d)\d{4}(?!\d)", movie_input_filtered)

    # if any 4 digits are detected in the string
    if collect_year:
        # get only the last set of digits
        search_index = movie_input_filtered.find(str(collect_year[-1]))
        movie_input_filtered = movie_input_filtered[: search_index + 4]

    # search for bluray string and get everything to the left of it
    elif "bluray" in movie_input_filtered:
        search_index = movie_input_filtered.find("bluray")
        movie_input_filtered = movie_input_filtered[:search_index]

    # split string
    movie_input_filtered = movie_input_filtered.split(".")

    # rejoin string and strip off any excess white space
    movie_input_filtered = " ".join(movie_input_filtered).strip()

    return extracted_editions, movie_input_filtered
