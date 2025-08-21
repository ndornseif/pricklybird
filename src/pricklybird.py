#!/usr/bin/env python

"""
Functions to generate pricklybird codes from arbitrary binary data.
Will run selftest when executed as a script.
"""

WORDLIST = [
    "perm",
    "evil",
    "lady",
    "chip",
    "tutu",
    "ebay",
    "plot",
    "rage",
    "cold",
    "dose",
    "duck",
    "rust",
    "slip",
    "wavy",
    "wing",
    "ride",
    "lend",
    "wish",
    "swim",
    "down",
    "game",
    "acts",
    "heat",
    "yoga",
    "mule",
    "aloe",
    "stud",
    "slob",
    "hung",
    "acre",
    "life",
    "user",
    "kiwi",
    "malt",
    "rope",
    "view",
    "bony",
    "shed",
    "skew",
    "self",
    "flop",
    "omen",
    "rack",
    "lift",
    "boil",
    "deed",
    "cult",
    "hash",
    "chef",
    "kite",
    "duct",
    "dock",
    "pork",
    "fool",
    "spew",
    "hunt",
    "tusk",
    "mate",
    "wimp",
    "fang",
    "tart",
    "etch",
    "atom",
    "darn",
    "zone",
    "data",
    "wink",
    "only",
    "buck",
    "kilt",
    "stir",
    "item",
    "nerd",
    "gala",
    "tidy",
    "upon",
    "spur",
    "disk",
    "pogo",
    "mold",
    "mull",
    "pout",
    "send",
    "unit",
    "math",
    "keep",
    "sham",
    "land",
    "volt",
    "grab",
    "walk",
    "dill",
    "quit",
    "veto",
    "gown",
    "skid",
    "east",
    "smog",
    "blob",
    "wool",
    "year",
    "flip",
    "gore",
    "coke",
    "dust",
    "poet",
    "rake",
    "cape",
    "cure",
    "fled",
    "cage",
    "sage",
    "halt",
    "wake",
    "salt",
    "cope",
    "suds",
    "wick",
    "even",
    "taps",
    "calm",
    "boat",
    "left",
    "oval",
    "flag",
    "wind",
    "bust",
    "undo",
    "lazy",
    "king",
    "cone",
    "yard",
    "plus",
    "late",
    "bats",
    "tank",
    "raid",
    "bush",
    "slit",
    "snap",
    "grub",
    "kick",
    "case",
    "poem",
    "colt",
    "polo",
    "fray",
    "fade",
    "sect",
    "rant",
    "sift",
    "bash",
    "park",
    "wilt",
    "dish",
    "blot",
    "hate",
    "silk",
    "eats",
    "doze",
    "navy",
    "grew",
    "scan",
    "desk",
    "void",
    "lily",
    "robe",
    "deal",
    "ship",
    "surf",
    "gulf",
    "shop",
    "same",
    "most",
    "bath",
    "lens",
    "mace",
    "chow",
    "fact",
    "kung",
    "step",
    "take",
    "name",
    "dial",
    "dime",
    "nail",
    "tree",
    "rule",
    "golf",
    "stop",
    "opal",
    "mama",
    "doll",
    "lent",
    "muse",
    "romp",
    "goal",
    "tilt",
    "shun",
    "rice",
    "stew",
    "shut",
    "ruin",
    "last",
    "grit",
    "jump",
    "jaws",
    "drab",
    "rush",
    "cost",
    "rich",
    "clad",
    "glad",
    "slum",
    "ajar",
    "wipe",
    "wise",
    "ruby",
    "hush",
    "lung",
    "tile",
    "tall",
    "skit",
    "mute",
    "sled",
    "lion",
    "putt",
    "hull",
    "push",
    "coat",
    "neon",
    "glow",
    "skip",
    "drum",
    "path",
    "risk",
    "wife",
    "slug",
    "boss",
    "rash",
    "cork",
    "stem",
    "grid",
    "acid",
    "turf",
    "exit",
    "jolt",
    "pace",
    "cozy",
    "aids",
    "chew",
    "half",
    "edge",
    "neat",
    "blog",
    "date",
]

REVERSE_WORDLIST: dict[str, int] = {word: i for i, word in enumerate(WORDLIST)}


