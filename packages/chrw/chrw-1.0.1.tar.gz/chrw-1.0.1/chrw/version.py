__version__ = "1.0.1"

# Just incase they don't have requests installed yet.
codes = None

try:
    import requests.structures

    _codes = {
        -1:("not_post",),
        0: ("ok", "good", "success",),
        1: ("api_disabled", "disabled",),
        2: ("captcha_incorrect",),
        3: ("url_too_long",),
        4: ("url_invalid",),
        5: ("custom_url_invalid",),
        6: ("partial_form_data",),
        7: ("no_such_key",),
        8: ("no_such_url",),
        9: ("deletion_invalid",),
        10:("deletion_failed",)
    }

    codes = requests.structures.LookupDict(name="reply_codes")
    for (code, titles) in list(_codes.items()):
        for title in titles:
            setattr(codes, title, code)
            setattr(codes, title.upper(), code)
except ImportError:
    pass