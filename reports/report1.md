# Informe sobre el proyecto de asistente para agentes de soporte al cliente

Este es un asistente simple que hace una llamada a un modelo de OpenAI con una consulta que recibe un agente humano 
por parte de un cliente de un banco ejemplo, a traves de un chat de whatsapp.

La funcion del asistente virtual es ayudar al agente a responder en tiempo y forma al cliente con la información 
oficial del banco. Para ello se proporciona una base ejemplo de conocimientos con detalle de productos y servicios 
ofrecidos por el banco.

El asistente no esta pensado como un agente conversacional, ya que el usuario no es el cliente directo sino un agente
humano que necesita una respuesta precisa y breve. Por ello es que en el system prompt se le dice que debe limitarse 
a dar una respuesta concreta segun lo que tiene en su base de conocimientos y no hacer re-preguntas.

Tambien se le dice en el system prompt que es un experto en operativa bancaria, de manera que pueda inferir
correctamente la tematica de la pregunta cuando esta no esta claramente definida por el usuario.

Este asistente seria parte de una UI que haría llamadas de API y luego le responderia al usuario. Por lo tanto se 
necesita una respuesta estructurada en JSON que pueda ser luego procesada. Esta estructura se la estamos pidiendo
tambien en el system prompt.

Finalmemte cabe aclarar, que en un entorno mas real y de producción, se usaría un RAG con acceso a una base de datos
de conocimietos real que tendria el banco.

## Resultados de las pruebas

Las pruebas fueron hechas con tecnicas de zero-shot y few-shot, esta última adjuntando un ejemplo de formato de la 
respuesta. No se incursionó en tecnicas de CoT ya que el objetivo del asistente no lo justifica. No se requiere seguir
pasos de razonamiento sino simplemente encontrar información en una base de conocimientos.

Los resultados fueron muy satisfactorios. Se experimentó con preguntas concretas y fáciles de encontrar en la base
(comision de cuenta corriente), preguntas offtopic (remedio para dolor de cabeza), preguntas genéricas (info productos
de inversion), y preguntas de temas bancarios pero de productos que el banco no ofrece (money market). Estas preguntas
estan hardcoded en el codigo y pueden seleccionarse indicando el numero de la pregunta en el prompt que hace el script.

Se apreció la diferencia de usar un modelo u otro. Con el modelo mas simple GPT-4o, la pregunta generica sobre
productos de inversion fue respondida con un "no tenemos productos de inversion", ya que no figura en la base de
conocimientos explicitamente con ese nombre. Pero al usar el modelo mas avanzado GPT-5-mini, respondio ofreciendo
los productos de plazo fijo y caja de ahorro, ya que son productos que pagan interes y pueden considerarse de
inversión.

No se experimentó con distintas temperaturas, se usó siempre el valor 0.0002 para que sea bien determinístico.

En cuanto al uso de tokens, el hecho de que la base de conocimientos se anexa al system prompt hace que sea
bastante voluminoso los input tokens. Y seria mucho mayor con una base real. Pero en un entorno de producción se
usaria RAG y el prompt seria mucho mas reducido.

Todas las pruebas quedan registradas en el archivo de salida el cual incluye no solo las métricas completas sino
tambien la consulta y la respuesta, de manera que se pueda hacer un buen tracking del asistente. Los archivos están
versionados con un timestamp.


