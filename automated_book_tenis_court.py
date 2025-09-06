from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pause
import datetime
from tkinter import *

# Choose Hours Panel
root = Tk()
root.title("Book Tennis Court")
root.geometry("400x400")
horas = []  # 1: 9am, 2: 10am, 3: 11am, 4: 12am, 5: 1pm, 6: 2pm, 7: 3pm, 8: 4pm, 9: 5pm, 10: 6pm, 11: 7pm, 12: 8pm
dic_hours = {'9:00': 1, '10:00': 2, '11:00': 3, '12:00': 4, '13:00': 5, '14:00': 6, '15:00': 7, '16:00': 8, '17:00': 9, '18:00': 10, '19:00': 11, '20:00': 12}
dic_hours_summer = {'9:00': 1, '10:00': 2, '11:00': 3, '12:00': 4, '13:00': 5, '16:00': 6, '17:00': 7, '18:00': 8, '19:00': 9, '20:00': 10}

# Listbox
my_listbox = Listbox(root)
my_listbox.pack(pady=15)

# Add item to Listbox
my_listbox.insert(1,"9:00")
my_listbox.insert(2,"10:00")
my_listbox.insert(3,"11:00")
my_listbox.insert(4,"12:00")
my_listbox.insert(5,"13:00")
#my_listbox.insert(6,"14:00")
#my_listbox.insert(7,"15:00")
my_listbox.insert(6,"16:00")
my_listbox.insert(7,"17:00")
my_listbox.insert(8,"18:00")
my_listbox.insert(9,"19:00")
my_listbox.insert(10,"20:00")

def add():
    global hours
    my_label.config(text=my_listbox.get(ANCHOR))
    hours.append(my_label.cget("text"))
    var_hours.set(f'selected hours: {hours}')
    print(horas)

my_button = Button(root, text="Add Wished Hour", command=add)
my_button.pack(pady=10)

# Show Selected Hour
my_label = Label(root,text="")
my_label.pack(pady=5)

# Show Hours List
var_hours = StringVar()
var_hours.set('selected hours: ')
l_hours = Label(root, textvariable = var_hours)
l_hours.pack()

# Prevent the screen from closing
root.mainloop()


print('paused...')
# Today's date and time
t = datetime.datetime.today()
# Indicate time
future = datetime.datetime(t.year,t.month,t.day,11,59,00)
# Wait until the time entered
pause.until(future)
print('running')

# Data to Fill
my_id = "XXXXX"
email = "XXXXX"
phone = "XXXXX"
current_available_reservations = 0
number_attempts = 0
reservation_successful = False  # Control Variable

while not reservation_successful and number_attempts <= 20:  # Run until a time is successfully booked

    # Add attempt
    number_attempts = number_attempts + 1

    # Enter the website
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("XXXXX")
    time.sleep(3)

    # Enter id
    input_id = driver.find_element(By.XPATH, "//input[@value]")
    input_id.send_keys(my_id)

    # Click on Validate
    click_button = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div/div/div/div/button")
    click_button.click()

    # Choose Hour
    time.sleep(3)
    for hour in hours:
        hour = dic_hours_summer[hour]
        print(hour)
        try:
            button_hour = driver.find_element(By.XPATH, f"//div/div[1]/div[3]/div/div[2]/div/button[{hour}]")
            color_button = button_hour.get_attribute('color')
            print(color_button)
            if color_button == "white" or color_button == "secundary.1":
                button_hour.click()
                validate_time = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div/div[3]")
                validate_time.click()
                print("Selected Hour")
                reservation_successful = True
                break  # Salir del bucle for una vez que se selecciona una hora
        except:
            print("Hour NOT Selected")
            go_back = driver.find_element(By.XPATH, "//div/div[1]/div[2]/button/h1")
            go_back.click()
            continue

    # If a time has been selected successfully, continue with the reservation process
    if reservation_successful:
        # Enter email and phone
        time.sleep(2)
        enter_email = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div[2]/div[3]/div/input")
        enter_email.clear()
        time.sleep(0.25)
        enter_email.send_keys(email)
        enter_phone = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div[2]/div[4]/div/input[@value]")
        enter_phone.send_keys(phone)

        # Accept and Finish
        accept_and_end = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div[2]/button")
        accept_and_end.click()
        time.sleep(2)
        print("Booking Successful")
        break  # Exit the while loop once a time has been reserved
