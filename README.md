Integrantes:
- Francisco Aybar 
- Joaquin Castellano
- Santiago Martin



INTELIGATE

IDEA DEL PROYECTO:
	La idea de este proyecto es de crear un sistema de análisis de patentes en distintos vehículos 
  para permitir o no el paso de este, mediante un sistema de barreras, actúa similarmente a un 
  telepeaje en el que la persona al ingresar al área, ingresara su patente en una consola, si la 
  patente se encuentra en el sistema de usuarios de telepeaje con pago al dia, se analizará el vehículo 
  (acorde a su tipo será el pago cobrado) y si esta al dia, se levantara la barrera permitiendo el paso 
  (luz verde), sino, la barrera no se levantara, se prenderá una luz roja, se activará una alarma y un 
  cartel. También se incluirá un manejo de la barrera manual en caso de emergencias, como el de ambulancias 
  y/o policía.

PYTHON - QT DESIGNER:
	La parte que se desarrollará en python y qt designer será la de el ingreso de la patente (utilizando un 
  teclado matricial en el cual el usuario ingresa su dni y se busca el auto a su nombre), la búsqueda de esta 
  en el sistema (utilizando diccionarios de python para analizar el auto, dni, precio y el gmail del usuario) 
  y su respectivo precio dependiendo el tipo de vehículo (moto, auto, camión), el retorno de si se encuentra 
  o no (dará true si si, lo que levantara la barrera, o false si no, lo que no la levantara, activará la 
  alarma y le enviará un gmail al conductor de la infracción). La barrera también será configurada para 
  detectar si alguien la choca y para generar un delay antes de volver a bajar así el auto puede pasar 
  completamente. (si se comete una infracción, el sistema puede enviar un gmail al departamento policial 
  o directamente una multa municipal al infractor)

ARDUINO
	En arduino poseeremos distintas conecciones de un teclado matricial (donde se ingresa físicamente el dni 
  del conductor)l, protoboard (para conectar fácilmente todos los componentes), leds (para señalizar el 
  funcionamiento), resistencias para que no se queme nada, un sistema de barrera que la elevara o bajará 
  dependiendo los parámetros devueltos por el código, se usará un sistema con un motor para mobiliar la 
  barrera, un led para señalar si se abre o no (verde o rojo), y una alarma (que se activa cuando el conductor 
  no está inscrito al sistema o si se comete una infracción), también abra un botón para levantar manualmente 
  la barrera en caso de una emergencia.






