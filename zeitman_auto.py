#!/usr/bin/env python3


"""
Automatically fill out zeitweb form
"""

import getpass
import random
import time
import os

from selenium.common.exceptions import (
    UnexpectedTagNameException,
    NoSuchElementException,
)
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# import config.py file - copy template if doesn't exist
if not os.path.exists("config.py"):
    print("config.py file does not exist: copying template!")
    os.popen("cp config_template.py config.py")
    time.sleep(1)  # otherwise config is not imported correctly
import config


# user information
usr = input("Username: ")
pswd = getpass.getpass("Password: ")

# launch zeitweb
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://zeitweb.hzdr.de/scripts_zeitm/login.php?sso=2")

# login
usr_elem = driver.find_element("name", "username")
usr_elem.clear()
usr_elem.send_keys(usr)
pswd_elem = driver.find_element("name", "passwort")
pswd_elem.send_keys(pswd)
submit = driver.find_element("id", "button")
submit.click()

# go to chosen month
monthstr = "jahrmonat(" + str(config.year) + "," + str(config.month) + ', "E")'
timesheets = driver.find_elements("class name", "statustd")

# search until chosen month is found
for timesheet in timesheets:
    onclick = timesheet.get_attribute("onclick")
    if onclick == monthstr:
        timesheet.click()
        break

# max no of days in month
ndays = 31

# switch to the main table frame
frame = driver.find_element("name", "Hauptfenster")
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
    rand_starthr, rand_startmin = random_time(
        config.starthr, config.startmin, config.rand_start
    )
    rand_endhr, rand_endmin = random_time(config.endhr, config.endmin, config.rand_end)

    # exception raised if holiday or month < 31 days
    try:
        # check that day is a normal working day
        type_id = "anab" + str(n)
        type_elem = Select(driver.find_element("name", type_id))
        default_text = type_elem.first_selected_option.text

        # start hour
        strthr_id = "tf_vonSS" + str(n)
        strthr_elem = Select(driver.find_element("name", strthr_id))

        # start minute
        strtmin_id = "tf_vonMM" + str(n)
        strtmin_elem = Select(driver.find_element("name", strtmin_id))

        # end hour
        endhr_id = "tf_bisSS" + str(n)
        endhr_elem = Select(driver.find_element("name", endhr_id))

        # end minute
        endmin_id = "tf_bisMM" + str(n)
        endmin_elem = Select(driver.find_element("name", endmin_id))

        # input data if day is normal working day
        autofill_types = ["not entered", "mobile working"]
        overwrite_types = ["present", "mobile working"]

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
        elif default_text in overwrite_types and config.overwrite_data:
            strthr_elem.select_by_value(str(rand_starthr))
            strtmin_elem.select_by_value(str(rand_startmin))
            endhr_elem.select_by_value(str(rand_endhr))
            endmin_elem.select_by_value(str(rand_endmin))

    except UnexpectedTagNameException:
        pass

    except NoSuchElementException:
        break

# if save and exit
if config.save_and_exit:

    # sleep for a second
    time.sleep(1)
    # switch back to main frame
    driver.switch_to.parent_frame()

    # switch to navigation frame
    frame = driver.find_element("name", "Navigation")
    driver.switch_to.frame(frame)

    # click save button
    save_button = driver.find_element("name", "Save_az")
    save_button.click()

    # close browser
    driver.close()
