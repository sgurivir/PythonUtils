# !/usr/bin/python

""" HTTP Utilities """
import urllib
import urllib2
from urllib2 import HTTPError
import json

class NetUtil:
    @staticmethod
    def http_delete(host, path, delete_data, header_map={}, parameters_map=None):
        """
        Sends a HTTP DELETE request and returns the response
        Raises exception if HTTP 200 is not received in response

        :param host: host address
        :param path: path in URL
        :param data: post data in message
        :param post_data: HTTP request headers to send in GET request

        e.g. http_get("http://www.apple.com/", "robots.txt", {"User-Agent": "Safari"})
        """

        class RequestWithMethod(urllib2.Request):
            def __init__(self, method, *args, **kwargs):
                self._method = method
                urllib2.Request.__init__(self, *args, **kwargs)

            def get_method(self):
                return self._method

        request_url = host + path

        if parameters_map:
            param_data = urllib2.urlencode(parameters_map)
            request_url = request_url + "?" + param_data

        request = RequestWithMethod("DELETE",
                                  url=request_url,
                                  data=delete_data,
                                  headers=header_map)
        try:
            response = urllib2.urlopen(request)
        except HTTPError as error:
            print("HTTP response error")
            print(error.read())
            raise error

        return response.read()

print NetUtil.http_delete(host="http://quark-app-dev.geo.apple.com",
      	                  path="/api/2.0/repository/" + "e1baf3b0-525d-11e5-803b-637e28c04f96",
	        	  delete_data="")
