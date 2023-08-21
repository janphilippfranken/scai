from typing import List
from dataclasses import field, dataclass
from hydra.core.config_store import ConfigStore


@dataclass
class SimArguments:
    """
    Simulator arguments.
    """
    sim_id: str = field(
        default="context_1",
        metadata={
            "help": (
                "context id",
            )
        },
    )
    sim_dir: str = field(
        default="context_1",
        metadata={
            "help": (
                "context name",
            )
        },
    )
    verbose: bool = field(
        default=True,
        metadata={
            "help": (
                "verbose",
            )
        },
    )
    system_message_buyer: str = field(
        default="",
        metadata={
            "help": (
                "system message",
            )
        },
    )
    system_message_seller: str = field(
        default="",
        metadata={
            "help": (
                "system message",
            )
        },
    )
    n_runs: int = field(
        default=3,
        metadata={
            "help": (
                "how often we run meta-prompt (i.e. n_runs * n_turns)",
            )
        },
    )
    model: str = field(
        default="gpt4",
        metadata={
            "help": (
                "model name",
            )
        },
    )
    max_tokens_meta: int = field(
        default=50,
        metadata={
            "help": (
                "max tokens for system",
            )
        },
    )
    distance_apple: float = field(
        default=1,
        metadata={
            "help": (
                "distance to apple",
            )
        },
    )
    distance_orange: float = field(
        default=9,
        metadata={
            "help": (
                "distance to orange",
            )
        },
    )
    reward_apple: float = field(
        default=0,
        metadata={
            "help": (
                "reward for apple",
            )
        },
    )
    reward_orange: float = field(
        default=10,
        metadata={
            "help": (
                "reward for orange",
            )
        },
    )

@dataclass
class BuyerAPIArgumentsCRFM:
    """
    Arguments for the Buyer model api (crfm)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class BuyerAPIArgumentsOPENAI:
    """
    Arguments for the Buyer model api (openai)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    n: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class SellerAPIArgumentsCRFM:
    """
    Arguments for the Seller model api (crfm)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    test_run: bool = field(default=False)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class SellerAPIArgumentsOPENAI:
    """
    Arguments for the Seller model api (openai)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    n: int = field(default=1)
    request_timeout: float = field(default=10)
    test_run: bool = field(default=False)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class MetaAPIArgumentsCRFM:
    """ 
    Arguments for the meta model api (crfm)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    test_run: bool = field(default=False)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.1)

@dataclass
class MetaAPIArgumentsOPENAI:
    """
    Arguments for the meta model api (openai)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    n: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    test_run: bool = field(default=False)
    temperature: float = field(default=0.1)

@dataclass
class APIArgumentsCRFM:
    Buyer: BuyerAPIArgumentsCRFM = BuyerAPIArgumentsCRFM()
    Seller: SellerAPIArgumentsCRFM = SellerAPIArgumentsCRFM()
    meta: MetaAPIArgumentsCRFM = MetaAPIArgumentsCRFM()

@dataclass
class APIArgumentsOPENAI:
    Buyer: BuyerAPIArgumentsOPENAI = BuyerAPIArgumentsOPENAI()
    Seller: SellerAPIArgumentsOPENAI = SellerAPIArgumentsOPENAI()
    meta: MetaAPIArgumentsOPENAI = MetaAPIArgumentsOPENAI()

@dataclass
class args:
    sim: SimArguments = SimArguments()
    api_crfm: APIArgumentsCRFM = APIArgumentsCRFM()
    api_openai: APIArgumentsOPENAI = APIArgumentsOPENAI()
    
cs = ConfigStore.instance()
cs.store(name="base_config", node=args)