#!/usr/bin/python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Location
from time import sleep

# Bot token receieved from BotFather
TOKEN = ''

# Luis application setup
LUIS_KEY = ''
ENDPOINT = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/1463f532-eb87-4cd6-aa69-197ef6e0fbce?verbose=true&timezoneOffset=-360&q='

# Global parameters  
is_locked = False
is_lights_are_on = False

################################################### GPIO pins setup #############################################################
GPIO.setmode(GPIO.BOARD)

#Servo
GPIO.setup(3, GPIO.OUT)
pwm=GPIO.PWM(3, 50)
pwm.start(0)
#LEDs
GPIO.setup(5, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)


# Change the angle of the Servo motor
def set_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(3, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3, False)
    pwm.ChangeDutyCycle(0)


##################################################### Command Handlers ##########################################################
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def lock(update, context):
    set_angle(90)
    is_locked = True
    update.message.reply_text('The car is locked!')
    

def unlock(update, context):
    set_angle(0)
    is_locked = False
    update.message.reply_text('The car is unlocked!')


def turn_on_lights(update, context):
    GPIO.output(5, True)
    GPIO.output(7, True)
    GPIO.output(29, True)
    GPIO.output(31, True)
    global is_lights_are_on
    is_front_lights_are_on = True
    update.message.reply_text('Lights are ON!')


def turn_off_lights(update, context):
    GPIO.output(5, False)
    GPIO.output(7, False)
    GPIO.output(29, False)
    GPIO.output(31, False)
    global is_front_lights_are_on
    is_lights_are_on = False
    update.message.reply_text('Lights are OFF!')


def is_locked(update, context):
    if (is_locked):
        update.message.reply_text("I'm locked!")
    else:
        update.message.reply_text("I'm not locked")


def is_lights_on(update, context):
    if (is_lights_are_on):
        update.message.reply_text('Lights ON!')
    else:
        update.message.reply_text('Lights OFF!')


def where_are_you(update, context):
    context.bot.send_location(chat_id=update.message.chat_id, latitude=32.1589224, longitude=34.8084406)


###################################################### Language Understanding ###################################################

# Parse the message and call the right command handler
def hadle_text_message(update, context):
    intent = get_intent(update.message.text)
    if (intent == "get lights"):
        islightson(update, context)
    elif (intent == "get location"):
        whereareyou(update, context)
    elif (intent == "get lock"):
        islocked(update, context)
    elif (intent == "lock"):
        lock(update, context)
    elif (intent == "Turn off the lights"):
        turn_off_lights(update, context)
    elif (intent == "Turn on the lights"):
        turn_on_lights(update, context)
    elif (intent == "unlock"):
        unlock(update, context)
    else:
        update.messae.reply_text("Sorry I didn't understand you")


# Send the receieved message to the LUIS application and get the top scoring intent
def get_intent(message):
    # Set up the request headers
    headers = {
        'Ocp-Apim-Subscription-Key': LUIS_KEY,
    }

    try:
		# Send the request to the Luis application endpoint
        r = requests.get(ENDPOINT + message, headers=headers)
		
		# Get the top scoring intent from the possible intents list
        return r.json()['topScoringIntent']['intent']
    except Exception:
        return None
		
#################################################################################################################################


def main():
	# Set up the bot updater with the bot Token
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
	
	# Set up a commnad handler for each command
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("lock", lock))
    dp.add_handler(CommandHandler("unlock", unlock))
    dp.add_handler(CommandHandler("turnonlights", turn_on_lights))
    dp.add_handler(CommandHandler("turnofflights", turn_off_lights))
    dp.add_handler(CommandHandler("islightson", is_lights_on))
    dp.add_handler(CommandHandler("whereareyou", where_are_you))
	
	# Set up a message handler for text messages
    dp.add_handler(MessageHandler(Filters.text, hadle_text_message))
	
	# Start listen for incoming messages
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()