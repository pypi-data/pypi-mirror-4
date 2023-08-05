# encoding=utf-8

"""TeamLab API

See http://api.teamlab.com/
"""

__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "0.1"


import json
import urllib
import urllib2


class Client(object):
    def __init__(self, hostname, verbose=False):
        self.hostname = hostname
        self.verbose = verbose
        self.token = None

    def authenticate(self, login, password):
        resp = self.call_api("/api/1.0/authentication.json", post={
            "userName": str(login),
            "password": str(password),
        })

        self.token = str(resp["token"])

    def get_user_info(self, username="@self"):
        resp = self.call_api("/api/1.0/people/%s.json" % username)
        return resp

    def get_projects(self):
        return self.call_api("/api/1.0/project.json")

    def get_task_list(self):
        resp = self.call_api("/api/1.0/project/task/@self.json")
        return resp

    def call_api(self, uri, post=None, get=None):
        uri = "http://" + self.hostname + uri

        if post is None:
            data = None
        else:
            data = urllib.urlencode(post)

        if get is not None:
            uri += "?" + urllib.urlencode(get)

        self.log("Fetching %s" % uri)

        req = urllib2.Request(uri, data)
        if self.token is not None:
            req.add_header("Authorization", self.token)
        req.add_header("Accept", "application/json")

        res = urllib2.urlopen(req)
        if res.getcode() >= 400:
            raise Exception("Error accessing the API: %s" % res.read())

        response = res.read()

        return json.loads(response)["response"]

    def log(self, message):
        if self.verbose:
            print message


__all__ = [
    "Client",
]
