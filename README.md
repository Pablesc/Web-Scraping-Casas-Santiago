# Proyecto Web Scraping Casas Santiago

Proyecto enfocado en la extracción de datos de las casas en venta usadas de la región metropolitana desde [Portal Inmobiliario](https://www.portalinmobiliario.com/venta/casa/propiedades-usadas/metropolitana).

## Descripción

Se extraen un total de 76 variables correspondientes a cada una de las casas, las cuales se presentan a continuación:

### Datos sin tabla:

- Precio
- Comuna

Las tablas siguientes corresponden a la sección **Características del inmueble**.

### Tabla Principal:

- Superficie total
- Superficie útil
- Dormitorios
- Baños
- Estacionamientos
- Bodegas
- Cantidad de pisos
- Tipo de casa
- Antigüedad
- Gastos comunes

### Tabla Ambientes:

- Quincho
- Piscina
- Closets
- Baño de visitas
- Terraza
- Comedor
- Walk-in clóset
- Homeoffice
- Living
- Patio
- Dormitorio en suite
- Balcón
- Mansarda
- Jardín
- Cocina
- Dormitorio y baño de servicio
- Playroom
- Logia
- Desayunador

### Tabla Comodidades y equipamiento:

- Chimenea
- Gimnasio
- Jacuzzi
- Estacionamiento de visitas
- Área de cine
- Área de juegos infantiles
- Con área verde
- Ascensor
- Cancha de básquetbol
- Con cancha de fútbol
- Cancha de paddle
- Cancha de tenis
- Con cancha polideportiva
- Salón de fiestas
- Sauna
- Refrigerador

### Tabla Condiciones especiales:

- Amoblado

### Tabla Servicios:

- Acceso a internet
- Aire acondicionado
- Calefacción
- TV por cable
- Línea telefónica
- Gas natural
- Generador eléctrico
- Con energia solar
- Con conexión para lavarropas
- Agua corriente
- Cisterna
- Caldera

### Tabla Seguridad:

- Alarma
- Conserjería
- Portón automático
- Con condominio cerrado
- Acceso controlado

En la tabla Principal las variables toman valores numéricos o texto, en cambio, en el resto de tablas las variables toman un valor binario.

Se debe destacar que la sección **Características del inmueble** en algunas ocasiones presenta un formato distinto, es decir, el código fue desarrollado para abarcar los dos formatos posibles dependiendo de cual se presente en el browser.

A continuación se presentan los datos extraídos de las tablas correspondientes a la sección **Información de la zona**:

### Tabla Transporte

- Estaciones de metro 
- Paraderos

### Tabla Educación

- Jardines infantiles 
- Colegios 
- Universidades

### Tabla Áreas verdes

- Plazas

### Tabla Comercios

- Supermercados 
- Farmacias 
- Centros comerciales

### Tabla Salud

- Hospitales 
- Clínicas

Las variables de estas tablas toman valores numéricos (discretos) de 0 a 5 y representan los puntos mas cercanos a la casa en un rango de 2 kilometros.
