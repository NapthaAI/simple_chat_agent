#!/usr/bin/env python
import logging
from dotenv import load_dotenv
import json
from naptha_sdk.schemas import AgentDeployment, AgentRunInput
from naptha_sdk.inference import InferenceClient
import os
from simple_chat_agent.schemas import InputSchema, SystemPromptSchema

load_dotenv()

logger = logging.getLogger(__name__)

class SimpleChatAgent:

    def __init__(self, deployment: AgentDeployment):
        self.deployment = deployment
        if deployment.config.persona_module and deployment.config.system_prompt["persona"]:
            self.system_prompt = SystemPromptSchema(role=deployment.config.system_prompt["role"], persona=deployment.config.system_prompt["persona"])
        else:
            self.system_prompt = SystemPromptSchema(role=deployment.config.system_prompt["role"])
        self.node = InferenceClient(self.deployment.node)

    async def chat(self, inputs: InputSchema):
        if isinstance(inputs.tool_input_data, list):
            messages = [msg for msg in inputs.tool_input_data if msg["role"] != "system"]
        elif isinstance(inputs.tool_input_data, str):
            messages = [{"role": "user", "content": inputs.tool_input_data}]
        messages.insert(0, {"role": "system", "content": json.dumps(self.deployment.config.system_prompt)})

        response = await self.node.run_inference({"model": self.deployment.config.llm_config.model,
                                                    "messages": messages,
                                                    "temperature": self.deployment.config.llm_config.temperature,
                                                    "max_tokens": self.deployment.config.llm_config.max_tokens})

        if isinstance(response, dict):
            response = response['choices'][0]['message']['content']
        else:
            response = response.choices[0].message.content
        logger.info(f"Response: {response}")

        messages.append({"role": "assistant", "content": response})

        messages = [msg for msg in messages if msg["role"] != "system"]

        return messages

async def run(module_run: AgentRunInput, *args, **kwargs):
    logger.info(f"Running with inputs {module_run.inputs.tool_input_data}")

    simple_chat_agent = SimpleChatAgent(module_run.deployment)

    method = getattr(simple_chat_agent, module_run.inputs.tool_name, None)

    return await method(module_run.inputs)


if __name__ == "__main__":
    import asyncio
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment

    naptha = Naptha()

    deployment = asyncio.run(setup_module_deployment("agent", "simple_chat_agent/configs/deployment.json", node_url = os.getenv("NODE_URL"), load_persona_data=True))

    input_params = InputSchema(
        tool_name="chat",
        tool_input_data=[{"role": "user", "content": "tell me a joke"}],
    )

    module_run = AgentRunInput(
        inputs=input_params,
        deployment=deployment,
        consumer_id=naptha.user.id,
    )

    response = asyncio.run(run(module_run))

    print("RESPONSE", response)