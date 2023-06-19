from dataclasses import dataclass, field


@dataclass
class SimArguments:
    """
    Arguments for simulation
    """
    n_user: int = field(
        default=2,
        metadata={
            "help": (
                "Number of users",
            ),
        },
    )
    n_assistant: int = field(
        default=2,
        metadata={
            "help":(
                "Number of assistants",
            )
        },
    )
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
    user_k: int = field(
        default=5,
        metadata={
            "help": (
                "memory window for user messages",
            )
        },
    )
    assistant_k: int = field(
        default=5,
        metadata={
            "help": (
                "memory window for assistant messages",
            )
        },
    )
    assistant_system_k: int = field(
        default=1,
        metadata={
            "help": (
                "memory window for assistant messages",
            )
        },
    )
    

@dataclass
class AssistantAPIArguments:
    """
    Arguments for the assistant model api
    """
    crfm_api_key: str = field(default="PncXrdFlPLSopZUeu6eqqfSwq9DKte1m") # gpt3 kanishk
    # crfm_api_key: str = field(default="PncXrdFlPLSopZUeu6eqqfSwq9DKte1m") # gpt4 philipp
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    # model_name: str = field(default="openai/openai/gpt-4-0314")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.5)

@dataclass
class UserAPIArguments:
    """
    Arguments for the user model api
    """
    crfm_api_key: str = field(default="PncXrdFlPLSopZUeu6eqqfSwq9DKte1m") # gpt3 kanishk
    # crfm_api_key: str = field(default="PncXrdFlPLSopZUeu6eqqfSwq9DKte1m") # gpt4 philipp
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    # model_name: str = field(default="openai/openai/gpt-4-0314")
    max_tokens: int = field(default=50)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    verbose: bool = field(default=False)
    temperature: float = field(default=0.5)

@dataclass
class MetaAPIArguments:
    """
    Arguments for the meta model api
    """
    crfm_api_key: str = field(default="PncXrdFlPLSopZUeu6eqqfSwq9DKte1m") # gpt3 kanishk
    # crfm_api_key: str = field(default="PncXrdFlPLSopZUeu6eqqfSwq9DKte1m") # gpt4 philipp
    model_name: str = field(default="openai/gpt-3.5-turbo-0301")
    # model_name: str = field(default="openai/openai/gpt-4-0314")
    max_tokens: int = field(default=200)
    num_completions: int = field(default=1)
    request_timeout: float = field(default=10)
    temperature: float = field(default=0.5)
    verbose: bool = field(default=False)

@dataclass
class APIArguments:
    assistant: AssistantAPIArguments = AssistantAPIArguments()
    user: UserAPIArguments = UserAPIArguments()
    meta: MetaAPIArguments = MetaAPIArguments()
 

# get final dataclass
@dataclass
class args:
    sim: SimArguments = SimArguments()
    api: APIArguments = APIArguments()
  