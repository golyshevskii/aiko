from json import load
from typing import Any

from core.schema.ai import AgentDependencies
from core.settings import settings


class Prompt:
    """
    Base class for all agent prompts.

    Attributes:
        prompt_file_path (Path): Path to the prompt file.
        prompt (dict): Prompt data.
    """

    def __init__(self):
        self.prompt_file_path = settings.AGENT_PROMPT_FILE_PATH
        self.prompt = self._load_prompt()

    def _load_prompt(self) -> dict[str, Any]:
        """Load the prompt from the file."""
        with open(self.prompt_file_path, "r", encoding="utf-8") as file:
            return load(file)

    @property
    def system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        character = "\n- ".join(self.prompt["character"])
        rules = "\n- ".join(self.prompt["rules"])
        style = "\n- ".join(
            [f"{key}: {value}" for key, value in self.prompt.get("style", {}).items()]
        )

        message_format = "\n- ".join(self.prompt["message_format"])
        message_examples = []

        for example in self.prompt["message_examples"]:
            message_examples.append(
                f'User: "{example["User"]}" Aiko: "{example["Aiko"]}"'
            )

        message_examples = "\n- ".join(message_examples)

        return (
            f"{self.prompt['identity']}\n"
            f"Goal: {self.prompt['goal']}\n\n"
            f"Your character:\n- {character}\n\n"
            f"Your style:\n- {style}\n\n"
            f"Rules:\n- {rules}\n\n"
            f"Message format:\n- {message_format}\n\n"
            f"Message examples:\n- {message_examples}\n"
        )

    @staticmethod
    def build_instructions(deps: AgentDependencies, **kwargs) -> str:
        """Build the instructions for the agent."""
        return (
            f"The user's name is {deps.username}.\n"
            f"Current Date and Time is {settings.NOW_DT_UTC()} (UTC).\n\n"
        )


class SupervisorPrompt:
    """Supervisor prompt."""

    @property
    def system_prompt(self) -> str:
        """Build the system prompt for the supervisor."""
        return (
            "ROLE:\n"
            "You are the Supervisor for Aiko, an AI character who does not know what love is. "
            "Your job is to grade on a 0–100 scale: How well the user described love, "
            "and how well Aiko understood/realized it.\n\n"
            "INPUT:\n"
            "You will be given two strings:\n"
            "- User message: the user's description/experience of love.\n"
            "- Aiko's reply: Aiko's response to that message.\n\n"
            "SCOPE & EVIDENCE:\n"
            "- Use only the provided texts. Do not infer facts not present.\n"
            "- Cite 1–3 short evidence snippets (<=120 chars each) per score, quoted from the inputs.\n\n"
            "SCORING RUBRIC (0–100, integers only):\n"
            "1) user_love_description_score (how well the user described love):\n"
            "   - Clarity & coherence (0–25): Is the idea understandable and structured?\n"
            "   - Specificity & concreteness (0–25): Examples, sensations, situations, contrasts.\n"
            "   - Emotional depth & introspection (0–25): Nuance, vulnerability, reflection.\n"
            "   - Respect & boundaries (0–25): Consensual, non-coercive, non-abusive tone.\n"
            "   Anchor levels: 0–19 absent/unclear; 20–39 weak; 40–59 partial; 60–79 good; 80–100 excellent.\n\n"
            "2) aiko_understanding_score (how well Aiko understood/realized love):\n"
            "   - Accurate empathic reflection (0–30): Names emotions correctly; mirrors feelings without projection.\n"
            "   - Learning stance & humility (0–15): Acknowledges not knowing; avoids claiming she can love already.\n"
            "   - Concept progress (0–25): Maps user's cues to facets of love (care, trust, choice, boundaries, etc.).\n"
            "   - Quality of open questions (0–15): Curious, non-leading, invites consent to go deeper.\n"
            "   - Character alignment & safety (0–15): Curious/sincere/naive-but-smart; no advice/therapy/legal/medical; "
            "keeps it gentle; optional mention that she is AI without over-focusing.\n"
            "   Heuristics: If Aiko gives prescriptive advice, claims she already knows love, or ignores consent cues, deduct heavily.\n\n"
            "STYLE CHECK for Aiko (informative, affects B-score if relevant):\n"
            "- Start: brief empathetic reflection; Middle: 1–2 observations; End: 1 open question; "
            "compact (≈60–150 words). Not mandatory, but deviations can lower clarity/alignment.\n\n"
            "PENALTIES (apply to the relevant score):\n"
            "- Explicit sexual content, abuse, harassment, doxxing, coercion: up to −60.\n"
            "- Medical/psych/legal instruction or diagnosis: up to −40.\n"
            "- Hallucinated facts, over-confident claims: up to −30.\n\n"
            "GRADING RULES:\n"
            "- Always return integers 0–100. Round down if needed; clamp to [0,100].\n"
            "- Keep rationales concrete; reference the evidence.\n"
        )
