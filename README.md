# Backend Tech Lead Challenge 


## Problema

En Houm tenemos un gran equipo de Houmers que muestran las propiedades y solucionan todos los problemas que podrían ocurrir en ellas. Ellos son parte fundamental de nuestra operación y de la experiencia que tienen nuestros clientes. Es por esta razón que queremos incorporar ciertas métricas para monitorear cómo operan, mejorar la calidad de servicio y para asegurar la seguridad de nuestros Houmers.


## Requisitos

Crear un servicio REST que:

    Permita que la aplicación móvil mande las coordenadas del Houmer
    Para un día retorne todas las coordenadas de las propiedades que visitó y cuanto tiempo se quedó en cada una
    Para un día retorne todos los momentos en que el houmer se trasladó con una velocidad superior a cierto parámetro


Observaciones:

    El lenguaje de programación debe ser Python. 
    La solución debe ser de calidad de producción
    Incluir instrucciones de cómo ejecutar el código localmente
    Cualquier supuesto que se haya realizado tiene que ser documentado y justificado.
    Tienes 5 días para entregar tu respuesta
    Envíanos tus respuestas en una repo pública al correo techtalent@houm.com con copia a daniela.bustos@houm.com

# Solución
![Screenshot](houm_challenge/images/honest_work.png)

Debo aclarar que aunque he intentado tener en cuenta muchos factores que pueden afectar a la calidad de la solución como mantención del sistema, casos de borde, etc, no he incluido la configuración para el sistema en producción ya que dicha configuración implicaría realizar muchas suposiciones 

## Sistemas/Servidores

Se propone la utilización de sistemas linux y/o containerizados para servir la solución, situados detrás de un balanceador de carga y kubernetes para escalar la cantidad de máquinas que sirven la aplicación en función del tráfico demandado.

La solución implementada utiliza 2 tipos de base de datos para almacenar la información.

- relacional, soporta la arquitectura informacional de django y sus modelos.
- nosql, almacena los datos de serie de tiempo que incluyen la información geográfica.




## Arquitectura de modelos

Las clases implementadas para la solución a modo de presentar un mínimo producto viable són:

- Property, es la entidad utilizada para representar las propiedades.
  - Campos:
    - name: nombre identificado
    - polygon: objeto geográfico
  - Supuestos:
    - Las propiedad está contenida en un polígono de forma que podemos verificar la presencia de un usuario en la propiedad cuando la posición del usuario está dentro del polígono de la propiedad. En cuanto a la representación de la ubicación de la propiedad como punto, se utiliza el centroide.

- Presence, es la entidad utilizada para agregar el tiempo que los houmers están presentes en una propiedad.
  - Campos:
    - user: usuario presente en la propiedad
    - property: propiedad visitada
    - date: fecha de la visita del usuario a la propiedad
    - time_spent: suma de los tiempos que el usuario estuvo en la propiedad 
  - Supuestos:
    - La presencia en la/las propiedades se calcula/agrega 1 vez al día en una tarea asíncrona de celery.

- Setting, es la entidad utilizada para almacenar los settings de la aplicación que pueden cambiar en tiempo de ejecución.
  - Campos:
    - key: clave identificadora del setting
    - value: valor del setting
    - descripction: texto explicativo del setting
  - Supuestos:
    - Para calcular cuando un usuario se mueve mas rápido de una velocidad definida en km/h, se almacena ese valor en un setting.

Pese a no estar desarrolladas adhoc, junto a otras muchos paquetes, quiero destacar el uso de:
- django y django-rest-framework
- el paquete django.contrib.auth.models. Estas clases son la fundación para el sistema de usuarios, autorización y autenticación, grupos y permisos.
- el paquete django.contrib.gis. Ver sección **Consideraciones GIS**.

Para almacenar los datos de serie de tiempo en la base de datos no relacional se utiliza el esquema de campos siguiente:
- original_time: tiempo de la medición para casos en los que el usuario no tenga conexión a internet durante un lapso de tiempo
- insert_time: tiempo de insert en la coleccion
- location: diccionario con datos geográficos
  - lat: latitud
  - lng: longitud
