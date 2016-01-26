# !/usr/bin/python

""" HTTP Utilities """
import urllib
import urllib2
from urllib2 import HTTPError
import json

class NetUtil:
    @staticmethod
    def http_request(host, path, post_data=None, header_map={}, parameters_map={}):
        request_url = host + path

        if parameters_map:
            param_data = urllib2.urlencode(parameters_map)
            request_url = request_url + "?" + param_data

        print "Request : " + request_url
        request = urllib2.Request(url=request_url,
                                  data=post_data,
                                  headers=header_map)
        try:
            response = ""
            response = urllib2.urlopen(request)
	
            # Raise exception if the network request has failed
            if response.code is not 200:
                print response.read()
                raise
        except HTTPError as error:
            print error.read()
            raise error

        return response.read()

    @staticmethod
    def http_get(host, path, header_map={}, parameters_map={}):
        return NetUtil.http_request(host,
                                    path,
                                    header_map=header_map,
                                    parameters_map=parameters_map)

    @staticmethod
    def http_post(host, path, post_data, header_map={}):
        return NetUtil.http_request(host,
                                    path,
                                    post_data=post_data,
                                    header_map=header_map)

print NetUtil.http_get("http://www.google.com/", "robots.txt", {"User-Agent": "Safari"})
print NetUtil.http_post(host="http://httpbin.org/",
                        path="post",
                        post_data="fdasffsvvvvfdfsfsaf",
                        header_map={"Content-Type": "application/json"})
print NetUtil.http_post(host="https://quark-app-dev.geo.apple.com/",
                        path="api/2.0/repository",
                        post_data='{"user":"rbrown8", "repo_type":"kittyhawk"}',
			header_map={"Content-Type": "application/json"})
