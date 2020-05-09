#!/usr/bin/env python3

import anki_vector
import time
from math import ceil
from anki_vector.util import degrees
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from PIL import Image, ImageDraw, ImageFont
import asyncio
from tesla_api import TeslaApiClient
import sys
import os

def make_text_image(text_to_draw, x, y, font=None):
    dimensions = (184, 96)
    text_image = Image.new('RGBA', dimensions, (0, 0, 0, 255))
    dc = ImageDraw.Draw(text_image)
    dc.text((x, y), text_to_draw, fill=(255, 255, 255, 255), font=font)
    return text_image

try:
    font_file = ImageFont.truetype("arial.ttf", 50)
    font_file2 = ImageFont.truetype("arial.ttf", 45)
except IOError:
    try:
        font_file = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        pass

async def main():
    client = TeslaApiClient('TESLA ACCOUNT EMAIL GOES HERE', 'TESLA ACCOUNT PASSWORD GOES HERE')

    vehicles = await client.list_vehicles()

    for v in vehicles:
        await v.wake_up()
        print(v.display_name)
        state = await v.charge.get_state()
        state2 = await v.climate.get_state()
        print("{:0.0f}% Battery Level.".format(state["battery_level"]))
        print("{:0.0f} Miles of Range.".format(state["battery_range"]))
        print("{:0.0f}ºc Inside temperature.".format(state2["inside_temp"]))
        print("Charger is currently {}".format(state["charging_state"]))
        print("{} Minutes to charging complete".format(state["minutes_to_full_charge"]))

        text_to_draw = (v.display_name)
        text_to_draw2 = ("{:0.0f}%".format(state["battery_level"]))
        text_to_draw3 = ("{:0.0f}m".format(state["battery_range"]))
        text_to_draw4 = ("{:0.0f}ºc".format(state2["inside_temp"]))
        text_to_draw5 = ("{}".format(state["charging_state"]))
        text_to_draw6 = ("{} mins".format(state["minutes_to_full_charge"]))
        face_image = make_text_image(text_to_draw, 10, 20, font_file)
        face_image2 = make_text_image(text_to_draw2, 45, 20, font_file)
        face_image3 = make_text_image(text_to_draw3, 35, 20, font_file)
        face_image4 = make_text_image(text_to_draw4, 35, 20, font_file)
        face_image5 = make_text_image(text_to_draw5, 0, 20, font_file2)
        face_image6 = make_text_image(text_to_draw6, 10, 20, font_file)
        args = anki_vector.util.parse_command_args
        
        with anki_vector.Robot() as robot:
            
            current_directory = os.path.dirname(os.path.realpath(__file__))
            image_path = os.path.join(current_directory, "images", "Tesla_Vector.jpg")
            image_file = Image.open(image_path)
            screen_data = anki_vector.screen.convert_image_to_screen_data(image_file)
            duration_s = 1.0
            robot.behavior.set_head_angle(degrees(25.0))
            robot.screen.set_screen_with_image_data(screen_data, duration_s)

            robot.behavior.say_text('Your Tesla', True, 1.1)
            screen_data = anki_vector.screen.convert_image_to_screen_data(face_image) 
            robot.screen.set_screen_with_image_data(screen_data, 3.0, interrupt_running=True)
            robot.behavior.say_text(v.display_name, True, 0.9)

            screen_data2 = anki_vector.screen.convert_image_to_screen_data(face_image2)
            robot.screen.set_screen_with_image_data(screen_data2, 4.0, interrupt_running=True)
            robot.behavior.say_text('is currently at' + str(state["battery_level"]) + 'percent battery level', True, 1.1)

            screen_data3 = anki_vector.screen.convert_image_to_screen_data(face_image3)
            robot.screen.set_screen_with_image_data(screen_data3, 4.0, interrupt_running=True)
            robot.behavior.say_text('which is' + str("{:0.0f}".format(state["battery_range"]) + 'miles of range'))
            
            screen_data4 = anki_vector.screen.convert_image_to_screen_data(face_image4)
            robot.screen.set_screen_with_image_data(screen_data4, 4.0, interrupt_running=True)
            robot.behavior.say_text('The interior temperature is' + str("{:0.0f}".format(state2["inside_temp"]) + 'degrees celseeus'))
            
            if (state["charging_state"]) == 'Charging':
                screen_data5 = anki_vector.screen.convert_image_to_screen_data(face_image5)
                robot.screen.set_screen_with_image_data(screen_data5, 4.0, interrupt_running=True)
                robot.behavior.say_text((v.display_name) + " is currently {}".format(state["charging_state"])) 
                time.sleep(0.2)
                screen_data6 = anki_vector.screen.convert_image_to_screen_data(face_image6)
                robot.screen.set_screen_with_image_data(screen_data6, 4.0, interrupt_running=True)
                robot.behavior.say_text(' and will complete charging in {}'.format(state["minutes_to_full_charge"]) + ' minutes', )

            if (state["battery_level"] <= 20):
                robot.behavior.say_text('you may want to consider charging up' + (v.display_name) + '. Touch my back sensor to open the charge port', True, 1.1)
                while True:
                    if robot.touch.last_sensor_reading.is_being_touched:
                        robot.audio.stream_wav_file("Sounds/Robot_blip_low.wav", 85)
                        await (v.controls.open_charge_port())
                        print('Charge Port Opened')
                        robot.behavior.say_text('Charge Port Opened')

                break
                
            if (state["battery_level"] >= 90):
                current_directory = os.path.dirname(os.path.realpath(__file__))
                image_path = os.path.join(current_directory, "images", "tesla_icon.jpg")
                image_file = Image.open(image_path)
                screen_data = anki_vector.screen.convert_image_to_screen_data(image_file)
                duration_s = 1.0
                robot.behavior.set_head_angle(degrees(25.0))
                robot.screen.set_screen_with_image_data(screen_data, duration_s)
                robot.behavior.say_text((v.display_name) + 'is ready to drive!, Touch my back sensor to open the doors', True, 1.1)
                while True:
                    if robot.touch.last_sensor_reading.is_being_touched:
                        await v.controls._vehicle._command('door_unlock')
                        robot.audio.stream_wav_file("Sounds/Robot_blip_low.wav", 85)
                        print('Doors unlocked')
                        robot.behavior.say_text('doors unlocked')
                        time.sleep(180)
                        await v.controls._vehicle._command('door_lock')
                        print('Doors Auto locked')
                        robot.behavior.say_text('doors auto locked')
                        break 
                        
    await client.close()

asyncio.run(main())