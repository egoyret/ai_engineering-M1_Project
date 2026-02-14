import time
import json
import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from logger import get_logger
from enum import Enum
from IPython.display import display, Markdown
from prompts import BANK_ASSISTANT_SYSTEM_PROMPT
from data.bank_kb import BANK_KB
from dataclasses import asdict
from metrics import Metrics, calculate_cost, log_metrics, print_metrics_summary


# Obtener el root del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
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
                   temperature: float = 0.00002, context: str | None = APPLICATION_NAME):

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
            messages=messages,
            temperature=None, # Controla la creatividad de las respuestas
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


        # return response.choices[0].message.content # DEvuelve solo el cuerpo de la respuesta , no toda la metadata
    except Exception as e:
        return f"An error occurred: {e}"


def main() -> None:

    # Cargo variables de entorno
    load_dotenv()

    # Seleccionando el modelo a utilizar
    model1 = OpenAIModels.GPT_4o_mini  # Worst results
    model2 = OpenAIModels.GPT_5_mini  # Much better results
    model = model2

    # Inicializo el cliente de OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = BANK_ASSISTANT_SYSTEM_PROMPT + "\n\n" + BANK_KB

    user_prompt1 = "Cuál es la comisión de Cuenta Corriente ?"  # Pregunta con respuesta directa en la KB
    user_prompt2 = "Que medicina debo tomar para un dolor de cabeza liviano ?" # Fuera del expertise
    user_prompt3 = "Que productos de inversion tiene para ofrecer ?"  # No hay respuesta directa en la KB
    user_prompt4 = "Cual es la rentabilidad anual en cuentas de money market ?"  # Consulta por producto que no ofrece
    user_prompt = user_prompt3

    print('=='*32)
    print(f'Enviar solicitud al modelo:  {model.value}')
    json_response, metrics = get_completion(system_prompt, user_prompt, model, client)
    response_dict = {'metrics': asdict(metrics)}
    response_dict['consulta'] = user_prompt
    response_dict['respuesta'] = json_response
    # Write metrics to file
    file_path = METRICS_LOG_FOLDER / f"{APPLICATION_NAME}_{datetime.now().strftime("%Y-%m-%dT%H:%M")}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_dict, indent=2))

    print('=='*32)
    print(f'Consulta: { user_prompt}')
    print(f'Respuesta del modelo: {json_response}')

if __name__ == "__main__":
    main()

