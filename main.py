import pandas as pd
import numpy as np
import sklearn as sk
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Final # per dare un tipo di variabile alle nostre costanti
import requests
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
load_dotenv()
KEY: Final = os.getenv("KEY")
BOT_NAME : Final = '@loreimasbot'

# definisco funzione asincrona, per starting command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Velkommen tilbage')  # messaggio iniziale quando si preme start

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Det er en ny kommando')

# Responses
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if 'f1' in text:
        url = "https://api.formula1.com/v1/event-tracker"
        headers = {
            "accept": "*/*",
            "accept-language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
            "apikey": "xZ7AOODSjiQadLsIYWefQrpCSQVDbHGC",
            "content-type": "application/json",
            "locale": "en",
            "origin": "https://www.formula1.com",
            "priority": "u=1, i",
            "referer": "https://www.formula1.com/",
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        # Find the next race session in the timetables array
        timetables = data.get("seasonContext", {}).get("timetables", [])
        next_race = None
        next_event = next((event for event in timetables if event.get("state") == "upcoming"), None)
        for session in timetables:
            if session.get("sessionType") == "Race" and session.get("state") == "upcoming":
                next_race = session
                break

        if next_event:
            print("Prossimo evento:")
            print("Tipo:", next_event.get("description"))
            print("Inizio:", next_event.get("startTime"))
            print("Fine:", next_event.get("endTime"))
            print("Timezone:", next_event.get("timezone"))
            start_time = next_event.get("startTime")
            timezone = next_event.get("timezone")
            print(timezone)

            naive_dt = datetime.fromisoformat(start_time)

                # Timezone sorgente
            source_tz = pytz.timezone(timezone)
            localized_dt = source_tz.localize(naive_dt)

                # Timezone italiana
            italian_tz = pytz.timezone("Europe/Rome")
            italian_dt = localized_dt.astimezone(italian_tz)

        else:
            print("Nessun evento upcoming trovato.")
            message1 = "No upcoming race found."
        message1 = (f"🏁 *Next F1 Event Info:*\n"
                    f"📍 Name: {next_event.get("description")}\n"
                    f"🕒 Start Time: {next_event.get("startTime")}\n"
                    f"🇮🇹 Start Time (Italy): {italian_dt}")

        await update.message.reply_text(message1, parse_mode="Markdown")

        if next_race:
            race_info = data.get("race", {})
            print("Next Race Information:")
            print(f"Name: {race_info.get('meetingName', 'N/A')}")
            print(f"Location: {race_info.get('meetingLocation', 'N/A')}")
            print(f"Country: {race_info.get('meetingCountryName', 'N/A')}")
            print(f"Start Time: {next_race.get('startTime', 'N/A')}")
            message = (
                    f"🏁 *Next F1 Race Info:*\n"
                    f"📍 Name: {race_info.get('meetingName', 'N/A')}\n"
                    f"🌍 Location: {race_info.get('meetingLocation', 'N/A')}, {race_info.get('meetingCountryName', 'N/A')}\n"
                    f"🕒 Start Time: {next_race.get('startTime', 'N/A')}"
            )

        else:
            print("No upcoming race found.")
            message = "No upcoming race found."

        await update.message.reply_text(message, parse_mode="Markdown")

if __name__ == '__main__':
    app = Application.builder().token(KEY).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Bot is running...")
    app.run_polling()



