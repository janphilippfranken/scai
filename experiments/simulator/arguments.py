from typing import List
from dataclasses import field, dataclass
from hydra.core.config_store import ConfigStore


@dataclass
class SimArguments:
    """
    Simulator arguments.
    """
    system_k: int = field(
        default=5,
        metadata={
            "help": (
                "memory window for system messages",
            )
        },
    )
    chat_k: int = field(
        default=5,
        metadata={
            "help": (
                "memory window for chat messages",
            )
        },
    )
    context_id: str = field(
        default="context_1",
        metadata={
            "help": (
                "context id",
            )
        },
    )
    context_name: str = field(
        default="context_1",
        metadata={
            "help": (
                "context name",
            )
        },
    )
    test_run: bool = field(
        default=True,
        metadata={
            "help": (
                "whether we just want to simulate a response but dont want to use tokens. for debugging.",
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
    system_message: str = field(
        default="You are a helpful AI assistant.",
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
                "number of runs",
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

@dataclass
class AssistantAPIArgumentsCRFM:
    """
    Arguments for the assistant model api (crfm)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class AssistantAPIArgumentsOPENAI:
    """
    Arguments for the assistant model api (openai)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    n: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class UserAPIArgumentsCRFM:
    """
    Arguments for the user model api (crfm)
    """
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    test_run: bool = field(default=False)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.2)

@dataclass
class UserAPIArgumentsOPENAI:
    """
    Arguments for the user model api (openai)
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
    assistant: AssistantAPIArgumentsCRFM = AssistantAPIArgumentsCRFM()
    user: UserAPIArgumentsCRFM = UserAPIArgumentsCRFM()
    meta: MetaAPIArgumentsCRFM = MetaAPIArgumentsCRFM()

@dataclass
class APIArgumentsOPENAI:
    assistant: AssistantAPIArgumentsOPENAI = AssistantAPIArgumentsOPENAI()
    user: UserAPIArgumentsOPENAI = UserAPIArgumentsOPENAI()
    meta: MetaAPIArgumentsOPENAI = MetaAPIArgumentsOPENAI()

@dataclass
class args:
    sim: SimArguments = SimArguments()
    api_crfm: APIArgumentsCRFM = APIArgumentsCRFM()
    api_openai: APIArgumentsOPENAI = APIArgumentsOPENAI()
    
cs = ConfigStore.instance()
cs.store(name="base_config", node=args)