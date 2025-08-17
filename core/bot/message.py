class Messages:
    """Container for all messages used in the bot."""

    # BOT
    START = "Hi `{username}`\\!\n\nYou can't reach Aiko yet\\.\\.\\.\nUnlock her with an [AIKO]({token_url}) token 💫"
    CALL = "✨ Aiko is listening\\.\\.\\."
    CALL_INACTIVE = "Oops\\! To call Aiko you'll need an [AIKO]({token_url}) token 💫"

    # SYSTEM
    ERROR = "An system error occurred while processing your request\\.\nPlease try again later\\.\\.\\."

    # AIKO
    AIKO_ERROR = "I got a little tangled in my thoughts\\.\\.\\.\nCould you please call me again in a few minutes\\?"


msg = Messages()
