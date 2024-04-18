import requests
from chat.schemas import InputSchema
from chat.utils import get_logger
import json

logger = get_logger(__name__)

OLLAMA_ENDPOINT = 'http://localhost:11434/api/generate'


def run(job: InputSchema, cfg: dict = None, **kwargs):
    logger.info(f"Running job {job.model} {job.prompt}")
    logger.info(f"cfg: {cfg}")


    data = {
        'model': job.model,
        'prompt': job.prompt,
        'stream': False
    }

    response = requests.post(
        OLLAMA_ENDPOINT,
        json=data
    )

    response.raise_for_status()
    response_json = response.json()

    logger.info(f'RESPONSE JSON: {response_json}')


    return response_json['response']

if __name__ == "__main__":
    job = InputSchema(
        model='mistral',
        prompt='tell me a joke',
    )
    response = run(job)

    print('ttttttt', response)