def calculate_crc8(data: bytearray, polynominal: int) -> bytearray:
    """
    Calculate CRC-8 checksum for the given bytearray.
    """
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynominal
            else:
                crc <<= 1
            crc &= 0xFF

    return crc.to_bytes(1)


def bytes_to_words(data: bytearray) -> list[str]:
    """
    Return a string with each input byte mapped to the corresponding pricklybird word"

    ## Usage
    >>> bytes_to_words(bytearray([1, 2, 3, 4]))
    ['evil', 'lady', 'chip', 'tutu']
    """
    return [WORDLIST[int(b)] for b in data]


def convert_to_pricklybird(data: bytearray) -> str:
    """
    Convert arbitrary data to pricklybird words and attach CRC.

    The attached CRC is a CRC-8 with polynominal 0x07.
    The words are sperated using a colon `-`.

    ## Usage
    >>> convert_to_pricklybird(bytearray([1, 2, 3, 4]))
    'evil-lady-chip-tutu-hull'
    """
    return "-".join(bytes_to_words(data + calculate_crc8(data, 0x07)))


def words_to_bytes(words: list[str]) -> bytearray:
    """
    Map a list of pricklybird words to their coresponding bytes.

    ## Usage
    >>> words_to_bytes(['evil', 'lady', 'chip', 'tutu'])
    bytearray(b'\x01\x02\x03\x04')
    """
    data = bytearray(len(words))
    for i, word in enumerate(words):
        index = REVERSE_WORDLIST.get(word)
        if index is None:
            raise ValueError(f"{word} at index {i} is not a valid pricklybird keyword.")
        data[i] = index
    return data


def convert_from_pricklybird(words: str, ignore_crc: bool = False) -> bytearray:
    """
    Convert pricklybird words to bytearray and check CRC.

    Setting `ignore_crc` to True will ignore an incorrect CRC
    otherwise it raises a `ValueError`.

    ## Usage
    >>> convert_from_pricklybird('evil-lady-chip-tutu-hull')
    bytearray(b'\x01\x02\x03\x04')
    """
    if not words.strip():
        raise ValueError("Empty input string")

    word_list = words.split("-")
    if len(word_list) < 2:  # Need at least data + CRC
        raise ValueError("Input to short, must contain at least 2 words.")

    data = words_to_bytes(word_list)
    if not ignore_crc and calculate_crc8(data, 0x07) != b"\x00":
        raise ValueError("Invalid CRC while decoding words.")
    return data[:-1]


def selftest(seed: int = 1) -> int:
    def generate_test_data(seed: int) -> bytearray:
        """
        Implementation of Lehmer64 PRNG.
        """
        state = seed & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        multiplier = 0xDA942042E4DD58BA
        for _ in range(128):
            state = (state * multiplier) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        result = bytearray()
        for _ in range(128):
            state = (state * multiplier) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            random_val = state >> 64 & 0xFFFFFFFFFFFFFFFF
            result += random_val.to_bytes(8, "little")
        return result

    # Doctest examples
    assert bytes_to_words(bytearray([1, 2, 3, 4])) == [
        "evil",
        "lady",
        "chip",
        "tutu",
    ]
    assert convert_to_pricklybird(bytearray([1, 2, 3, 4])) == "evil-lady-chip-tutu-hull"
    assert words_to_bytes(["evil", "lady", "chip", "tutu"]) == bytearray(
        b"\x01\x02\x03\x04"
    )
    assert convert_from_pricklybird("evil-lady-chip-tutu-hull") == bytearray(
        b"\x01\x02\x03\x04"
    )

    # Long data selftest
    test_data = generate_test_data(seed)
    words = convert_to_pricklybird(test_data)
    decoded_data = convert_from_pricklybird(words)
    assert decoded_data == test_data

    # Flip bit in first word
    test_data[0] ^= 1
    incorrect_word = bytes_to_words(test_data[0:1])[0]
    # Replace fist word with incorrect one
    words = incorrect_word[:4] + words[4:]
    try:
        convert_from_pricklybird(words)
    except ValueError:  # Incorrect CRC was detected
        pass
    else:
        raise AssertionError

    print("Selftest passed.")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(selftest())
