#!/usr/local/bin/python3

import json
import os
import math
from discord_webhook import DiscordWebhook

########
# Install Python PIP3
# sudo apt-get -y install python3-pip
# install Discord-Webhook module
# % pip3 install discord-webhook
#
# CRONTAB
# run script every 3 hours
# 0 */3 * * * cd ~/mnds; python3 mnds.py >> cron.log 2>&1
########


class mnds:
    """co8/mnds - Mysterium Node Discord Status"""

    _discord_url = "https://discord.com/api/webhooks/900191773463285781/JImKIdRo2UXqDvRp5QtZplsABYGn8ndWorokgsaalq1rF_IUi51mpCWYtAvDDtmJf7UW"
    _curl_url = "curl -s http://localhost:4050/"

    def get_services(self):
        # return os.popen(self._curl_url + "services").read()
        output = [
            {
                "provider_id": "0xb7ae946600e80eca0d50869ea06fc8c0b53d304c",
                "type": "wireguard",
                "status": "Running",
                "proposal": {
                    "price": {
                        "currency": "MYSTT",
                        "per_hour": 114042996843727,
                        "per_gib": 228085993687453980,
                    },
                },
            },
        ]
        return output[0]

    def get_stats(self):
        # output = os.popen(self._curl_url + "sessions/stats-aggregated").read()
        output = {
            "stats": {
                "count": 1488,
                "count_consumers": 717,
                "sum_bytes_received": 149290392763,
                "sum_bytes_sent": 14802564239,
                "sum_duration": 15173349,
                "sum_tokens": 35793641406550526275,
            }
        }
        output["stats"]["earnings"] = str(
            self.nice_myst_amount(output["stats"]["sum_tokens"], 4)
        )
        return output["stats"]

    def get_healthcheck(self):
        # return os.popen(self._curl_url + "healthcheck").read()
        output = {
            "uptime": "4h39m49.968940602s",
            "version": "0.67.2",
        }
        return output

    def get_version(self):
        healthcheck = self.get_healthcheck()
        return healthcheck["version"]

    def services_mnds(self):
        services = self.get_services()
        per_hour_places = 6
        per_gib_places = 4
        return {
            # "provider_id": services["provider_id"],
            "provider_id": services["provider_id"][0:7],  # first 7 char of Node ID
            "status": services["status"].upper(),
            "type": services["type"].upper(),
            "currency": services["proposal"]["price"]["currency"],
            # "per_hour": services["proposal"]["price"]["per_hour"],
            "per_hour": str(
                self.nice_myst_amount(
                    services["proposal"]["price"]["per_hour"], per_hour_places
                )
            ),
            # "per_gib": services["proposal"]["price"]["per_gib"],
            "per_gib": str(
                self.nice_myst_amount(
                    services["proposal"]["price"]["per_gib"], per_gib_places
                )
            ),
        }

    def truncate(self, f, n):
        return math.floor(f * 10 ** n) / 10 ** n

    def nice_myst_amount(self, amt, places):
        niceNum = 0.000000000000000001
        return self.truncate(amt * niceNum, places)

    def discord_message(self):
        services = self.services_mnds()
        stats = self.get_stats()
        version = self.get_version()
        # print(type(stats["earnings"]))
        # exit()
        output = (
            "Node: **"
            + services["provider_id"]
            # + "** Status: **"
            + "** / **"
            + services["status"]
            # + "** Earnings: **"
            + "** / **"
            + stats["earnings"]
            + " MYST**"
            + "\n"
            + "Version: **"
            + version
            + "**  / "
            + "Sessions: "
            + str(stats["count"])
            # + " / "
            # + str(stats["count_consumers"])
            + "\n"
            # + "Service: "
            + services["type"]
            + " `"
            + services["per_hour"]
            + "`/hr + "
            + services["per_gib"]
            + "/GiB"
            # + services["currency"]
        )
        return output

    ##############################
    def __init__(self):
        """init"""
        message = self.discord_message()
        # print(message)
        _discord_url = self._discord_url
        webhook = DiscordWebhook(url=_discord_url, content=message)
        webhook_response = webhook.execute()
        print(webhook_response.reason)


##############################
mnds = mnds()
