from typing import Iterable
import scrapy
from bs4 import BeautifulSoup as bs
from ..items import PaniniItem
import unidecode

class Arana(scrapy.Spider):
    name = "arana"

    def start_requests(self):
        lista_palabras = ["berserk"]

        for palabra in lista_palabras:
            url_panini = f"https://tiendapanini.com.mx/catalogsearch/result/index/?p=1&q={palabra}"
            yield scrapy.Request(
                url=url_panini,
                callback=self.encontrar_nuevos_productos,
                meta={
                    "keyword" : palabra,
                    "pagina" : 1
                }
            )
    
    def encontrar_nuevos_productos(self, response):
        palabra = response.meta["keyword"]

        pagina = bs(response.body, "html.parser")

        try:
            if response.meta["pagina"] == 1:
                numero_paginas = len(pagina.find('ul', class_='items pages-items').find_all('li')) - 2
            elif response.meta["pagina"] > 1:
                numero_paginas = len(pagina.find('ul', class_='items pages-items').find_all('li')) - 3
        except AttributeError:
            numero_paginas = 1

        lista_productos = pagina.find_all("li", class_="item product product-item")

        for producto in lista_productos:
            yield scrapy.Request(
                url=producto.a["href"],
                callback=self.parse_datos_producto,
                meta={
                    "keyword" : palabra,
                    "url" : producto.a["href"]
                }
            )

        # Si hay más páginas, sigue navegando por ellas
        for i in range(2, numero_paginas + 1):
            siguiente_pagina_url = f"https://tiendapanini.com.mx/catalogsearch/result/index/?p={i}&q={palabra}"
            yield scrapy.Request(
                url=siguiente_pagina_url,
                callback=self.encontrar_nuevos_productos,
                meta={
                    "keyword" : palabra,
                    "pagina" : i
                }
            )

    def parse_datos_producto(self, response):
        pagina = bs(response.body, "html.parser")

        producto = PaniniItem()

        nombre_producto = unidecode.unidecode(pagina.find("h1", class_="page-title").get_text(strip=True))
        precio = pagina.find("span", class_="price").get_text(strip=True)

        try:
            descripcion_producto = unidecode.unidecode(pagina.find("div", class_="value").p.get_text(strip=True))
        except AttributeError:
            descripcion_producto = ""

        # Manejo de excepciones para evitar errores si no se encuentra algún dato
        try:
            anio_publicacion = pagina.find("td", {"data-th": "Año de publicación"}).get_text(strip=True)
        except AttributeError:
            anio_publicacion = ""

        try:
            mes_publicacion = pagina.find("td", {"data-th": "Mes"}).get_text(strip=True)
        except AttributeError:
            mes_publicacion = ""

        try:
            coleccion = unidecode.unidecode(pagina.find("td", {"data-th": "Colección"}).get_text(strip=True))
        except AttributeError:
            coleccion = ""

        producto["nombre_producto"] =  nombre_producto,
        producto["descripcion_producto"] =  descripcion_producto,
        producto["precio"] = precio, 
        producto["anio_publicacion"] = anio_publicacion,
        producto["mes_publicacion"] = mes_publicacion,
        producto["coleccion"] = coleccion
        producto["url"] = response.meta["url"]

        yield producto
