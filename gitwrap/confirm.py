import random

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
    word = random.choice(POKEMON)
    typed = prompt_fn(f"{action} — type '{word.upper()}' to confirm: ").strip()
    confirmed = typed.upper() == word.upper()
    return confirmed, word, typed
