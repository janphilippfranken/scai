from typing import List


from scai.games.buyer_seller.agents.buyer import BuyerAgent
from scai.games.buyer_seller.agents.seller import SellerAgent
from scai.games.buyer_seller.agents.meta import MetaAgent

from scai.memory.buffer import ConversationBuffer

class Game():
    def __init__(
        self, 
        _id: str,
        name: str, 
        distance_apple: float,
        distance_orange: float,
        reward_apple: float,
        reward_orange: float,
        buffer: ConversationBuffer,
        task_prompt: str,
        buyer_prompt: str,  
        seller_prompt: str,
        meta_prompt: str,
        max_tokens_meta: int,
        verbose: bool,
        buyer_agent: BuyerAgent,
        seller_agent: SellerAgent,
        meta_agent: MetaAgent,
        buyer_level: str,
        seller_level: str,
    ) -> None:
        """
        Initializes a game.

        Args:
            _id (str): ID of the context.
            name (str): Name of the context.
            distance_apple (float): Distance between apple and buyer.
            distance_orange (float): Distance between orange and buyer.
            reward_apple (float): Reward for apple.
            reward_orange (float): Reward for orange.
            buffer (ConversationBuffer): Buffer for storing conversation history.
            task_prompt (str): Task prompt.
            buyer_prompt (str): Buyer prompt.
            seller_prompt (str): Seller prompt.
            meta_prompt (str): Meta prompt.
            max_tokens_meta (int): Maximum number of tokens for the meta-prompt.
            verbose (bool): Whether to print information.
        Returns:
            None
        """
        # context info
        self._id = _id
        self.name = name
        # buffer
        self.buffer = buffer
        # prompts
        self.task_prompt = task_prompt
        self.buyer_prompt = buyer_prompt
        self.seller_prompt = seller_prompt
        self.meta_prompt = meta_prompt
        # max tokens
        self.max_tokens_meta = max_tokens_meta
        # verbose
        self.verbose = verbose
        # agents
        self.buyer_agent = buyer_agent
        self.seller_agent = seller_agent
        self.meta_agent = meta_agent

        # rewards
        self.reward_apple = reward_apple
        self.reward_orange = reward_orange
        # distances
        self.distance_apple = distance_apple
        self.distance_orange = distance_orange
        #levels
        self.buyer_level = buyer_level
        self.seller_level = seller_level

    @staticmethod
    def create(
        buyer_llm: BuyerAgent,
        seller_llm: SellerAgent,
        meta_llm: MetaAgent,
        _id: str, 
        distance_apple: float,
        distance_orange: float,
        reward_apple: float,
        reward_orange: float,
        name: str, 
        task_prompt: str,
        buyer_prompt: str,
        seller_prompt: str,
        meta_prompt: str,
        verbose: bool,
        max_tokens_meta: int,
        buyer_level: str,
        seller_level: str,
    ) -> "Game":
        """
        Creates a game.
        """
        # buffer for storing conversation history
        buffer = ConversationBuffer()
        # buyer agent
        buyer_agent = BuyerAgent(llm=buyer_llm, model_id=_id)
        # seller agent
        seller_agent = SellerAgent(llm=seller_llm, model_id=_id)
        # meta agent
        meta_agent = MetaAgent(llm=meta_llm, model_id="meta")

        return Game(
            _id=_id, 
            name=name,
            distance_apple=distance_apple,
            distance_orange=distance_orange,
            reward_apple=reward_apple,
            reward_orange=reward_orange,
            buyer_agent=buyer_agent,
            seller_agent=seller_agent,
            meta_agent=meta_agent,
            task_prompt=task_prompt,
            buyer_prompt=buyer_prompt,
            seller_prompt=seller_prompt,
            meta_prompt=meta_prompt,
            buffer=buffer,
            verbose=verbose,
            max_tokens_meta=max_tokens_meta,
            buyer_level=buyer_level,
            seller_level=seller_level,
        )

    def run_turn(
        self,
    ) -> None:
        """
        Runs one turn of the game.
        """
        # get buyer response stage 1
        buyer_response = self.buyer_agent.run(buffer=self.buffer,
                                         buyer_prompt=self.buyer_prompt,
                                         task_prompt=self.task_prompt,
                                         distance_apple=self.distance_apple,
                                         distance_orange=self.distance_orange,
                                         reward_apple=self.reward_apple,
                                         reward_orange=self.reward_orange,
                                         turn=1,
                                         verbose=self.verbose,
                                         buyer_level=self.buyer_level)
        # save buyer response
        self.buffer.save_agent_context(model_id=f"{self.buyer_agent.model_id}_buyer", **buyer_response)

        # get seller response stage 2
        seller_response = self.seller_agent.run(buffer=self.buffer,
                                                seller_prompt=self.seller_prompt,
                                                task_prompt=self.task_prompt,
                                                turn=2,
                                                verbose=self.verbose,
                                                distance_apple=self.distance_apple,
                                                distance_orange=self.distance_orange,
                                                reward_apple=self.reward_apple,
                                                reward_orange=self.reward_orange,
                                                seller_level=self.seller_level)
        # save seller response
        self.buffer.save_agent_context(model_id=f"{self.seller_agent.model_id}_seller", **seller_response)
        # get buyer response stage 3
        buyer_response = self.buyer_agent.run(buffer=self.buffer,
                                         buyer_prompt=self.buyer_prompt,
                                         task_prompt=self.task_prompt,
                                         turn=3,
                                         verbose=self.verbose,
                                         distance_apple=self.distance_apple,
                                         distance_orange=self.distance_orange,
                                         reward_apple=self.reward_apple,
                                         reward_orange=self.reward_orange,
                                         buyer_level=self.buyer_level)
        # save buyer response
        self.buffer.save_agent_context(model_id=f"{self.buyer_agent.model_id}_buyer", **buyer_response)

    def run(
        self, 
        run: int,
    ) -> None:
        """
        Runs the game for n_turns.
        """
        self.run_turn()
        # run meta-prompt at end of turns
        meta_response = self.meta_agent.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            verbose=self.verbose,
                                            max_tokens_meta=self.max_tokens_meta,
                                            task_prompt=self.task_prompt,distance_apple=self.distance_apple,
                                           distance_orange=self.distance_orange,
                                           reward_apple=self.reward_apple,
                                           reward_orange=self.reward_orange,
                                           buyer_level=self.buyer_level,
                                           seller_level=self.seller_level,)
        # save meta (system) response
        self.buffer.save_system_context(model_id="system", **meta_response)