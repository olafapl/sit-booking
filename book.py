from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime, timedelta
import argparse


def log_in(driver, username: str, password: str):
    print("Logger inn ...")
    driver.get("https://www.sit.no/connect/oauthconnector_dataporten")

    # Select organization.
    choose_org = driver.find_element_by_id("org-chooser-selectized")
    choose_org.click()
    choose_org.send_keys("NTNU")
    choose_org.send_keys(Keys.RETURN)
    driver.find_element_by_xpath("//*[@id='discoform_feide']/button").click()

    # Fill out and submit login form.
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_xpath("//*[@id='main']/div[1]/form/button").click()

    # Wait for redirect to sit.no.
    driver.find_element_by_id("page")
    print("Innlogging vellykket!")


facility_checkboxes = {
    "gløshaugen": 1,
    "dragvoll": 2,
    "portalen": 3,
    "moholt": 5
}


def book_slot(driver, start: str, days: int, facility: str, max_tries=2):
    print(f"Booker egentreningstime {start[:2]}:{start[2:]} på {facility.capitalize()} om {days} dag(er) ...")
    now = datetime.now()
    training_start = (now + timedelta(days=days)).replace(
        hour=int(start[:2]), minute=int(start[2:]), second=0, microsecond=0)
    delta = training_start - now

    if delta >= timedelta(days=2):
        opens_in = delta - timedelta(days=2)
        print(f"Booking åpner om {str(opens_in).split('.')[0]}. Går i dvale ...")
        sleep(opens_in.total_seconds())
    
    current_try = 1
    while current_try <= max_tries:
        try:
            driver.get("https://www.sit.no/trening/treneselv")

            # Accept cookies.
            if current_try == 1:
                try:
                    driver.find_element_by_xpath("//*[@id='popup-buttons']/button[1]").click()
                except:
                    pass

            driver.switch_to.frame(driver.find_element_by_id("ibooking-iframe"))
    
            # Uncheck unwanted facilities.
            for i in range(1, 6):
                if i == facility_checkboxes[facility]:
                    continue
                driver.find_element_by_xpath(f"//*[@id='ScheduleApp']/div/div/div[2]/div/button[{i}]/input").click()
    
            # Click on the slot.
            driver.find_element_by_xpath(f"//*[@id='ScheduleApp']/div/div/div[4]/div[{1 + days}]"
                                                f"/div[(.//*|.)[contains(., '{start[:2]}.{start[2:]}–')]]/div").click()
            sleep(1)  # Wait for the modal to fade in.
    
            # Click on the "book" button in the modal.
            driver.find_element_by_xpath(
                "//*[@id='ScheduleApp']/div/div/div[5]/div/div/div[3]/div[8]/button[1]").click()
            sleep(1)  # Wait for the modal to fade in.
    
            # Click the "OK" button in the confirmation modal.
            driver.find_element_by_xpath("//*[@id='ModalDiv']/div/div/div[2]/button").click()
            print("Booking vellykket!")
            break
        except:
            if current_try == max_tries:
                print("Klarte ikke å booke time :-(")
            else:
                print("Det har skjedd en feil. Prøver på nytt ...")
            current_try += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Book egentreningstid hos Sit.")
    parser.add_argument("brukernavn", type=str, help="Feide-brukernavn")
    parser.add_argument("passord", type=str, help="Feide-passord")
    parser.add_argument("--tid", type=str, metavar="hhmm", help="starttid (eksempel: 0730)", required=True)
    parser.add_argument("--dager", type=int, default=2, help="antall dager frem i tid det skal bookes (default: 2)")
    parser.add_argument("--max-forsøk", type=int, default=2, help="maks. antall forsøk på å booke (default: 2)")
    parser.add_argument("--senter", type=str, default="gløshaugen", choices=facility_checkboxes.keys(),
                        help="treningssenter (default: gløshaugen)")
    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    log_in(driver, args.brukernavn, args.passord)
    book_slot(driver, args.tid, args.dager, args.senter, args.max_forsøk)
    driver.quit()
