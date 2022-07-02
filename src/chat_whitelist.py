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


def get_censored_string(
    CFG: MainBotConfig, string_to_check, debug=False
) -> Tuple[List[str], str]:
    """
    Returns a tuple of (blacklisted_words, censored_string)
    """
    string_to_check = string_to_check.encode("ascii", "ignore").decode("ascii")
    blacklisted_words = []
    censored_string_assembly = []
    space_bypassed_string = ""

    def print_if_debug(print_str, is_debug):
        if is_debug:
            print(print_str)

    # punctuation = {"!", "?", ",", ".", ":", ";", "'", '"', "(", ")", "@", "#", "$", "%", "^", "&", "*",}
    for word in string_to_check.split(" "):
        word_is_spaced = False
        original_word = word
        clean_word = "".join(char for char in word if char.isalpha())

        # Handle people trying to space out non-whitelisted words
        if len(clean_word) == 1:
            print_if_debug(f"space_bypassed_string: {clean_word} ({word})", debug)
            space_bypassed_string += clean_word
            continue
        elif len(space_bypassed_string) > 0:
            space_bypassed_censored = space_bypassed_string
            print_if_debug(
                f"space_bypassed_censored assembly: {space_bypassed_string} ({word})",
                debug,
            )
            if (
                space_bypassed_string.strip() != ""
                and space_bypassed_string.lower()
                not in CFG.chat_whitelist_datasets["whitelisted_words"]
                and space_bypassed_string.lower()
                not in CFG.chat_whitelist_datasets["dictionary"]
            ):
                blacklisted_words.append(space_bypassed_string.lower())
                space_bypassed_censored = space_bypassed_string.replace(
                    space_bypassed_string, "*" * len(space_bypassed_string)
                )
            space_bypassed_censored = " ".join(space_bypassed_censored)
            censored_string_assembly.append(space_bypassed_censored)
            space_bypassed_string = ""  # Clear space bypass buffer

        if (
            clean_word.strip() != ""
            and clean_word.lower()
            not in CFG.chat_whitelist_datasets["whitelisted_words"]
            and clean_word.lower() not in CFG.chat_whitelist_datasets["dictionary"]
        ):

            suffix_removal_success = False
            if len(clean_word) >= 3:
                print_if_debug(f"cleanword_suffix_check: {clean_word} ({word})", debug)
                # Allow suffix-extended characters, like "testtttttttttttttttt" qualifying as "test"
                offset = 1
                index = len(clean_word) - offset
                while (index > 2) and clean_word[index] == clean_word[index - 1]:
                    word_attempt = clean_word[:offset].lower()
                    print(word_attempt)
                    if (
                        word_attempt in CFG.chat_whitelist_datasets["whitelisted_words"]
                        or word_attempt in CFG.chat_whitelist_datasets["dictionary"]
                    ):
                        clean_word = word
                        suffix_removal_success = True
                        break
                    offset += 1
                    index = len(clean_word) - offset

            if not suffix_removal_success or len(clean_word) < 3:
                print_if_debug(f"blacklist_action: {clean_word} ({word})", debug)
                blacklisted_words.append(clean_word.lower())
                previous_asterisks = original_word.count("*")
                clean_word = original_word.replace(clean_word, "*" * len(clean_word))
                if clean_word.count("*") < len(clean_word) - previous_asterisks:
                    # Theres some weird interjecting symbols and we should just censor the whole word
                    clean_word = len(original_word) * "*"
        elif word_is_spaced:
            # If we've checked the non-spaced word is fine,
            # retain the spacing
            clean_word = " ".join(clean_word)
            print_if_debug(f"word_is_spaced: {clean_word} ({word})", debug)
        else:
            # If we're not censoring, leave numbers in
            # clean_word = "".join(char for char in word if char.isalnum())
            print_if_debug(f"not_censoring: {clean_word} ({word})", debug)
            clean_word = word

        censored_string_assembly.append(clean_word)

    # Finish adding any single-char last-words
    if len(space_bypassed_string) > 0:

        clean_word = space_bypassed_string
        original_word = space_bypassed_string
        if (
            clean_word.strip() != ""
            and clean_word.lower()
            not in CFG.chat_whitelist_datasets["whitelisted_words"]
            and clean_word.lower() not in CFG.chat_whitelist_datasets["dictionary"]
        ):
            blacklisted_words.append(clean_word.lower())
            clean_word = original_word.replace(clean_word, "*" * len(clean_word))
        else:
            # retain the spacing
            clean_word = " ".join(clean_word)

        print_if_debug(f"single-char last-words: {clean_word} ({original_word})", debug)
        censored_string_assembly.append(clean_word)

    return blacklisted_words, " ".join(censored_string_assembly)


def get_random_name(CFG: MainBotConfig, seed_string):
    """
    Returns a random 2-word username, based on the second parameter (seed_string)
    """
    prefixes = sorted(list(CFG.chat_whitelist_datasets["random_prefixes"]))
    suffixes = sorted(list(CFG.chat_whitelist_datasets["random_suffixes"]))

    seed_string = seed_string.lower().encode("ascii", "ignore").decode("ascii")
    seed_number = sum([ord(char) for char in seed_string])

    prefix = prefixes[seed_number % len(prefixes)]
    suffix = suffixes[seed_number % len(suffixes)]

    return f"{prefix.capitalize()}{suffix.capitalize()}"


def word_in_blacklist(CFG: MainBotConfig, word):
    return word.lower() in CFG.chat_whitelist_datasets["rejected_words"]
