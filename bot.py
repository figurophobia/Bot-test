from bs4 import BeautifulSoup
from collections import Counter
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from termcolor import colored
from dotenv import load_dotenv
from twilio.rest import Client

import os


def load_credentials():
    load_dotenv()
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    return email, password


def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
    return webdriver.Firefox(options=options)  # Cambiar a webdriver.Chrome() si usas Chrome


def login_to_course(driver, course_url, email, password):
    driver.get(course_url)
    time.sleep(5)
    
    email_field = driver.switch_to.active_element
    email_field.send_keys(email)
    email_field.send_keys(Keys.RETURN)
    time.sleep(2)
    
    password_field = driver.switch_to.active_element
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)
    
    button_field = driver.switch_to.active_element
    button_field.send_keys(Keys.RETURN)
    time.sleep(5)


def get_activities(driver):
    driver.refresh()
    time.sleep(5)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.find_all('div', class_='activity-item focus-control', attrs={"data-activityname": True})


def process_activities(activity_elements, previous_activities):
    current_activities = set()
    print(f"Se encontraron {len(activity_elements)} actividades:")
    
    for index, element in enumerate(activity_elements, start=1):
        activity_name = element.get('data-activityname')
        current_activities.add(activity_name)
        print(f"{index}. Nombre de actividad: {activity_name}")
        
    if previous_activities:
        new_activities = current_activities - previous_activities
        removed_activities = previous_activities - current_activities

        if new_activities:
            for activity in new_activities:
                print(colored(f"Actividad nueva: {activity}", "green"))
                send_whatsapp_message(f"Actividad nueva: {activity}")

        if removed_activities:
            for activity in removed_activities:
                print(colored(f"Actividad eliminada: {activity}", "red"))
                send_whatsapp_message(f"Actividad eliminada: {activity}")

    return current_activities

def send_whatsapp_message(mensaje):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=mensaje,
        to='whatsapp:+34642506943'
    )


def main():
    email, password = load_credentials()
    course_url = "https://cv.usc.es/course/view.php?id=49565"
    driver = setup_driver()
    
    try:
        login_to_course(driver, course_url, email, password)
        previous_activities = set()

        while True:
            activity_elements = get_activities(driver)
            if not activity_elements:
                print("No se encontraron elementos con el atributo 'data-activityname'.")
            else:
                previous_activities = process_activities(activity_elements, previous_activities)
            
            time.sleep(30)
    finally:
        driver.quit()




if __name__ == "__main__":
    main()