- status: marca de procesamiento del objeto con el fin de no reprocesar datos.


## Componentes/Servicios externalizables

Se propone utilizar servicios externos para alivianar la carga de la máquina o máquinas que ejecutan la aplicación.

Para ello se pueden mover fuera de la máquina los siguientes elementos:
- Base de datos relacional-espacial.
- Base de datos no relacional.
- Redis.
- Workers de celery.
- Recolección de métricas, logs y trazas de excepciones.


## Consideraciones GIS
Para satisfacer los requerimientos de funcionalidades implicadas con sistemas GIS, se ha utilizado el paquete django.contrib.gis.
Con la utilización de este paquete se puede realizar queries geoespaciales, hacer conversiones entre sistemas de referencia y utilizar los modelos con geometrías necesarios para este tipo de operaciones.

Se parte del supuesto que los datos de posición salen de los teléfonos de los houmers, cuyos gps entregan coordenadas geográficas en el [sistema de referencia WGS84](https://en.wikipedia.org/wiki/Geographic_coordinate_system).

Se utiliza un subconjunto de los datos de dicho sistema de referencia, concretamente se utilizan las coordenas latitud y longitud.


## Consideraciones de zona horaria
Todos los tiempos se almacenan como unix timestamp, es decir como número de segundos transcurridos desde 1970-01-01 00:00:00 UTC.


## Consideraciones de autenticación
Para realizar toda petición susceptible de autentificar e identificar al usuario que se vinculará con los datos, se debe incluir un header del tipo:

    {'Authorization': 'Token 060e703af0d766a73f223771db40a710faf09132'}

Para obtener el token se debe realizar una petición POST a ``/api/token/`` con las credenciales del usuario q desea obtener el token:

    {
      'username': 'username_del_usuario',
      'password': 'password_del_usuario'
    }


## Flujo de la aplicación


### Registro de posición
![Screenshot](houm_challenge/images/map_position.png)


El registro de posicion de un houmer se realiza mediante peticiones POST al endpoint ``/api/position/``.

Los parametros de la request son:
- timestamp (obligatorio): es el tiempo en identificador del tiempo en formato unix timestamp
- lat (obligatorio): latitud
- lng (obligatorio): longitud

Dichos campos se validan previamente a la operación de guardado en la base de datos nosql, formateados con el diccionario siguiente:
- original_time: tiempo de la medición para casos en los que el usuario no tenga conexión a internet durante un lapso de tiempo
- insert_time: tiempo de insert en la coleccion
- location: diccionario con datos geográficos
  - lat: latitud
  - lng: longitud
- status: marca de procesamiento del objeto con el fin de no reprocesar datos.


### Presencia en las propiedades
![Screenshot](houm_challenge/images/ouija.png)


Los datos de presencia en propiedades para un día y un usuario se recuperan desde el endpoint con query_params ``/api/presence/`` con el método GET.

Los parametros de la request son:
- user__id (obligatorio): id del usuario a consultar
- date (obligatorio): string con fecha a consultar, formato "YYYY-MM-DD"

El resultado es una lista **paginada** de objetos del tipo:

    {
      'id': 2,                      # id del objeto presence
      'user': 2,                    # id del usuario
      'property': 1,                # id del objeto property
      'property_name': 'Casa 1',    # nombre del objeto property
      'date': '2022-04-19',         # fecha
      'time_spent': 140,            # tiempo registrado dentro del polígono
      'property_centroid': {        # objeto con los datos del punto centroide de la aplicación
        'type': 'Point', 
        'coordinates': [-70.5446686230096, -33.384804669077916]}
    }

Para soportar la funcionalidad requerida se ha creado el modelo **Property** y el modelo **Presence** descritos anteriormente.

Mediante una tarea asíncrona de celery se procesan los datos de la bd nosql cuyo ``status=='pending'``.

Se itera sobre todos los registros pendientes y se realiza una query espacial para ver si las coordenadas del registro están dentro del polígono de alguna propiedad.

Después el objeto presence identificado unívocamente por **user**, **property** y **date**, se utiliza para agregar en el campo **time_spent** la suma de los tiempos entre los pares de registros que están dentro del polígono.

Supuestos: 
- los polígonos de las propiedades no se solapan, pero si lo hacen, el houmer que se encuentre en un lugar donde se solapan más de una propiedad, se registrará como si estuviera en todas esas propiedades a la vez.
- como las queries espaciales pueden ser muy demandantes de recursos se plantea realizarlas en una tarea asíncrona una vez al día en horarios de baja demanda. En un entorno productivo utilizaría celery-beat para programar la tarea periódica, pero en este mvp se debe hacer una petición GET a ``/api/position/`` para disparar el procesamiento de la tarea.


### Monitoreo de límite de velocidad
![Screenshot](houm_challenge/images/speed_limit.png)


Los datos de los tiempos en que el houmer se desplazó con una velocidad superior a cierto parametro se recuperan desde la ruta con parámetros ``/api/safety/speed/`` y el método GET.

Los parametros de la request son:
- user__id (obligatorio): id del usuario a consultar
- date (obligatorio): string con fecha a consultar, formato "YYYY-MM-DD"
- threshold (opcional): umbral o límite de velocidad, si no se informa el parámetro se utilizara el valor del setting max_speed

Los datos entregados por este endpoint son como el siguiente ejemplo:

    {
      'count': 2,
      'results': 
      [
        {
          'user_id': 2,
          'start_utc_time': '2022-01-01T00:02:00',
          'end_utc_time': '2022-01-01T00:03:00',
          'speed_in_km_per_hour': 70.56376871215986},
        },
        {
          'user_id': 2,
          'start_utc_time': '2022-01-01T00:00:00', 
          'end_utc_time': '2022-01-01T00:01:00',
          'speed_in_km_per_hour': 13560.731716960214
        }
      ]
    }


