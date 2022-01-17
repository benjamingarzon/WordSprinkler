# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:16:47 2021

@author: Benjamin.Garzon
"""
import os
import pickle
import random
import re
from collections import defaultdict

from google_trans_new import google_translator

# define parameters
N = 20
FREQS_FILE = "freqs.pkl"
SRC_FILE = "notes.txt"
SEND = "email"


def sprinkle(N, FREQS_FILE, SRC_FILE, SEND):
    lines = []
    with open(SRC_FILE, "r") as myfile:
        for line in myfile:
            line = line.strip()
            line = re.sub(" +", " ", line)
            line = re.sub("-", "â", line)
            if not line.startswith("#") and not line == "":
                if not line[0].isdigit():
                    lines.append(line)
    # Select N, take freqs into account
    if os.path.exists(FREQS_FILE):
        with open(FREQS_FILE, "rb") as myfile:
            frequencies = pickle.load(myfile)
        # remove some of them from the list if they already appeared
        for line in frequencies:
            if random.choice(range(frequencies[line] + 1)) > 0:
                if line in lines:
                    lines.remove(line)
    else:
        frequencies = defaultdict(int)
    selected = random.sample(lines, N)
    for line in selected:
        frequencies[line] += 1
    with open(FREQS_FILE, "wb") as myfile:
        pickle.dump(frequencies, myfile)
    # translate into English
    translator = google_translator()
    lines = [(line, translator.translate(line, lang_tgt="en")) for line in selected]
    message = ""
    for line in lines:
        message += "{}\n -> {}\n\n".format(line[0], line[1])
    message += 80 * "-" + "\nTotal of {} concepts reminded.".format(len(frequencies))
    if SEND == "Twilio":
        # send with Whatsapp
        from twilio.rest import Client

        # env variables
        TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
        TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
        FROM_NUMBER = os.environ["FROM_NUMBER"]
        TO_NUMBER = os.environ["TO_NUMBER"]
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=FROM_NUMBER, to=TO_NUMBER)
    if SEND == "email":
        print(message)
        import yagmail

        SENDER_ADDRESS = os.environ["SENDER_ADDRESS"]
        RECEIVER_ADDRESS = os.environ["RECEIVER_ADDRESS"]
        print("Sending from {} to {}".format(SENDER_ADDRESS, RECEIVER_ADDRESS))
        yag = yagmail.SMTP(SENDER_ADDRESS)
        yag.send(to=RECEIVER_ADDRESS, subject="EIN PAAR NEUE WÖRTER", contents=message)
        print("Done!")


if __name__ == "__main__":
    sprinkle(N, FREQS_FILE, SRC_FILE, SEND)
# import time
# time.sleep(5)
