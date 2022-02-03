#!/usr/bin/env python3


"""
Automatically fill out zeitweb form
"""

import sys
import getpass
import random
import time

from selenium.common.exceptions import (
    UnexpectedTagNameException,
    NoSuchElementException,
)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

###################################################

# user defined parameters

month = 1  # month by number
year = 2022

# time data

# average start time
starthr = 9
startmin = 30

# average finish time
endhr = 18
endmin = 30

# random noise (in blocks of 10 minutes)
rand_start = 1
rand_end = 3

# whether to overwrite existing presence data
overwrite_data = False

# whether to automatically save and exit
save_and_exit = True

##################################################

# user information
usr = input("Username: ")
pswd = getpass.getpass("Password: ")

# launch zeitweb
driver = webdriver.Chrome()
driver.get("https://zeitweb.hzdr.de/scripts_zeitm/login.php?sso=2")

# login
usr_elem = driver.find_element_by_name("username")
usr_elem.clear()
usr_elem.send_keys(usr)
pswd_elem = driver.find_element_by_name("passwort")
pswd_elem.send_keys(pswd)
submit = driver.find_element_by_id("button")
submit.click()

# go to chosen month
monthstr = "jahrmonat(" + str(year) + "," + str(month) + ', "E")'
timesheets = driver.find_elements_by_class_name("statustd")

# search until chosen month is found
for timesheet in timesheets:
    onclick = timesheet.get_attribute("onclick")
    if onclick == monthstr:
        timesheet.click()
        break

# max no of days in month
ndays = 31

# switch to the main table frame
frame = driver.find_element_by_name("Hauptfenster")
driver.switch_to.frame(frame)


def random_time(hour, minute, noise):

    # add in the random noise
    randtime = 10 * random.randint(-noise, noise)

    if minute + randtime >= 60:
        hour = hour + 1
        minute = (minute + randtime) % 60
    elif minute + randtime <= 0:
        hour = hour - 1
        minute = (minute + randtime) % 60
    else:
        minute = minute + randtime

    return hour, minute


# loop over days in the month
for n in range(1, ndays + 1):

    # randomise start and end times
    rand_starthr, rand_startmin = random_time(starthr, startmin, rand_start)
    rand_endhr, rand_endmin = random_time(endhr, endmin, rand_end)

    # exception raised if holiday or month < 31 days
    try:
        # check that day is a normal working day
        type_id = "anab" + str(n)
        type_elem = Select(driver.find_element_by_name(type_id))
        default_text = type_elem.first_selected_option.text

        # start hour
        strthr_id = "tf_vonSS" + str(n)
        strthr_elem = Select(driver.find_element_by_name(strthr_id))

        # start minute
        strtmin_id = "tf_vonMM" + str(n)
        strtmin_elem = Select(driver.find_element_by_name(strtmin_id))

        # end hour
        endhr_id = "tf_bisSS" + str(n)
        endhr_elem = Select(driver.find_element_by_name(endhr_id))

        # end minute
        endmin_id = "tf_bisMM" + str(n)
        endmin_elem = Select(driver.find_element_by_name(endmin_id))

        # input data if day is normal working day
        autofill_types = ["not entered", "teleworking"]
        overwrite_types = ["present", "teleworking"]

        # if data should be filled
        if default_text in autofill_types:
            strthr_elem.select_by_value(str(rand_starthr))
            strtmin_elem.select_by_value(str(rand_startmin))
            endhr_elem.select_by_value(str(rand_endhr))
            endmin_elem.select_by_value(str(rand_endmin))

            # enter "present" which has key "9999"
            if default_text == "not entered":
                type_elem.select_by_value("9999")

        # if overwriting data
        elif default_text in overwrite_types and overwrite_data:
            strthr_elem.select_by_value(str(rand_starthr))
            strtmin_elem.select_by_value(str(rand_startmin))
            endhr_elem.select_by_value(str(rand_endhr))
            endmin_elem.select_by_value(str(rand_endmin))

    except UnexpectedTagNameException:
        pass

    except NoSuchElementException:
        break

# if save and exit
if save_and_exit:

    # sleep for a second
    time.sleep(1)
    # switch back to main frame
    driver.switch_to.parent_frame()

    # switch to navigation frame
    frame = driver.find_element_by_name("Navigation")
    driver.switch_to.frame(frame)

    # click save button
    save_button = driver.find_element_by_name("Save_az")
    save_button.click()

    # close browser
    driver.close()
