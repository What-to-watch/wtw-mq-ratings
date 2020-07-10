# WtW MQ PoC

Este es un PoC para mostrar como se podría manejar una situación con alto throughput de ratings sin escalar necesariamente la BD. El mecanismo seleccionado para manejar este requerimiento fue el uso de kafka para servir de de message queue (MQ); esta se utiliza como mecanismo para desacoplar el envio de ratings y la eventual persistencia en la base de datos. 

Aunque este es un PoC trata de mostrar cuales serían los componentes en la solución propuesta. Los componentes en el PoC corresponden a diferentes contenedores de docker; estos se pueden identificar en los diferentes servicios que se encuentran en el `./docker-compose.yml`. Los componentes de la solución son los siguientes:

- **Persistencia:** Este es el componente que posee la restricción de no replicable para manejar elce alto flujo de datos. Este corresponde al servicio de *docker-compose* `db`. La base de datos es postgresSQL para emular el ambiente en producción actual. 

- **Kafka/Zookeper:** Aunque Kafka y Zookeper son servicios por separados dentro de *docker-compose* (`kafka` y `zookeeper`) juntos funcionan para brindar las capacidades de cola de mensaje para la aplicación. Para obtener información detallada de kafka lo pueden hacer a traves de la [documentación](https://kafka.apache.org/). Kafka esta diseñado para funcionar en clusters y utiliza zookeper para registrarse y encontrar los otros brokers. Zookeper es un servicio para *service discovery* y como se menciono ayuda a los nodos de kafka a encontrarse entre ellos. Kafka permite manejar alta cantidad de mensajes debido a su posibilidad de replicarse y por esto fue seleccionado para este use case.

- **Service(Producer):** Este componente tiene como unica funcionalidad exoner un endpoint (se mostrara más adelante como acceder a el). Este se puede agregar dentro de la aplicación existente ya que solamente deja un mensaje en kafka. Este corresponde al servicio de *docker-compose* `service`

- **Subscriber:** Este es el nuevo componente dentro de la arquitectura que se encarga de leer los mensajes producto de la cola de mensajes de kafka. Actualmente tiene un scope limitado pero es facil implementar un mecanismo que utilice varias conexiones a la base de datos para aumentar el performance. Este componente puede limitar la cantidadde mensajes que se aceptan y evitar que la base de datos no pueda manejar el flujo de mensajes directo.

## Deploy

### Pre-requisites
El despliegue como se menciono esta basado en docker-compose. Esta herramienta es parte del toolkit de docker, entonces si ya lo tienen instalado no debería ser necesario instalar nada más para realizar el despliegue.

### Deployment

Despues de clonar el repositorio solo es necesario ejecutar lo siguiente para levantar la arquitectura:

`docker-compose up -d`

***Nota:*** Un problema actual es que el contendor de kafka no esta listo para aceptar conexiones (aunque los otros contenedores declaran la dependencia). Se puede esperar un momento y despues correr de nuevo el comando para volver a levantar los servicios. Pueden validar que ese sea el problema ejecutando `docker-compose logs <subscriber|service>`; si ese es el problema veran un mensaje de `No Availables Brokers`

Despues de que ya estan levantado los contendores se necesita crear manualmente el topic en kafka ya que la imagen no soporta crear topicos a traves del `docker-compose.yml`- Pueden ejecutar el siguiente comando para crear el topic dentro del contenedor de kafka 

`docker-compose exec kafka kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic movie-ratings`

Las particiones y el factor de replicacion se colocan en 1 ya que se tiene solamente una instancia de kafka corriendo en este PoC. Estos valores se pueden ajustar cuando se este corriendo un cluster completo.

Una vez creado el topic ya pueden enviar peticiones al servicio. El mensaje generado será reicibido por el subscriber y será persistido en la base de datos. La peticion (usando curl es la siguiente):

`curl --location --request GET 'localhost:5000/rate' --header 'Content-Type: application/json' --data-raw '{
    "user_id":4,
    "movie_id":3,
    "rating":4
}'`

Los nombres de los campos se explican por si solos.

Para validar que el mensaje quedó en la BD pueden conectarse a postgres usando el mecanismo de su preferencia. La base de datos expone el puerto 6423 y pueden usar la info dentro del `docker-compose.yml` para la clave y el usuario. 

***Nota:*** Durante las pruebas se utilizo pgadmin para probar ya que se tiene instalado postgresSQL localmente. Pero cualquier herramiento se puede usar para validar que la info quedé correctamente desplegada.