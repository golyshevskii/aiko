from dataclasses import dataclass
from core.settings import settings

PLACEHOLDERS = dict(
    token_url=settings.APP_TOKEN_BUY_URL,
    winners_count=settings.APP_EPOCH_WINNERS_COUNT,
    epoch_length_days=settings.APP_EPOCH_LENGTH_DAYS,
    support_email=settings.APP_SUPPORT_EMAIL,
)


@dataclass
class FAQItem:
    """Single FAQ item with question and answer."""

    id: str
    question: str
    answer: str


class FAQ:
    """FAQ data container."""

    ITEMS: list[FAQItem] = [
        FAQItem(
            id="who_is_aiko",
            question="Who is Aiko?",
            answer=(
                "Aiko is an AI character who does not yet understand what *love* is\\. "
                "She needs human help to awaken feelings of love in her through stories and reflections\\."
            ),
        ),
        FAQItem(
            id="what_is_epoch",
            question="What is an epoch?",
            answer=(
                "An epoch is a time window for users to explain Aiko their love experience\\. "
                "Each epoch lasts {epoch_length_days} days\\. At the end\\, the top {winners_count} participants win the prize pool of AIKO tokens\\."
            ).format(**PLACEHOLDERS),
        ),
        FAQItem(
            id="epoch_reset",
            question="Why does Aiko reset each epoch?",
            answer=(
                "At the start of every new epoch Aiko resets her understanding of love\\, "
                "so everyone begins on equal footing\\. "
                "However\\, the evaluation rubric becomes a bit stricter each epoch\\, "
                "making it progressively harder to convince Aiko\\."
            ),
        ),
        FAQItem(
            id="how_to_start",
            question="How do I start?",
            answer=(
                "1\\. Get an [AIKO]({token_url}) token\\.\n"
                "2\\. Check if Aiko is active by the `/call` command\\.\n"
                "3\\. Share a concrete experience or perspective about love\\.\n"
            ).format(**PLACEHOLDERS),
        ),
        FAQItem(
            id="why_token",
            question="Why do I need the AIKO token?",
            answer=(
                "Holding at least one AIKO token unlocks chat access for the epoch and funds the prize pool and development\\. "
                "It also aligns incentives: the better the community stories, the stronger the ecosystem\\."
            ),
        ),
        FAQItem(
            id="how_to_get_token",
            question="How do I get the token?",
            answer=(
                "Purchase [AIKO]({token_url}) via the link or supported exchanges/wallets\\. "
                "After the purchase, you will be able to chat with Aiko\\."
            ).format(**PLACEHOLDERS),
        ),
        FAQItem(
            id="multiple_submissions",
            question="Can I submit multiple times in an epoch?",
            answer=(
                "Yes\\, but quality beats quantity\\. "
                "Spam and low\\-effort messages are down\\-ranked and may be moderated\\."
            ),
        ),
        FAQItem(
            id="language",
            question="Which languages are supported?",
            answer=("You may write in any language you want\\."),
        ),
        FAQItem(
            id="scoring",
            question="How are winners selected?",
            answer=(
                "Submissions are scored 0\\–100 by an evaluation rubric focused on clarity\\, specificity\\, coherence\\, "
                "emotional self\\-reflection\\. The top {winners_count} by final score win for the epoch\\."
            ).format(**PLACEHOLDERS),
        ),
        FAQItem(
            id="payouts",
            question="How are prizes paid?",
            answer=(
                "Winners receive AIKO tokens from the epoch prize pool to their connected wallet within 24 hours after epoch end\\."
            ),
        ),
        FAQItem(
            id="refunds",
            question="Can I get a refund?",
            answer=(
                "Donations and token purchases are final\\. We cannot reverse on\\-chain transactions\\."
            ),
        ),
        FAQItem(
            id="account_wallet",
            question="Can I change my wallet?",
            answer=(
                "Yes\\. You can relink a new wallet before the epoch ends\\. "
                "Rewards are sent to the wallet linked at the time of payout\\."
            ),
        ),
        FAQItem(
            id="results",
            question="Where can I see results?",
            answer=("Epoch leaderboards and winners are published on the Aiko chat\\."),
        ),
        FAQItem(
            id="support",
            question="How can I contact support?",
            answer="Email `{support_email}`\\.".format(**PLACEHOLDERS),
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
