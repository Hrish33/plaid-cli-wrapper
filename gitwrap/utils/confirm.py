import random

# Legendary Pokemon used as confirmation words for destructive commands.
# A random one is chosen each time so the prompt can't be muscle-memoried.
POKEMON = [
    # gen 1
    "articuno", "zapdos", "moltres", "mewtwo", "mew",
    # gen 2
    "lugia", "hooh", "raikou", "entei", "suicune", "celebi",
    # gen 3
    "kyogre", "groudon", "rayquaza", "latios", "latias",
    "regice", "regirock", "registeel", "jirachi", "deoxys",
]


def request_confirmation(action: str, prompt_fn=input):
    """Prompt the user to type a random legendary Pokemon name to confirm a destructive action.

    Args:
        action: Short description of what is about to happen (shown in the prompt).
        prompt_fn: Injectable input function — override in tests to avoid blocking on stdin.

    Returns:
        Tuple of (confirmed: bool, expected_word: str, typed_word: str).
    """
    word = random.choice(POKEMON)
    typed = prompt_fn(f"{action} — type '{word.upper()}' to confirm: ").strip()
    confirmed = typed.upper() == word.upper()
    return confirmed, word, typed
