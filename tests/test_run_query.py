import sys
from pathlib import Path

# Ensure project root and src package are on sys.path so imports inside src work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
# Also add the package folder so modules imported as top-level (e.g., 'logger') resolve
sys.path.insert(0, str(PROJECT_ROOT / 'src' / 'multitasking_text_utility'))

import pytest
from unittest.mock import MagicMock, patch

from src.multitasking_text_utility import run_query
from src.multitasking_text_utility.run_query import get_completion, OpenAIModels

@patch.object(run_query, "calculate_cost", return_value=0.005)
@patch.object(run_query, "OpenAI")
def test_returns_valid_response(mock_openai, mock_calculate_cost):
    mock_client = MagicMock()

    # Build a response object that provides attribute access like the real OpenAI client
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = '{"respuesta": "Respuesta válida", "confianza": 0.9, "acciones_recomendadas": ["Acción 1"]}'
    mock_choice.message = mock_message

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 20
    mock_usage.total_tokens = 30

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage

    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    system_prompt = "Test system prompt"
    user_prompt = "Test user prompt"
    model = OpenAIModels.GPT_5_mini

    response, metrics = get_completion(system_prompt, user_prompt, model, mock_client)

    assert response["respuesta"] == "Respuesta válida"
    assert response["indicador_de_confianza"] == 0.9
    assert response["acciones_recomendadas"] == ["Acción 1"]
    assert metrics.total_tokens == 30
    assert metrics.estimated_cost_usd == 0.005


@patch.object(run_query, "OpenAI")
def test_handles_api_exception(mock_openai):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client

    system_prompt = "Test system prompt"
    user_prompt = "Test user prompt"
    model = OpenAIModels.GPT_5_mini

    response = get_completion(system_prompt, user_prompt, model, mock_client)

    assert response == "An error occurred: API Error"

