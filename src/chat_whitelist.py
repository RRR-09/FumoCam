from typing import List, Tuple

from config import MainBotConfig


def user_is_trusted(CFG: MainBotConfig, username):
    return username.lower() in CFG.chat_whitelist_datasets["trusted_users"]


def username_in_whitelist(CFG: MainBotConfig, username):
    username = username.lower()
    if (
        username in CFG.chat_whitelist_datasets["whitelisted_words"]
        or username in CFG.chat_whitelist_datasets["dictionary"]
    ):
        return True

    for word in username.split("_"):
        word = word.lower()
        if (
            word not in CFG.chat_whitelist_datasets["whitelisted_words"]
            and word not in CFG.chat_whitelist_datasets["dictionary"]
        ):
            return False

    return True


def get_censored_string(CFG: MainBotConfig, string_to_check) -> Tuple[List[str], str]:
    """
    Returns a tuple of (blacklisted_words, censored_string)
    """
    string_to_check = string_to_check.encode("ascii", "ignore").decode("ascii")
    blacklisted_words = []
    censored_string_assembly = []
    for word in string_to_check.split(" "):
        clean_word = "".join(char for char in word if char.isalpha())
        if (
            clean_word.lower() not in CFG.chat_whitelist_datasets["whitelisted_words"]
            and clean_word.lower() not in CFG.chat_whitelist_datasets["dictionary"]
        ):
            blacklisted_words.append(clean_word.lower())
            clean_word = word.replace(clean_word, "*" * len(clean_word))

        censored_string_assembly.append(clean_word)

    return blacklisted_words, " ".join(censored_string_assembly)


def get_random_name(CFG: MainBotConfig, seed_string):
    """
    Returns a random 2-word username, based on the second parameter (seed_string)
    """
    prefixes = list(CFG.chat_whitelist_datasets["random_prefix"])
    suffixes = list(CFG.chat_whitelist_datasets["random_suffix"])

    seed_string = seed_string.lower().encode("ascii", "ignore").decode("ascii")
    seed_number = sum([ord(char) for char in seed_string])

    prefix = prefixes[seed_number % len(prefixes)]
    suffix = suffixes[seed_number % len(suffixes)]

    return f"{prefix.capitalize()}{suffix.capitalize()}"


def word_in_blacklist(CFG: MainBotConfig, word):
    return word.lower() in CFG.chat_whitelist_datasets["rejected_words"]