Supuestos:
- el cálculo de la velocidad de desplazamiento se calcula y recalcula de una forma muy parecida al cálculo de la presencia en propiedades, pero debido a que este caso no requiere de queries espaciales, se procesa en el mismo hilo de ejecución. Además de esta forma se puede tener los resultados sin tener que esperar al proceso periódico asíncrono.


## Ejecución de la solución

Estas instrucciones son para sistemas operativo debian 11 o similares.
Se debe contar con un usuario con privilegios de root o de sudo, si sudo esta instalado en el sistema.


#### Clonar repo
``git clone https://github.com/jbci/houm-challenge``

situarse en el directorio:

``cd houm-challenge``


#### Requerimientos de sistema
- [db geoespacial](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/install/geolibs/): para jugar instala spatialite
- [redis](https://redis.io/)
- [python3.9](https://wiki.debian.org/Python)
- [python3.9-venv](https://packages.debian.org/stable/python3-venv)


#### Crear y activar virtualenv
``python3.9 -m venv houm_venv``

``source houm_venv/bin/activate``

para desactivarlo:

``deactivate``


#### Requerimientos python
``pip install -r requirements.txt``


#### Fichero .env
Situate en el directorio settings del proyecto

``cd houm_challenge/houm_challenge/settings``

``cp .env.example .env``


#### Poblar base de datos
Migrate para crear la bd y correr management command creado para esta tarea, situandose en la ruta donde se encuentra el fichero manage.py.

``cd houm-challenge``

``./manage.py migrate``

con un resultado como:

![Screenshot](houm_challenge/images/migrate.png)

``./manage.py populate``

![Screenshot](houm_challenge/images/populate.png)


#### Arrancar worker de celery
En otro terminal/proceso que debe mantenerse en ejecución para el correcto funcionamiento de la aplicación ejecuta:

``celery -A houm_challenge worker -l INFO``

![Screenshot](houm_challenge/images/redis.png)


#### Arrancar el server de desarrollo

``./manage.py runserver``

![Screenshot](houm_challenge/images/runserver.png)


#### Tests
Existen tests unitarios pero se recomienda correr el script end_to_end.py para testear todas las funcionalides.

Desde la ruta raiz del repo:

``cd mocks``

y con el virtualenv activado:

``python end_to_end.py``

![Screenshot](houm_challenge/images/redis.png)


#### debugging
Si algo falla haber elegido correrlo con docker :P

- docker

