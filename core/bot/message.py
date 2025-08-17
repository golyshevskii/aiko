class Messages:
    """Container for all messages used in the bot."""

    # BOT
    START = "Hi `{username}`\\!\nUnlock _Aiko_ with an [AIKO]({token_url}) token 💫"
    CALL = "❣️ Aiko is fully attentive\\.\\.\\."
    CALL_INACTIVE = "Oops\\! To call Aiko you'll need an [AIKO]({token_url}) token 💫"

    # FAQ
    FAQ_TITLE = "💡 *FAQ*. Select the question ↓"
    FAQ_BACK_BUTTON = "← Back to questions"

    # SYSTEM
    ERROR = "An system error occurred while processing your request\\. Please try again later\\.\\.\\."

    # AIKO
    AIKO_ERROR = "I got a little tangled in my thoughts\\.\\.\\.\nCould you please call me again in a few minutes\\?"


msg = Messages()
