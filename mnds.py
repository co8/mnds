#!/usr/local/bin/python3

import json
import os
import math
from discord_webhook import DiscordWebhook

########
# Install Python PIP3
# $ sudo apt-get -y install python3-pip
# install Discord-Webhook module
# $ pip3 install discord-webhook
#
# CRONTAB
# run script every 3 or 6 hours
# $ crontab -e
# 0 */3 * * * cd ~/mnds; python3 mnds.py >> cron.log 2>&1
# or
# 0 */6 * * * cd ~/mnds; python3 mnds.py >> cron.log 2>&1
########


class mnds:
    """co8/mnds - Mysterium Node Discord Status"""

    _config = {}
    _discord_url = ""
    _api_route = "http://localhost:4050/"

    def curl_tequila(self, endpoint):
        output = os.popen("curl -s " + self._api_route + endpoint).read()
        return json.loads(output)

    def load_config(self):
        with open("config.json") as json_data_file:
            self._config = json.load(json_data_file)
        self._discord_url = self._config["discord_url"]

    def sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} Yi{suffix}"

    def get_mmn_report(self):
        output = self.curl_tequila("mmn/report")
        bounty = {}
        if bool(output["report"]["position_residential_eligible"]):
            bounty = {
                "position": str(output["report"]["position_residential"]),
                "tokens": output["report"]["balance_residential_tokens"],
                "usd": self.format_usd(output["report"]["balance_residential_usd"]),
            }
        else:
            bounty = {
                "position": str(output["report"]["position_global"]),
                "tokens": output["report"]["balance_global_tokens"],
                "usd": self.format_usd(output["report"]["balance_global_usd"]),
            }
        output["bounty"] = bounty
        return output

    # not used until mainnet
    def get_stats(self):
        output = self.curl_tequila("sessions/stats-aggregated")
        output["stats"]["earnings"] = str(
            self.nice_myst_amount(output["stats"]["sum_tokens"])
        )
        output["stats"]["transfer"] = self.sizeof_fmt(
            output["stats"]["sum_bytes_received"] + output["stats"]["sum_bytes_sent"]
        )
        return output["stats"]

    def get_healthcheck(self):
        return self.curl_tequila("healthcheck")

    def get_version(self):
        output = self.get_healthcheck()
        return output["version"]

    def get_services(self):
        output = self.curl_tequila("services")
        services = output[0]
        status = (
            "Active"
            if services["status"] == "Running"
            else "{services['status']}".upper()
        )
        return {
            "provider_id": services["provider_id"],
            "status": status,
            "type": services["type"].capitalize(),
            "currency": services["proposal"]["price"]["currency"],
            "per_hour": str(
                self.nice_myst_amount(services["proposal"]["price"]["per_hour"])
            ),
            "per_gib": str(
                self.nice_myst_amount(services["proposal"]["price"]["per_gib"])
            ),
        }

    def nice_myst_amount(self, amt):
        output = amt * 0.000000000000000001
        places = "{:.4f}" if output > 0.001 else "{:.6f}"
        return places.format(output).rstrip("0")

    def format_usd(self, amt):
        return "{:.2f}".format(amt)

    def node_name(self, name, provider_id):
        if len(name) > 20:
            return provider_id[0:7]
        else:
            return name

    def discord_message(self):
        services = self.get_services()
        version = self.get_version()
        mmn_report = self.get_mmn_report()
        stats = self.get_stats()
        return (
            "🤖 **"
            + self.node_name(mmn_report["name"], services["provider_id"])
            + "**, v"
            + version
            + ", "
            + services["status"]
            + "\n"
            + "**"
            + mmn_report["bounty"]["tokens"]
            + "**, #"
            + mmn_report["bounty"]["position"]
            # + " ($"
            # + mmn_report["bounty"]["usd"]
            # + ")"
            # + "\n"
            # + ", "
            # + str(stats["count"])
            # + " Sessions"
            # + ", "
            # + stats["transfer"]
            # + " Transferred"
            + "\n"
            + "Rate:  "
            + services["per_hour"]
            + "/hr + "
            + services["per_gib"]
            + "/GiB"
        )

    ##############################
    def __init__(self):
        """mnds init"""
        self.load_config()
        message = self.discord_message()
        webhook = DiscordWebhook(url=self._discord_url, content=message)
        webhook_response = webhook.execute()
        print(webhook_response.reason)


##############################
mnds = mnds()
