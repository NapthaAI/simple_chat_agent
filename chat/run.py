#!/usr/bin/env python

from chat.schemas import InputSchema
from chat.utils import get_logger
import json
from litellm import completion
import yaml

logger = get_logger(__name__)

def run(inputs: InputSchema, worker_nodes = None, orchestrator_node = None, flow_run = None, cfg: dict = None):
    logger.info(f"Running with inputs {inputs.prompt}")
    logger.info(f"cfg: {cfg}")

    prompt = inputs.prompt
    messages = [
        {"role": "system", "content": cfg["inputs"]["system_message"]},
        {"role": "user", "content": prompt},
    ]
    response = completion(
        model=cfg["models"]["ollama"]["model"],
        messages=messages,
        temperature=cfg["models"]["ollama"]["temperature"],
        max_tokens=cfg["models"]["ollama"]["max_tokens"],
        api_base=cfg["models"]["ollama"]["api_base"],
    )

    response = response.choices[0].message["content"]
    logger.info(f"Response: {response}")

    return response

if __name__ == "__main__":

    cfg_path = f"chat/component.yaml"
    with open(cfg_path, "r") as file:
        cfg = yaml.load(file, Loader=yaml.FullLoader)

    inputs = InputSchema(
        prompt='tell me a joke',
    )
    response = run(inputs, cfg)


