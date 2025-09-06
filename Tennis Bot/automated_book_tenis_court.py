from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pause
import datetime
from tkinter import *

# Choose Hours Panel
root = Tk()
root.title("Reserva Hora Tenis Parque Araucano")
root.geometry("400x400")
horas = []  # Lista para almacenar horas seleccionadas
dic_hours = {'9:00': 1, '10:00': 2, '11:00': 3, '12:00': 4, '13:00': 5, '14:00': 6, '15:00': 7, '16:00': 8, '17:00': 9, '18:00': 10, '19:00': 11, '20:00': 12}
dic_hours_summer = {'9:00': 1, '10:00': 2, '11:00': 3, '12:00': 4, '13:00': 5, '16:00': 6, '17:00': 7, '18:00': 8, '19:00': 9, '20:00': 10}

# Listbox
my_listbox = Listbox(root)
my_listbox.pack(pady=15)

# Add items to Listbox
for i, hora in enumerate(dic_hours_summer.keys(), 1):
    my_listbox.insert(i, hora)

def add():
    my_label.config(text=my_listbox.get(ANCHOR))
    horas.append(my_label.cget("text"))
    var_hours.set(f'Horas seleccionadas: {horas}')
    print(horas)

my_button = Button(root, text="Agregar Hora Deseada", command=add)
my_button.pack(pady=10)

# Show Selected Hour
my_label = Label(root, text="")
my_label.pack(pady=5)

# Show Hours List
var_hours = StringVar()
var_hours.set('Horas seleccionadas: ')
l_hours = Label(root, textvariable=var_hours)
l_hours.pack()

# Prevent the screen from closing
root.mainloop()

print('Esperando para ejecutar...')

# Esperar hasta hora deseada
t = datetime.datetime.today()
future = datetime.datetime(t.year, t.month, t.day, 5, 9, 0)
pause.until(future)
print('Ejecutando...')

# Datos personales
my_id = "XXXXX"
email = "XXXXX"
phone = "XXXXX"

current_available_reservations = 0
number_attempts = 0
reservation_successful = False

while not reservation_successful and number_attempts <= 20:
    number_attempts += 1
    print(f"Intento número: {number_attempts}")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print(f"Error iniciando el navegador: {e}")
        break

    try:
        driver.get("XXXXX")
        time.sleep(3)

        # Ingresar RUT
        input_id = driver.find_element(By.XPATH, "//input[@value]")
        input_id.send_keys(my_id)

        # Click en validar
        click_button = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div/div/div/div/button")
        click_button.click()

        # Esperar a que cargue
        time.sleep(3)

        for hora in horas:
            index_hora = dic_hours_summer.get(hora)
            print(f"Intentando reservar hora: {hora} (índice {index_hora})")

            try:
                button_hour = driver.find_element(By.XPATH, f"//div/div[1]/div[3]/div/div[2]/div/button[{index_hora}]")
                color_button = button_hour.get_attribute('color')
                print(f"Color del botón: {color_button}")

                if color_button in ["white", "secundary.1"]:
                    button_hour.click()
                    time.sleep(1)

                    try:
                        validate_time = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div/div[3]")
                        validate_time.click()
                        print("Hora seleccionada correctamente")
                        reservation_successful = True
                        break
                    except:
                        print("No se pudo validar la hora")
            except:
                print("Hora no disponible o botón no encontrado")

                try:
                    go_back = driver.find_element(By.XPATH, "//div/div[1]/div[2]/button/h1")
                    go_back.click()
                    time.sleep(1)
                except:
                    print("No se pudo volver atrás")
                    continue

        if reservation_successful:
            try:
                time.sleep(2)
                enter_email = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div[2]/div[3]/div/input")
                enter_email.clear()
                time.sleep(0.25)
                enter_email.send_keys(email)

                enter_phone = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div[2]/div[4]/div/input[@value]")
                enter_phone.send_keys(phone)

                accept_and_end = driver.find_element(By.XPATH, "//div/div[1]/div[3]/div[2]/button")
                accept_and_end.click()
                time.sleep(2)
                print("Hora reservada con éxito")
                break
            except:
                print("Error al completar los datos finales")

    except Exception as e:
        print(f"Ocurrió un error durante el intento: {e}")

    finally:
        driver.quit()
