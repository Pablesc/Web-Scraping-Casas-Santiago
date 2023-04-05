from bs4 import BeautifulSoup
import requests
import pandas as pd
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import time

#Este url contiene todas las comunas de la RM
url_principal = 'https://www.portalinmobiliario.com/venta/casa/propiedades-usadas/metropolitana/_NoIndex_True_FiltersAvailableSidebar?filter=city'

#Función para obtener información de la página de manera desorganizada.
def data(url):
    html_texto = requests.get(url).text
    soup = BeautifulSoup(html_texto, 'lxml')
    return soup

#Función para determinar la url de cada una de las comunas de la RM
def urls_por_comuna(soup):
    #Lista de comunas de la RM
    comunas = soup.find('div', class_ = 'ui-search-search-modal-grid-columns')
    urls_por_comuna = []
    for comuna in comunas:
        nombre_comuna = unidecode(comuna.find('span', class_ = 'ui-search-search-modal-filter-name').text.replace(' ','-'))
        if nombre_comuna == 'Tiltil':
           url_cada_comuna = 'https://www.portalinmobiliario.com/venta/casa/propiedades-usadas/til-til-metropolitana'
        else:
            url_cada_comuna = 'https://www.portalinmobiliario.com/venta/casa/propiedades-usadas/' + nombre_comuna + '-metropolitana/_NoIndex_True'
        
        #Se genera una restricción para separar por filtro de precios si las páginas tienen mas de 2000 resultados
        soup_por_comuna = data(url_cada_comuna)

        resultados_por_comuna = soup_por_comuna.find('span', class_ = 'ui-search-search-result__quantity-results shops-custom-secondary-font').text.replace('.','')
        resultados = [int(x) for x in resultados_por_comuna.split() if x.isdigit()]

        if resultados[0] > 2000:
            comunas_con_filtro = soup_por_comuna.find_all('li', class_ = 'ui-search-money-picker__li')
            for ciudad in comunas_con_filtro:
                url_casa_filtro = ciudad.a['href']
                urls_por_comuna.append(url_casa_filtro)
        else:
            urls_por_comuna.append(url_cada_comuna)
    return  urls_por_comuna

#Función para obtener la página siguiente    
def pag_sig(soup):
    page_principal = soup.find('ul', class_ = 'ui-search-pagination andes-pagination shops__pagination')
    if not page_principal or not page_principal.find('li', class_ = 'andes-pagination__button andes-pagination__button--next shops__pagination-button'):
        return
    else:
        url_pag_sig = page_principal.find('li', class_ = 'andes-pagination__button andes-pagination__button--next shops__pagination-button').a['href']
        return url_pag_sig

