import apysigner
import constants
import re


def check_signature(signature, private_key, full_path, payload):
    """
    Checks signature received and verifies that we are able to re-create
    it from the private key, path, and payload given.

    :param signature:
        Signature received from request.
    :param private_key:
        Base 64, url encoded private key.
    :full_path:
        Full path of request, including GET query string (excluding host)
    :payload:
        The request.POST data if present. None if not.

    :returns:
        Boolean of whether signature matched or not.
    """
    url_to_check = _strip_signature_from_url(signature, full_path)
    computed_signature = apysigner.get_signature(private_key, url_to_check, payload)
    return constant_time_compare(signature, computed_signature)


def _strip_signature_from_url(signature, url_path):
    signature_qs = r"(\?|&)?{0}={1}$".format(constants.SIGNATURE_PARAM_NAME, signature)
    clean_url = re.sub(signature_qs, '', url_path, count=1)
    return clean_url


def constant_time_compare(val1, val2):
    """
    **This code was taken from the django 1.4.x codebase along with the test code**
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0