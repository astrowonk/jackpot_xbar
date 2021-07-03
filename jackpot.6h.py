#!/usr/local/opt/miniforge3/bin/python

# <bitbar.title>Jackpot</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Marcos</bitbar.author>
# <xbar.author.github>astrowonk</xbar.author.github>
# <bitbar.desc>Retrieves current lotto jackpots.</bitbar.desc>
# <bitbar.dependencies>python,requests</bitbar.dependencies>
# <bitbar.abouturl>http://marcoshuerta.com/</bitbar.abouturl>

import requests
import json


class Jackpot():
    mega_json = None
    pb_json = None
    mega_color = 'black'
    pb_color = 'black'
    symbol_color = 'black'

    def __init__(self) -> None:
        self.load_data()
        self.handle_color()

    def load_data(self):
        """Load data from endpoints, store to properties"""
        #load data
        url = "https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData"

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-us',
            'Host': 'www.megamillions.com',
            'Origin': 'https://www.megamillions.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.megamillions.com/',
            'X-Requested-With': 'XMLHttpRequest',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        self.mega_json = json.loads(response.json()['d'])

        url2 = "https://www.powerball.com/api/v1/estimates/powerball?_format=json"

        payload = {}
        headers = {}

        response2 = requests.request("GET",
                                     url2,
                                     headers=headers,
                                     data=payload)
        self.pb_json = response2.json()[0]

    def handle_color(self):

        #handle colors - make things green if prize is big
        if self.mega_json['Jackpot']['NextPrizePool'] > 200E6:
            self.mega_color = 'green'

        mapping_dict = {'Million': 1E6, "Billion": 1E9}
        out = self.pb_json['field_prize_amount'].split()
        pb_float_value = float(out[0].replace('$', '')) * mapping_dict[out[1]]

        if pb_float_value > 200E6:
            self.pb_color = 'green'
        else:
            self.pb_color = 'black'

        if 'green' in [self.mega_color, self.pb_color]:
            self.symbol_color = 'green'
        else:
            self.symbol_color = 'black'

    def generate_menu(self):
        pb_str = self.pb_json['field_prize_amount'].replace(
            'Million', 'M').replace(' ', '').replace('Billion', 'B')
        mm_str = f"${(self.mega_json['Jackpot']['NextPrizePool'] / 1E6):.1f}M"

        #generate menus
        print(
            f":dollarsign.circle.fill: | size=13 sfcolor={self.symbol_color}")
        print('---')
        print(f"MM: {mm_str} | size=12 color={self.mega_color}")
        print(f"PB: {pb_str} | size=12 color={self.pb_color}")


if __name__ == "__main__":
    Jackpot().generate_menu()
