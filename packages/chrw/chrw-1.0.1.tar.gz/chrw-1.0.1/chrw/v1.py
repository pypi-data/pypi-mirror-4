# -*- coding: utf-8 -*-

import chrw
import chrw.exceptions

import requests

import logging
import datetime
import time
import json
import functools

def rate_limited(max_per_second):
    """ Sort of based off of an answer about
        rate limiting on Stack Overflow.

        Definitely **not** thread safe, so
        don't even think about it, buddy.
    """
    import datetime
    min_request_time = datetime.timedelta(seconds=max_per_second)
    last_time_called = [None]
    def decorate(func):
        def rate_limited_function(*args, **kwargs):
            if last_time_called[0]:
                delta = datetime.datetime.now() - last_time_called[0]
                if delta < datetime.timedelta.min:
                    raise chrw.exceptions.TimeIsBackToFront, "Call the Doc!"
                elif delta < min_request_time:
                    msg = "Last request was {0}, should be at least {1}".format(
                        delta, min_request_time
                    )
                    raise chrw.exceptions.RequestRateTooHigh, msg
            ret = func(*args, **kwargs)
            last_time_called[0] = datetime.datetime.now()
            return ret
        return functools.update_wrapper(rate_limited_function, func)
    return decorate

class wrapper:
    """ A wrapper to the chr url shortening service APIv1.

        Obeys the 1r/s rule with rate limiting, so you
        can't accidentally hammer the API without knowing.

        View online @ http://pypi.python.org/pypi/chrw
    """

    def __init__(self, url, api_key, https=False, user_agent=None, require_200=True):
        """
            Pull together the various settings of the wrapper.

            :param url: the chr instance url, minus trailing slash (e.g. chr.so)
            :type url: str
            :param api_key: your API key, as written in the database
            :type api_key: str
            :param https: are we using https to access this instance?
            :type https: bool
            :param user_agent: what user agent will we use to access the API?
            :type user_agent: str or None
            :param require_200: should we raise an exception on a non-200OK reply?
            :type require_200: bool
        """
        self.url = url
        self.base = url + "/api/v1"
        self.api_key = api_key
        self.https = https
        self.user_agent = user_agent or "chrw/{0} (@https://github.com/plausibility/chrw)".format(chrw.__version__)
        self.require_200 = require_200
        self.reply = {}
        self.post = {}

    @property
    def schema(self):
        return 'https'if self.https else 'http'

    def shorten(self, url, custom=None, give_delete=True):
        """
            Sends a URL shorten request to the API.

            :param url: the URL to shrink
            :type url: str
            :param custom: a custom URL to request
            :type custom: str
            :param give_delete: would we like a deletion key to be returned?
            :type give_delete: bool
            :return: the API response JSON dict
            :rtype: dict
        """
        data = self.fetch("/submit", {
            "long": url,
            "short": custom if custom else "",
            "delete": "true" if give_delete else ""
        })

        return data
        
    def stats(self, url):
        """
            Request the stats for a given URL.

            :param url: the shortened url to get stats for
            :type url: str
            :return: the statistics JSON dict for the URL
            :rtype: dict
        """
        data = self.fetch("/stats", {
            "short": url
        })

        return data

    def delete(self, url, code):
        """
            Request a URL be deleted.

            This will only work if you supply the valid deletion code.

            :param url: the shortened url to delete
            :type url: str
            :param code: the deletion code given to you on URL shorten
            :type code: str
            :return: the deletion request's reply dict
            :rtype: dict
        """
        data = self.fetch("/delete", {
            "short": url,
            "delete": code
        })

        return data

    def expand(self, url):
        """
            This will simply expand a shortened url (e.g, ``+foo``)
            to the larger url (e.g, ``http://foo.example.com/bar``)

            :param url: the shortened URL to expand
            :type url: str
            :return: the expansion request reply dict
            :rtype: dict
        """
        data = self.fetch("/expand", {
            "short": url
        })

        return data

    @rate_limited(1)
    def fetch(self, url, pdata, store_to_self=True):
        """
            This does the bulk of the work for the wrapper.

            It will send a POST request, to the API URL, with
            all required data, as well as the api_key given,
            and will handle various replies, raising exceptions
            as required.

            :param url: the url segment to POST to (unbuilt url, e.g., /submit, /expand)
            :type url: str
            :param pdata: a dictionary of data to POST
            :type pdata: dict
            :param store_to_self: should we store the reply (if any) to self.reply?
            :type store_to_self: bool
            :return: the API reply data
            :rtype: dict
            :raises: chrw.exceptions.ApiDisabled,
                     chrw.exceptions.InvalidApiKey,
                     chrw.exceptions.PartialFormData,
                     chrw.exceptions.NonZeroException
        """
        url = self.schema + '://' + self.base + url
        post = dict(pdata.items() + {
            "api_key": self.api_key  
        }.items())
        self.post = post
        res = requests.post(url, post, headers={"User-Agent": self.user_agent})
        if self.require_200 and res.status_code != requests.codes.ok:
            raise chrw.exceptions.RequestFailed, "Got HTTP reply {0}, needed {1}".format(res.status_code, requests.codes.ok)
        
        if not res.json:
            raise chrw.exceptions.InvalidDataReturned, "Invalid JSON data was returned"

        if store_to_self:
            self.reply = res.json

        if res.json["enum"] == chrw.codes.api_disabled:
            raise chrw.exceptions.ApiDisabled, res.json["message"]
        elif res.json["enum"] == chrw.codes.no_such_key:
            raise chrw.exceptions.InvalidApiKey, res.json["message"]
        elif res.json["enum"] == chrw.codes.partial_form_data:
            raise chrw.exceptions.PartialFormData, res.json["message"]
        elif res.json["enum"] != chrw.codes.success:
            __ = "Non-zero reply {0}: {1}".format(res.json["enum"], res.json["message"])
            raise chrw.exceptions.NonZeroReply, __

        return res.json