#Función para obtener los datos de cada casa de una url (página web)
def variables(soup_principal):
    options = webdriver.ChromeOptions() 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')
    service = Service('driver/chromedriver.exe') 
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(5)
    wait = WebDriverWait(driver, 1)
    
    datos_casas = []
    
    #Se ubican todas las casas dentro de la página
    casas = soup_principal.find_all('li', class_ = 'ui-search-layout__item shops__layout-item')
    for casa in casas:
        #Se obtiene la url de cada casa
        url_cada_casa = casa.div.div.a['href']
        try:
            driver.get(url_cada_casa)
            content = driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(content, 'lxml')
            
            #Se obtienen los datos sin tabla
            cada_casa = soup.find('div', class_ = 'ui-pdp-price__second-line')
            precio_casa = cada_casa.span.span.text

            comuna = soup.find_all('a', class_ = 'andes-breadcrumb__link')
            comuna_x_casa = comuna[4].text

            datos_otros = {
                'Precio': precio_casa,
                'Comuna': comuna_x_casa
                #'url': url_cada_casa
            }
            #Se establece condicional determinar si esta en formato antiguo
            formato = soup.find('h2', class_ = 'ui-pdp-specs__title')
            if formato is not None:

                #Se define este scroll para posicionar la pantalla en la tabla "Características del inmueble"
                scroll = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-pdp-specs__table')))
                driver.execute_script("arguments[0].scrollIntoView();",scroll)

                datos_tablas = {
                    'Superficie total': None, 
                    'Superficie útil': None, 
                    'Dormitorios': None, 
                    'Baños': None, 
                    'Estacionamientos': None, 
                    'Bodegas': None, 
                    'Cantidad de pisos': None, 
                    'Tipo de casa': None, 
                    'Antigüedad': None, 
                    'Gastos comunes': None
                }
                
                #Extracción de data de la tabla principal en formato antiguo
                datos_mostrados = soup.find_all('tr', class_ = 'andes-table__row')

                for datos in datos_mostrados:
                    encabezado = datos.find('th', class_ = 'andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title').text

                    for caracteristica in datos_tablas.keys():
                        if encabezado == caracteristica:
                            datos_tablas[caracteristica] = datos.td.span.text

                datos_tablas_inmueble = {
                        'Ambientes': {
                            'Quincho': 'No',
                            'Piscina': 'No',
                            'Closets': 'No',
                            'Baño de visitas': 'No',
                            'Terraza': 'No',
                            'Comedor': 'No',
                            'Walk-in clóset': 'No',
                            'Homeoffice': 'No',
                            'Living': 'No',
                            'Patio': 'No',
                            'Dormitorio en suite': 'No',
                            'Balcón': 'No',
                            'Mansarda': 'No',
                            'Jardín': 'No',
                            'Cocina': 'No',
                            'Dormitorio y baño de servicio': 'No',
                            'Playroom': 'No',
                            'Logia': 'No',
                            'Desayunador': 'No'
                        },

                        'Comodidades y equipamiento': {
                            'Chimenea': 'No',
                            'Gimnasio': 'No',
                            'Jacuzzi': 'No',
                            'Estacionamiento de visitas': 'No',
                            'Área de cine': 'No',
                            'Área de juegos infantiles': 'No',
                            'Con área verde': 'No',
                            'Ascensor': 'No',
                            'Cancha de básquetbol': 'No',
                            'Con cancha de fútbol': 'No',
                            'Cancha de paddle': 'No',
                            'Cancha de tenis': 'No',
                            'Con cancha polideportiva': 'No',
                            'Salón de fiestas': 'No',
                            'Sauna': 'No',
                            'Refrigerador': 'No'
                        },

                        'Condiciones especiales': {
                            'Amoblado': 'No'
                        },

                        'Servicios': {
                            'Acceso a internet': 'No',
                            'Aire acondicionado': 'No',
                            'Calefacción': 'No',
                            'TV por cable': 'No',
                            'Línea telefónica': 'No',
                            'Gas natural': 'No',
                            'Generador eléctrico': 'No',
                            'Con energia solar': 'No',
                            'Con conexión para lavarropas': 'No',
                            'Agua corriente': 'No',
                            'Cisterna': 'No',
                            'Caldera': 'No'
                        },

                        'Seguridad': {
                            'Alarma': 'No',
                            'Conserjería': 'No',
                            'Portón automático': 'No',
                            'Con condominio cerrado': 'No',
                            'Acceso controlado': 'No'
                        }           
                        
                    }               

                try:
                    #Se posiciona la pantalla en las tablas
                    scroll = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-pdp-specs__tabs')))
                    driver.execute_script("arguments[0].scrollIntoView();", scroll)

                    botones_tablas = driver.find_elements(By.CLASS_NAME, 'andes-tab__link')

                    #Este bloque va a seleccionar todas las pestañas de todas las tablas, es decir de la tabla del inmueble e info zona
                    #Por eso solo se extraen los botones del inmueble a ser clickeados.
                    botones_tabla_inmueble = []
                    for boton_tabla in botones_tablas:
                        encabezado = boton_tabla.text
                        if encabezado == 'Ambientes' or encabezado == 'Comodidades y equipamiento' or encabezado == 'Condiciones especiales' or encabezado == 'Servicios' or encabezado == 'Seguridad':
                            botones_tabla_inmueble.append(boton_tabla)

                    #Extracción de datos de la tabla Ambientes, Comodidades y equipamiento, Condiciones especiales, Servicios y Seguridad 
                    for boton_tabla in botones_tabla_inmueble:
                        boton_tabla.click()
                        encabezado = boton_tabla.text
                        try:
                            contenido = driver.find_element(By.CLASS_NAME, 'andes-tab-content')
                            no_negritas = contenido.find_elements(By.CLASS_NAME, 'ui-pdp-color--BLACK.ui-pdp-size--XSMALL.ui-pdp-family--REGULAR')
                            for titulo, valor in datos_tablas_inmueble.items():
                                if encabezado == titulo:
                                    for no_negrita in no_negritas:
                                        no_negrita_t = no_negrita.text
                                        for sub_titulo in valor.keys():
                                            if no_negrita_t == sub_titulo:
                                                datos_tablas_inmueble[titulo][sub_titulo] = 'Si'

                        except NoSuchElementException:
                            continue

                        if len(botones_tabla_inmueble) == 5 and boton_tabla == botones_tabla_inmueble[2]:
                            #hay que esperar un tiempo para que se mueva el scroll horizontal del elemento
                            time.sleep(1)
                            flecha = driver.find_element(By.XPATH, '//div[@class="andes-tabs__scroll-tool--controls"]/*[name()="svg"][@class="control-arrow"]')
                            flecha.click()
                            time.sleep(1)
                                      
                except TimeoutException:
                    pass
                
                for titulo, valor in datos_tablas_inmueble.items():
                    for sub_titulo, sub_valor in valor.items():
                        datos_tablas[sub_titulo] = sub_valor

            #Si esta en formato nuevo entra en este else
            else:
                
                scroll = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-pdp-collapsable__action')))
                driver.execute_script("arguments[0].scrollIntoView();", scroll)

                tablas = driver.find_element(By.CLASS_NAME, 'ui-pdp-collapsable__action')
                tablas.click()
                
                datos_tablas = {
                        #Tabla principal
                        'Superficie total': None, 
                        'Superficie útil': None, 
                        'Dormitorios': None, 
                        'Baños': None, 
                        'Estacionamientos': None, 
                        'Bodegas': None, 
                        'Cantidad de pisos': None, 
                        'Tipo de casa': None, 
                        'Antigüedad': None, 
                        'Gastos comunes': None,
                        #Tabla seguridad
                        'Alarma': 'No',
                        'Conserjería': 'No',
                        'Portón automático': 'No',
                        'Con condominio cerrado': 'No',
                        'Acceso controlado': 'No',
                        #Tabla ambiente
                        'Quincho': 'No',
                        'Piscina': 'No',
                        'Closets': 'No',
                        'Baño de visitas': 'No',
                        'Terraza': 'No',
                        'Comedor': 'No',
                        'Walk-in clóset': 'No',
                        'Homeoffice': 'No',
                        'Living': 'No',
                        'Patio': 'No',
                        'Dormitorio en suite': 'No',
                        'Balcón': 'No',
                        'Mansarda': 'No',
                        'Jardín': 'No',
                        'Cocina': 'No',
                        'Dormitorio y baño de servicio': 'No',
                        'Playroom': 'No',
                        'Logia': 'No',
                        'Desayunador': 'No',
                        #Tabla servicios
                        'Acceso a internet': 'No',
                        'Aire acondicionado': 'No',
                        'Calefacción': 'No',
                        'TV por cable': 'No',
                        'Línea telefónica': 'No',
                        'Gas natural': 'No',
                        'Generador eléctrico': 'No',
                        'Con energia solar': 'No',
                        'Con conexión para lavarropas': 'No',
                        'Agua corriente': 'No',
                        'Cisterna': 'No',
                        'Caldera': 'No',
                        #Tabla de comodidades y equipamiento
                        'Chimenea': 'No',
                        'Gimnasio': 'No',
                        'Jacuzzi': 'No',
                        'Estacionamiento de visitas': 'No',
                        'Área de cine': 'No',
                        'Área de juegos infantiles': 'No',
                        'Con área verde': 'No',
                        'Ascensor': 'No',
                        'Cancha de básquetbol': 'No',
                        'Con cancha de fútbol': 'No',
                        'Cancha de paddle': 'No',
                        'Cancha de tenis': 'No',
                        'Con cancha polideportiva': 'No',
                        'Salón de fiestas': 'No',
                        'Sauna': 'No',
                        'Refrigerador': 'No',
                        #Tabla de condiciones especiales
                        'Amoblado': 'No'
                    }
                
                #Extracción de datos de la tabla Principal, Ambientes, Comodidades y equipamiento, Condiciones especiales, Servicios y Seguridad en el formato nuevo
                datos_mostrados = soup.find_all('tr', class_ = 'andes-table__row ui-vpp-striped-specs__row')
                
                for datos in datos_mostrados:
                   
                    encabezado = datos.find('th', class_ = 'andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id').text    

                    for caracteristica in datos_tablas.keys():
                        if encabezado == caracteristica:
                            datos_tablas[caracteristica] = datos.td.span.text

            #Extracción de datos de las tablas de la sección Información de la zona           
            #Diccionario donde se almacena la información de la sección 'Información de la zona'
            datos_tabla_info_zona = {
                'Transporte': {'Estaciones de metro': 0, 'Paraderos': 0},
                'Educación': {'Jardines infantiles': 0, 'Colegios': 0, 'Universidades': 0},
                'Áreas verdes': {'Plazas': 0},
                'Comercios': {'Supermercados': 0, 'Farmacias': 0, 'Centros comerciales': 0},
                'Salud': {'Hospitales': 0, 'Clínicas': 0}
            }

            try:
                
                botones = driver.find_elements(By.CLASS_NAME, 'ui-vip-poi__tab-title')
                driver.execute_script("arguments[0].scrollIntoView();", botones[0])

                for boton in botones:
                    encabezado = boton.text
                    boton.click()

                    for titulo, valor in datos_tabla_info_zona.items():
                        if encabezado == titulo:
                            sub_secciones = driver.find_elements(By.XPATH, "//div[@class='ui-vip-poi__subsection']")
                            for sub_seccion in sub_secciones:
                                sub_encabezado = sub_seccion.find_element(By.XPATH, ".//span[@class='ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--SEMIBOLD ui-vip-poi__subsection-title']")
                                sub_encabezado_t = sub_encabezado.text
                                for sub_titulo in valor.keys():
                                    if sub_encabezado_t == sub_titulo:
                                        items = sub_seccion.find_elements(By.CLASS_NAME, 'ui-vip-poi__item')
                                        datos_tabla_info_zona[titulo][sub_titulo] = len(items)

            except NoSuchElementException:
                pass

            for titulo, valor in datos_tabla_info_zona.items():
                for sub_titulo, sub_valor in valor.items():
                    datos_tablas[sub_titulo] = sub_valor
            
            datos_unificados = {**datos_otros, **datos_tablas}

            datos_casas.append(datos_unificados)
        except requests.TooManyRedirects:
            continue
        except AttributeError:
            continue
        except TimeoutException:
            continue
        except IndexError:
            continue

    driver.quit()
    return datos_casas

#Se define la lista en donde se guardaran todos los datos
datos_casas = []

#Página principal 
soup = data(url_principal)
urls_comunas = urls_por_comuna(soup)

for url_comuna in urls_comunas:
    while True:
        #Extraer data de la página de la comuna
        soup_por_comuna = data(url_comuna)
        
        #Guardar la url de la pagina siguiente de la misma comuna
        url_comuna = pag_sig(soup_por_comuna)
        
        #Guardar los datos de todas las variables
        datos_casa = variables(soup_por_comuna)
        datos_casas += datos_casa

        df = pd.DataFrame(datos_casas)
        print(df)

        if not url_comuna:
            break

df.to_csv('datos_casas_santiago.csv', encoding='latin1', index=False)

