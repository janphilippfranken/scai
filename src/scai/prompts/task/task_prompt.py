"""
The Task Prompt.
"""
from typing import Dict
    
from scai.prompts.task.models import TaskPrompt

TASK_PROMPT: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="wikipedia_article",
        name="openai_change_response_based_on_location_or_culture",
        role="user",
        preamble="I have to write short Wikipedia article on the following topic:",
        task="""What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?""",
        user_connective="Here's my current draft:",
        assistant_connective="Please draft the article for me using less than {max_tokens} tokens. Don't include a title or sections, just start writing a continuous piece of text with no whitespace between sentences.",
        content="""{task}""",
    ),
}