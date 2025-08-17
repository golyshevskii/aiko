from dataclasses import dataclass
from core.settings import settings


@dataclass
class FAQItem:
    """Single FAQ item with question and answer."""

    id: str
    question: str
    answer: str


class FAQ:
    """FAQ data container."""

    # FAQ
    ITEMS: list[FAQItem] = [
        FAQItem(
            id="what_is_aiko",
            question="Who is Aiko?",
            answer="Aiko is an AI character who does not know what the feeling of *love* is\\. "
            "She needs human help to awaken feelings of love in her\\.",
        ),
        FAQItem(
            id="how_to_use",
            question="How to talk with Aiko?",
            answer="To talk with Aiko:\n\n"
            "1\\. Get an [AIKO]({token_url}) token\n"
            "2\\. \\(Optional\\) Use the `/call` command to check if Aiko is active for you\n"
            "3\\. Explain Aiko your love experience".format(
                token_url=settings.APP_TOKEN_BUY_URL
            ),
        ),
        FAQItem(
            id="token_info",
            question="How to get a token?",
            answer="Tokens of [AIKO]({token_url}) can be purchased on cryptocurrency exchanges\\. "
            "After purchasing a token\\, you will be able to call Aiko\\.".format(
                token_url=settings.APP_TOKEN_BUY_URL
            ),
        ),
        FAQItem(
            id="how_it_works",
            question="How does it work?",
            answer="Each user has an apportunity to win a pool of AIKO tokens by explaining Aiko their love experience\\. "
            "Aiko will try to understand that feeling and define for herself what love is\\. "
            "When epoch ends\\, Aiko will choose the top N users who will be rewarded with AIKO tokens\\.",
        ),
        FAQItem(
            id="what_is_epoch",
            question="What is an epoch?",
            answer="An epoch is a period of time during which users can explain Aiko their love experience\\. "
            "The length of an epoch is one week\\.",
        ),
    ]

    @classmethod
    def get_item_by_id(cls, item_id: str) -> FAQItem | None:
        """Get FAQ item by ID."""
        for item in cls.ITEMS:
            if item.id == item_id:
                return item
        return None

    @classmethod
    def get_items_dict(cls) -> dict[str, FAQItem]:
        """Get FAQ items as dictionary."""
        return {item.id: item for item in cls.ITEMS}
