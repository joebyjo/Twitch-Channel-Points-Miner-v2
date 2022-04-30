import logging
from datetime import datetime
from config import *

from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings
from TwitchChannelPointsMiner.classes.Discord import Discord, requests, dedent
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, DelayMode
from TwitchChannelPointsMiner.classes.Settings import Events
from TwitchChannelPointsMiner import utils


def webhooksend(self, message: str, event: Events) -> None:  # override the deafult webhook msg
    if str(event) in self.events:
        requests.post(
            url=self.webhook_api,
            json={
                "username": "Twitch Channel Points Miner",
                "avatar_url": "https://i.imgur.com/X9fEkhT.png",
                "embeds": [{
                    "title": str(event).lower(),
                    "description": f"```\n{dedent(message[1:])}\n```\n\n<t:{int(datetime.now().timestamp())}>",
                    "color": 0x8bc34a
                }]

            }
        )


def dont_millify(input, precision):  # override millify in module
    return input


# Monkey patching
Discord.send = webhooksend
utils.millify = dont_millify


twitch_miner = TwitchChannelPointsMiner(
    username=TWITCH_USERNAME,
    password=TWITCH_PWD,
    logger_settings=LoggerSettings(
        save=True,  # If you want to save logs in a file (suggested)
        console_level=logging.INFO,  # Level of logs - use logging.DEBUG for more info
        file_level=logging.INFO,  # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=True,  # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less="extraless",  # If you think that the logs are too verbose, set this to True,set this to "extraless" to remove datetime on console log
        colored=True,  # If you want to print colored text
        discord=Discord(
            webhook_api=DISCORD_WEBHOOK,
            # Discord Webhook URL
            events=[Events.STREAMER_ONLINE, Events.BET_WIN, Events.JOIN_RAID]
        )

    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,  # If you want to Bet / Make prediction
        follow_raid=True,  # Follow raid to obtain more points
        claim_drops=True,
        # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        watch_streak=True,
        # If a streamer go online change the priority of streamers array and catch the watch screak. Issue #11
        chat=ChatPresence.ONLINE,  # Join irc chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=BetSettings(
            strategy=Strategy.SMART,  # Choose you strategy!
            percentage=5,  # Place the x% of your channel points
            percentage_gap=20,  # Gap difference between outcomesA and outcomesB (for SMART strategy)
            max_points=5000,  # If the x percentage of your channel points is gt bet_max_points set this value
            stealth_mode=True,
            # If the calculated amount of channel points is GT the highest bet, place the highest value minus 1-2 points Issue #33
            delay_mode=DelayMode.FROM_END,
            # When placing a bet, we will wait until `delay` seconds before the end of the timer
            delay=6,
            minimum_points=2000  # Place the bet only if we have at least 20k points. Issue #113

        ))

)

twitch_miner.mine([
    Streamer("valorant",
             settings=StreamerSettings(make_predictions=False, follow_raid=True, claim_drops=True, watch_streak=True,
                                       chat=ChatPresence.ONLINE)),
    "officialboaster",
    "mistic",
    "michaelreeves"],
    followers=True)  # Array of streamers and followed streamers
