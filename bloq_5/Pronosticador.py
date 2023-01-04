from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


def crear_driver(website: str, path: str):

    # website será el link de la página web de cuotas que querremos navegar
    # para realizar la predicción del ganador del próximo partido. path será
    # un string con la ruta completa en la que está alojado el driver, que
    # previamente deberemos habernos descargado en nuestro ordenador.
    # Con ello creamos un driver para poder navegar la página web y lo
    # devolvemos para usarlo más adelante

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(website)  # Llamamos a la página web

    return driver


def dirigirse_cuotas(driver: webdriver.Chrome):

    # Usando el driver que ya hemos creado y pasado como argumento a esta
    # función, navegamos la página web de apuestas deportivas en busca del
    # apartado de la NBA. Para ello tendremos que ir pulsando en la página web
    # sucesivas veces, determinando dónde pulsar con el XPATH.

    # Dar el consentimiento de que somos mayores de edad
    driver.implicitly_wait(10)
    consentimiento = driver.find_element(By.XPATH,
                                         '//*[@id="logo-box"]/div[2]/a')
    consentimiento.click()
    time.sleep(1)

    # Aceptar las cookies
    driver.implicitly_wait(10)
    cookies = driver.find_element(By.XPATH,
                                  '/html/body/div[4]/div/div[2]/button')
    cookies.click()
    time.sleep(1)

    # Abri el menú de la página web
    driver.implicitly_wait(10)
    m = driver.find_element(By.XPATH,
                            '/html/body/div[1]/div[1]/header/div/div[1]/label')
    m.click()
    time.sleep(1)

    # Ir al apartado de pronósticos
    driver.implicitly_wait(10)
    prn = driver.find_element(By.XPATH,
                              '/html/body/div[1]/div[1]/header/nav/ul/li[3]/a')
    prn.click()
    time.sleep(1)

    # Seleccionar el deporte, baloncesto
    driver.implicitly_wait(10)
    basket = driver.find_element(By.XPATH, '//*[@id="style-4"]/div[4]/a')
    basket.click()
    time.sleep(1)

    # Seleccionar la liga de baloncesto, NBA
    driver.implicitly_wait(10)
    nba = driver.find_element(By.XPATH, '//*[@id="cal-section"]/div[1]/div[1]')
    nba.click()
    time.sleep(1)

    # Contamos cuantos partidos se nos muestran en la página web, típicamente
    # son 11, pero con esto determinamos de forma exacta por si varía

    driver.implicitly_wait(10)
    match = driver.find_element(By.XPATH, '//*[@id="cal-section"]/div[1]')
    num = int(len(match.text.split('\n'))/6)
    time.sleep(1)

    return num  # Devolvemos el número de partidos


