"""
Source: Off the Rails by Jan-Philipp Franken

example usage:
from chat_models.gpt4 import GPT4Agent
from chat_models.azure import AsyncAzureChatLLM

args.model.azure_api.api_key = os.getenv("OPENAI_API_KEY")

llm = AsyncAzureChatLLM(**args.model.azure_api)
model = GPT4Agent(llm=llm, **args.model.completion_config)
responses = model.batch_prompt(batch_messages=[messages])

"""

from typing import (
    Any,
    Dict,
    List, 
)

import asyncio


import logging 


logging.basicConfig(level=logging.INFO)


 # The cost per token for each model input.
MODEL_COST_PER_INPUT = {
    'gpt-4': 3e-05,
}
# The cost per token for each model output.
MODEL_COST_PER_OUTPUT = {
    'gpt-4': 6e-05,
}


class GPT4Agent():
    """
    gpt-4 LLM wrapper for async API calls.
    """
    def __init__(
        self, 
        llm: Any,
        **completion_config,
    ) -> None:
        self.llm = llm
        self.completion_config = completion_config
        self.all_responses = []
        self.total_inference_cost = 0

    def calc_cost(
        self, 
        response
    ) -> float:
        """
        Args:
        response (openai.ChatCompletion): The response from the API.

        Returns:
        float: The cost of the response.
        """
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (
            MODEL_COST_PER_INPUT['gpt-4'] * input_tokens
            + MODEL_COST_PER_OUTPUT['gpt-4'] * output_tokens
        )
        return cost
    
    async def get_response(
        self, 
        messages: List[Dict[str, str]],
    ) -> Any:
        """
        Get the response from the model.
        """
        return await self.llm(messages=messages, **self.completion_config)
    
    async def run(
        self, 
        messages: List,
    ) -> Dict[str, Any]:
        """Runs the model on a single list of messages."""
        print("awaiting response")
        response = await self.get_response(messages=messages)
        print("response received")
        
        cost = self.calc_cost(response=response)
        logging.info(f"Cost for running gpt4: {cost}")
       
        full_response = {
            'response': response,
            'response_str': [r.message.content for r in response.choices],
            'cost': cost
        }
        # Update total cost and store response
        self.total_inference_cost += cost
        self.all_responses.append(full_response)
    
        return full_response['response_str']
    
    async def batch_prompt_sync(
        self, 
        batch_messages: List[List],
    ) -> List[str]:
        """Handles async API calls for batch prompting.

        Args:
            messages (List[str]): A list of user messages

        Returns:
            A list of responses from the code model for each message
        """
        responses = [self.run(message) for message in batch_messages]
        return await asyncio.gather(*responses)

    def batch_prompt(
        self, 
        batch_messages: List[List],
    ) -> List[str]:
        """=
        Synchronous wrapper for batch_prompt.
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError(f"Loop is already running.")
        return loop.run_until_complete(self.batch_prompt_sync(batch_messages))