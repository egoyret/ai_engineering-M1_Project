# ai_engineering-M1_Project

## Asistente para agentes de soporte al cliente

El use case es el de un banco que tiene contratados agentes humanos de nivel muy junior para atender consultas de los clientes.

Para facilitar la tarea de los agentes junior y asegurarse de que den las respuestas correctas, y no tengan que perder tiempo accediendo manualmente a documentación del banco, se les da acceso a este asistente virtual.

Los agentes reciben las consultas a traves de un chat con el cliente e inmediatamente pasan la consulta al asistente virtual. El asistente accede a una base de conocimientos del banco y genera la respuesta la cual es analizada por el agente y luego pasada al cliente.

El asistente va a tener instrucciones precisas de que solo debe responder coninfomacion que esta en la base de conocimientos y que no debe hacer re-preguntas ya que no esta conversando con un cliente sino solo facilitandole informacion al agente sobre una pregunta concreta.

## Setup

```bash
1. Clonar el repo y pararse en el root del proyecto.
2. Instalar dependencias: uv sync
3. Generar archivo para variables de entorno: cp .env.example .env
```
Configura `.env`:

```bash
OPENAI_API_KEY=sk-...
```
## Ejecutar

```bash
Desde el root del proyecto:
python src/multitasking_text_utility/run_query.py

O también:
make run-project
```

## Input de la consulta
```bash
El script presenta el siguiente prompt:

Ingrese la consulta:

El usuario puede ingresar cualquier consulta o tipear uno de estos digitos para consultas de ejemplo:
1 "Cuál es la comisión de Cuenta Corriente ?"  # Pregunta con respuesta directa en la KB
2 "Que medicina debo tomar para un dolor de cabeza liviano ?" # Fuera del expertise
3 "Que productos de inversion tiene para ofrecer ?"  # No hay respuesta directa en la KB
4 "Cual es la rentabilidad anual en cuentas de money market ?"  # Consulta por producto que no ofrece
 
```
## Respuesta del asistente

El asistente responde con un print en la consola con la consulta, la respuesta, unas métricas básicas, y la ubicación de un archivo de output con un json con metricas y respuestas completas.

El nombre del archivo esta versionado con un timestamp a efectos de preservarlo y poder compararlos entre si.

## Tests
Para ejecutar los tests:
```bash
pytest

O también:
make test-se
```

## Estructura del proyecto:

```
ai_engineering/
├── logs/
│   ├── SoporteCliente_yyyy-mm-dd_hh-mm-ss.json  # Outputs del asistente
├── reports/
│   ├── report1.md                               # Informe final
├── src/
│   ├── run_query.py                             # Script principal ejecutable
│   ├── metrics.py                               # Dataclass de metrics
│   ├── prompts.py                               # System prompts
│   ├── bank_kb.py                               # base de conocimientos del banco
│   └── logger.py                                # Logs coloreados para debugging
└── tests/
    └── test_run_query.py                        # test unitario (con mocks)

```
