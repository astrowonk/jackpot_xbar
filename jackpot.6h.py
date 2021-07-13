#!/usr/bin/env python3

# <xbar.title>Jackpot</xbar.title>
# <xbar.version>v1.1</xbar.version>
# <xbar.author>Marcos</xbar.author>
# <xbar.author.github>astrowonk</bitabar.author.github>
# <xbar.desc>Retrieves current Mega Millions and Powerball jackpots.</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/astrowonk/jackpot_xbar</xbar.abouturl>

import gzip
from http import client
import json
import datetime
from os import environ


def get_weekday(day):
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    return days.index(day) + 1


def get_next_dayofweek_datetime(dayofweek):
    date_time = datetime.datetime.now().date()
    start_time_w = date_time.isoweekday()
    target_w = get_weekday(dayofweek)
    if start_time_w <= target_w:
        day_diff = target_w - start_time_w
    else:
        day_diff = 7 - (start_time_w - target_w)

    return date_time + datetime.timedelta(days=day_diff)


class Jackpot():
    mega_json = None
    pb_json = None
    mega_color = 'black'
    pb_color = 'black'
    symbol_color = 'black'
    pb_float_value = None
    icon_row = None

    def __init__(self) -> None:
        self.load_data()
        self.handle_color()
        self.set_icon()

    def set_icon(self):
        if environ.get('SWIFTBAR'):
            self.icon_row = f":dollarsign.circle.fill: | size=13 | sfcolor={self.symbol_color}"
        else:
            self.icon_row = f" $ | size=13 | font='Copperplate Gothic Bold' color={self.symbol_color}"

    def load_data(self):
        """Load data from endpoints, store to properties"""
        #load data
        conn = client.HTTPSConnection("www.megamillions.com")
        payload = ''
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-us',
            'Host': 'www.megamillions.com',
            'Origin': 'https://www.megamillions.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.megamillions.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        conn.request("POST", "/cmspages/utilservice.asmx/GetLatestDrawData",
                     payload, headers)
        response = conn.getresponse().read()
        self.mega_json = json.loads(json.loads(gzip.decompress(response))['d'])

        conn = client.HTTPSConnection("www.powerball.com")
        payload = ''
        headers = {}
        conn.request("GET", "/api/v1/estimates/powerball?_format=json",
                     payload, headers)
        response2 = conn.getresponse().read()

        self.pb_json = json.loads(response2)[0]

    def handle_color(self):

        #handle colors - make things green if prize is big
        if self.mega_json['Jackpot']['NextPrizePool'] >= 200E6:
            self.mega_color = 'green'

        mapping_dict = {'Million': 1E6, "Billion": 1E9}
        out = self.pb_json['field_prize_amount'].split()
        self.pb_float_value = float(out[0].replace('$',
                                                   '')) * mapping_dict[out[1]]

        if self.pb_float_value >= 200E6:
            self.pb_color = 'green'

        if 'green' in [self.mega_color, self.pb_color]:
            self.symbol_color = 'green'

    @staticmethod
    def format_float(value):
        """Format float as a string with B for billion and M for million"""
        if value >= 1E9:
            return f"{value / 1E9:.1f}B"
        elif value >= 1E6:
            return f"{value / 1E6:.1f}M"
        else:
            return f"{value / 1E3:.1f}K"

    def generate_menu(self):
        pb_str = self.format_float(self.pb_float_value)
        mm_str = self.format_float(self.mega_json['Jackpot']['NextPrizePool'])

        #generate menus
        print(self.icon_row)
        print('---')
        print(
            f"MM: {mm_str}, {self.get_next_drawing_date(['tue','fri'])} | size=12 color={self.mega_color} href=https://www.megamillions.com"
        )
        print(
            f"PB: {pb_str}, {self.get_next_drawing_date(['wed','sat'])} | size=12 color={self.pb_color} href=https://www.powerball.com"
        )

    @staticmethod
    def get_next_drawing_date(list_of_weekdays):
        dates = [get_next_dayofweek_datetime(x) for x in list_of_weekdays]
        return min(dates).strftime("%a %b %d")


if __name__ == "__main__":
    Jackpot().generate_menu()
