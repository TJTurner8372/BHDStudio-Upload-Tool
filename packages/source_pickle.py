import pickle


def get_saved_source_info(pickle_location):
    """
    Used to get information from pickle.dat file

    :param pickle_location: Location of the pickle.dat file.
    :return: Information extracted form pickle.dat file.
    """
    with open(pickle_location, "rb") as pf:
        return pickle.load(pf)


def save_source_info(pickle_location, source_file_information):
    """
    Used to save information to pickle.dat file

    :param pickle_location: Location of the pickle.dat file.
    :param source_file_information: Information extracted from the source file.
    :return: None
    """
    with open(pickle_location, "wb") as pf:
        pickle.dump(source_file_information, pf, protocol=pickle.HIGHEST_PROTOCOL)
