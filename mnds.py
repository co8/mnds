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

    _config = {}
    _discord_url = ""
    _curl_url = "curl -s http://localhost:4050/"

    def curl_tool(self, path):
        output = os.popen(self._curl_url + path).read()
        return json.loads(output)

    ###load config.json vars
    def load_config(self):
        with open("config.json") as json_data_file:
            self._config = json.load(json_data_file)
        self.set_discord_url()

    def set_discord_url(self):
        self._discord_url = self._config["discord_url"]

    def get_mmn_report(self):
        return self.curl_tool("mmn/report")

    def get_services(self):
        output = self.curl_tool("services")
        return output[0]

    def get_stats(self):
        output = self.curl_tool("sessions/stats-aggregated")
        output["stats"]["earnings"] = str(
            self.nice_myst_amount(output["stats"]["sum_tokens"], 4)
        )
        return output["stats"]

    def get_healthcheck(self):
        return self.curl_tool("healthcheck")

    def get_version(self):
        output = self.get_healthcheck()
        return output["version"]

    def services_mnds(self):
        services = self.get_services()
        per_hour_places = 6
        per_gib_places = 4
        return {
            "provider_id": services["provider_id"][0:7],  # first 7 char of Node ID
            "status": services["status"].upper(),
            "type": services["type"].capitalize(),
            "currency": services["proposal"]["price"]["currency"],
            "per_hour": str(
                self.nice_myst_amount(
                    services["proposal"]["price"]["per_hour"], per_hour_places
                )
            ),
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

    def format_usd(self, amt):
        return "{:.2f}".format(amt)

    def discord_message(self):
        services = self.services_mnds()
        stats = self.get_stats()
        version = self.get_version()
        mmn_report = self.get_mmn_report()
        output = (
            "**"
            # "Node: **"
            + mmn_report["name"]
            # + services["provider_id"]
            # + "** Status: **"
            + "** / **"
            + services["status"]
            # + "** Earnings: **"
            + "** / v"
            + version
            # + "**"
            + "\n"
            + "Bounty: **#"
            + str(mmn_report["report"]["position_residential"])
            + " / "
            + mmn_report["report"]["balance_residential_tokens"]
            + " ($"
            + self.format_usd(mmn_report["report"]["balance_residential_usd"])
            + ")**"
            + "\n"
            + "Earnings: "
            + stats["earnings"]
            + " "
            + services["currency"]
            + " / "
            + "Sessions: "
            + str(stats["count"])
            # + " / "
            # + str(stats["count_consumers"])
            + "\n"
            + "Rate: "
            # + services["type"] # Wireguard
            + " `"
            + services["per_hour"]
            + "/hr` + `"
            + services["per_gib"]
            + "/GiB`"
        )
        return output

    ##############################
    def __init__(self):
        """init"""
        self.load_config()
        message = self.discord_message()
        # print(message)
        _discord_url = self._discord_url
        webhook = DiscordWebhook(url=_discord_url, content=message)
        webhook_response = webhook.execute()
        print(webhook_response.reason)


##############################
mnds = mnds()
