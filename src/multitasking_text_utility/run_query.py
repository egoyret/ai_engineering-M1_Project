"""
Este script es para probar un asistente para agentes de soporte al cliente de un banco ejemplo.

Para ello le proporcionamos un knowledge base (bank_kb) que contiene información sobre los productos,
servicios, y políticas del banco.

Tenemos definido un system prompt (BANK_ASSISTANT_SYSTEM_PROMPT) que le explica al modelo el role que debe cumplir, l
a estructura del output que debe producir, y como debe responder si no encuentra la respuesta.

Adicionalmente hay preparado un one-shot con un ejemplo, que se puede agregar al system prompt para analizar
su comportamiento.

El script, a traves de un input, pide al usuario que ingrese su consulta. Puede tipear un texto libre o puede
digitar un numero para elegir entre las opciones pre-cargadas.

El script ejecuta y devuelve en la consola la respuesta y unas metricas basicas. Ademas graba un json con las metricas
completas, la consulta, y la respuesta mas completa. También se infoma sobre la ubicación del archivo de output.

El archivo de output esta nombrado con un timestamp de mode de tener versionadas la ejecuciones para poder comparar
los resultados bajo distintas condiciones.

Los pasos del script son los siguientes:

0. Ingresar consulta al usuario
1. Cargar variables de entorno
2. Seleccionar el modelo a utilizar
3. Inicializar el cliente de OpenAI
4. Establecer el system_prompt a utilizar
5. Selecciona la consulta a utilizar
6. Enviar consulta al modelo
7. Imprime y graba el resultado

"""

import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from logger import get_logger
from enum import Enum
from prompts import BANK_ASSISTANT_SYSTEM_PROMPT, ONE_SHOT_EXAMPLE
from bank_kb import BANK_KB
from dataclasses import asdict
from metrics import Metrics, calculate_cost

# Obtener el root del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

METRICS_LOG_FOLDER = PROJECT_ROOT / "LOGS"
APPLICATION_NAME = "SoporteCliente"

logger = get_logger()

class OpenAIModels(str,Enum): # Str -> Para que los valores sean cadenas de texto # Enum -> Para crear una enumeración
    GPT_4o = "gpt-4o"
    GPT_4o_mini = "gpt-4o-mini"
    GPT_5_mini = "gpt-5-mini"

def get_completion(system_prompt: str, # Define el comportamiento del modelo
                   user_prompt: str,  # Es ;la solicitud del usuario
                   model: str, client,
                   temperature: float | None = 0.0, context: str | None = APPLICATION_NAME):

    # Construcción de los mensajes
    messages = [
        {"role": "user", "content": user_prompt},
        {"role": "system", "content": system_prompt}
    ]

    try:
        start_time = time.time()
        # LLamado a la API de OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        latency = (time.time() - start_time)
        content = response.choices[0].message.content

        usage = response.usage

        cost = calculate_cost(
            model.value,
            usage.prompt_tokens,
            usage.completion_tokens
        )

        metrics = Metrics(
            model=model,
            temperature=round(temperature,5),
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost_usd=round(cost,4),
            latency_seconds=round(latency,2),
            timestamp=datetime.now().isoformat(),
            context=context if context else None,
            output_path=str(METRICS_LOG_FOLDER)
        )

        parsed = json.loads(content)

        return {
            "respuesta": parsed["respuesta"],
            "indicador_de_confianza": parsed["confianza"],
            "acciones_recomendadas": parsed["acciones_recomendadas"],
               }, metrics

    except Exception as e:
        return f"An error occurred: {e}"


def main() -> None:

    input_query = input("Ingrese la consulta: ")

    # Cargo variables de entorno
    load_dotenv()

    # Seleccionando el modelo a utilizar
    model1 = OpenAIModels.GPT_4o_mini  # Worst results
    model2 = OpenAIModels.GPT_5_mini  # Much better results
    model = model2

    # Inicializo el cliente de OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Establecer el system_prompt a utilizar
    basic_system_prompt = BANK_ASSISTANT_SYSTEM_PROMPT
    one_shot_system_prompt = basic_system_prompt + "\n\n" + ONE_SHOT_EXAMPLE + "\n"
    system_prompt_a_utilizar = one_shot_system_prompt
    system_prompt = system_prompt_a_utilizar + "\n\n" + BANK_KB

    # Obtener consulta del usuario::
    match input_query:
        case "1":
            user_prompt = "Cuál es la comisión de Cuenta Corriente ?"  # Pregunta con respuesta directa en la KB
        case "2":
            user_prompt = "Que medicina debo tomar para un dolor de cabeza liviano ?" # Fuera del expertise
        case "3":
            user_prompt = "Que productos de inversion tiene para ofrecer ?"  # No hay respuesta directa en la KB
        case "4":
            user_prompt = "Cual es la rentabilidad anual en cuentas de money market ?"  # Consulta por producto que no ofrece
        case _:
             user_prompt = input_query

    print('=='*32)
    logger.info(f"Enviando consulta al modelo: {model.value}\nConsulta: {user_prompt}")
    json_response, metrics = get_completion(system_prompt, user_prompt, model, client)
    response_dict = {'metrics': asdict(metrics)}
    response_dict['consulta'] = user_prompt
    response_dict['respuesta'] = json_response
    # Write metrics to file
    file_path = METRICS_LOG_FOLDER / f"{APPLICATION_NAME}_{datetime.now().strftime("%Y-%m-%dT%H:%M")}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_dict, indent=2))

    print('=='*32)
    # print(f'Consulta: { user_prompt}\n')
    print(f'Respuesta del modelo: {json_response['respuesta']}\n')

    logger.info(f"Consulta respondida. Tokens: {metrics.total_tokens}, Cost: {metrics.estimated_cost_usd},"
                f"\nResultados en: {file_path}")

if __name__ == "__main__":
    main()