def obtener_cuotas(driver: webdriver.Chrome, num: int, equipo: str):

    # Buscamos un equipo en la web, obtenemos su partido más cercano si existe,
    # su rival y las cuotas. Preguntamos al usuario si quiere obtener una
    # predicción de algún otro equipo. Para movernos y buscar en la página web
    # seguiremos usando el XPATH de los elementos deseados

    equipo_local = None

    for i in range(1, num+1):  # Buscamos en cada partido de la web

        driver.implicitly_wait(10)
        info = driver.find_element(By.XPATH,
                                   f'//*[@id="cal-section"]/div[1]/div[{i}]/span/span[2]/a').text
        comparar = info.lower()
        derecha = ('- ' + equipo).lower()
        izquierda = (equipo + ' -').lower()

    # Para ver si el equipo que buscamos es local o visitante, y determinar
    # por tanto que el equipo contra el que juega es visitante o local
    # respectivamente, buscamos teniendo en cuenta el guión que aparece
    # siempre entre ambos equipos

        if derecha in comparar:

            equipos = info.split(' - ')
            posicion = i
            equipo_local = equipos[0]
            equipo_visitante = equipos[1]
            driver.implicitly_wait(10)
            local = False
            break

        elif izquierda in comparar:

            equipos = info.split(' - ')
            posicion = i
            equipo_local = equipos[0]
            equipo_visitante = equipos[1]
            local = True
            break

    # Si se ha encontrado un partido del equipo, buscamos e imprimimos las
    # cuotas para dicho partido

    if equipo_local:

        cuota_local = driver.find_element(By.XPATH,
                                          f'//*[@id="cal-section"]/div[1]/div[{posicion}]/div/a[1]/span[2]').text
        cuota_visitante = driver.find_element(By.XPATH,
                                              f'//*[@id="cal-section"]/div[1]/div[{posicion}]/div/a[2]/span[2]').text

        # Deberemos distinguir entre si el equipo que hemos buscado es local o
        # visitante para así imprimir el partido por pantalla de la forma
        # equipo_local vs equipo_visitante

        if local:
            print(f'El partido más cercano de los {equipo_local} es '
                  f'{equipo_local}(local) vs {equipo_visitante}(visitante)')

        else:
            print(f'El partido más cercano de los {equipo_visitante} es '
                  f'{equipo_local}(local) vs {equipo_visitante}(visitante)')

        # Imprimimos las cuotas de ambos equipos

        print(f'Las cuotas correspondientes a ambos equipos son {equipo_local}'
              f': {cuota_local} y {equipo_visitante}: {cuota_visitante}')

        # Ahora debemos comparar la cuota del equipo local con la cuota del
        # equipo visitante, distinguiendo una vez más si el equipo que
        # buscábamos es local o visitante en el partido. Tendremos 2 posibles
        # opciones (local, visitante) * 3 posibles comparaciones de cuotas
        # (>, <, =), 6 opciones en total

        if local and cuota_local < cuota_visitante:
            print(f'Es más probable que los {equipo_local} ganen como locales '
                  f'su próximo partido frente a los {equipo_visitante}\n')

        elif not local and cuota_visitante < cuota_local:
            print(f'Es más probable que los {equipo_visitante} ganen fuera de '
                  f'casa su próximo partido frente a los {equipo_local}\n')

        elif local and cuota_local > cuota_visitante:
            print(f'Es más probable que los {equipo_local} pierdan como '
                  'locales su próximo partido frente a los '
                  f'{equipo_visitante}\n')

        elif not local and cuota_visitante > cuota_local:
            print(f'Es más probable que los {equipo_visitante} pierdan fuera '
                  f'de casa su próximo partido frente a los {equipo_local}\n')

        elif local and cuota_local == cuota_visitante:
            print(f'El próximo partido de los {equipo_local} será en casa y '
                  f'estará muy reñido frente a los {equipo_visitante}\n')

        elif not local and cuota_local == cuota_visitante:
            print(f'El próximo partido de los {equipo_visitante} será fuera de'
                  f' casa y estará muy reñido frente a los {equipo_local}\n')

    else:

        # Si no hemos encontrado el equipo en la web, es que no va a jugar
        # ningún partido próximamente, o puede que el nombre del equipo se
        # haya introducido de manera incorrecta

        print(f'Los {equipo} no jugarán ningún partido próximamente.\n')

    # Ahora preguntamos al usuario si desea realizar una predicción para algún
    # otro equipo, si dice que no se acabará la función, y si dice que sí se
    # le preguntará el nombre del equipo y se volverá a llamar a esta misma
    # función con este nuevo equipo como argumento

    nuevo = input('Desea realizar una predicción de otro equipo? (Si/No): ')

    while nuevo not in ['Si', 'No', 'si', 'no', 'Sí', 'sí']:
        nuevo = input('Por favor, introduzca una opción correcta (Si/No): ')

    if nuevo == 'Si' or nuevo == 'si' or nuevo == 'Sí' or nuevo == 'sí':
        equipo = input('Introduzca el nombre completo del equipo: ')
        obtener_cuotas(driver, num, equipo)


def pronostica(equipo: str):

    # Para un cierto equipo que se pasa como argumento a la función, crea un
    # driver para navegar por la página web de apuestas deportivas y obtiene
    # las cuotas del próximo partido de ese equipo. Además permite al usuario
    # solicitar más predicciones sobre otros equipos, en caso de que por
    # ejemplo, el equipo inicial no juegue partidos próximamente

    website = 'https://www.sportytrader.es/'
    path = eval(open('config.txt').read())['path']
    driver = crear_driver(website, path)
    num = dirigirse_cuotas(driver)
    obtener_cuotas(driver, num, equipo)