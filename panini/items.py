# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PaniniItem(scrapy.Item):
    nombre_producto = scrapy.Field()
    descripcion_producto = scrapy.Field()
    precio = scrapy.Field()
    anio_publicacion = scrapy.Field()
    mes_publicacion = scrapy.Field()
    coleccion = scrapy.Field()
    url = scrapy.Field()