#!/usr/bin/env python

"""Functions to generate pricklybird codes from arbitrary binary data.

Will run selftest when executed as a script.

Copyright (c) 2025 N. Dornseif

Licensed under the MIT license
<LICENSE or https://opensource.org/licenses/MIT>.
This file may not be copied, modified, or distributed
except according to those terms.
"""

WORDLIST = [
    "acid",
    "also",
    "anti",
    "arch",
    "area",
    "atom",
    "aunt",
    "baby",
    "back",
    "ball",
    "bang",
    "bare",
    "barn",
    "beef",
    "beep",
    "beer",
    "best",
    "beta",
    "blob",
    "blow",
    "boom",
    "boss",
    "bush",
    "call",
    "calm",
    "card",
    "cars",
    "cash",
    "clay",
    "coma",
    "cook",
    "core",
    "crab",
    "crop",
    "damp",
    "dark",
    "dash",
    "data",
    "dawn",
    "deaf",
    "deal",
    "deer",
    "deny",
    "dice",
    "disc",
    "dogs",
    "draw",
    "drug",
    "drum",
    "dust",
    "east",
    "easy",
    "eggs",
    "else",
    "epic",
    "etch",
    "ever",
    "evil",
    "exam",
    "face",
    "fact",
    "fawn",
    "film",
    "fish",
    "flag",
    "flaw",
    "flea",
    "flux",
    "food",
    "four",
    "full",
    "funk",
    "fury",
    "fuzz",
    "gain",
    "game",
    "gang",
    "gasp",
    "gear",
    "germ",
    "gift",
    "girl",
    "glow",
    "gold",
    "grab",
    "guts",
    "hair",
    "half",
    "hand",
    "harm",
    "hazy",
    "help",
    "herb",
    "hero",
    "high",
    "hill",
    "hiss",
    "horn",
    "hurt",
    "husk",
    "hype",
    "icon",
    "idea",
    "idle",
    "indy",
    "info",
    "iris",
    "itch",
    "item",
    "jade",
    "jail",
    "jaws",
    "join",
    "jump",
    "jury",
    "just",
    "kale",
    "keen",
    "keto",
    "kick",
    "king",
    "kiss",
    "kiwi",
    "knob",
    "lady",
    "lake",
    "lamp",
    "last",
    "leaf",
    "lens",
    "liar",
    "lion",
    "logo",
    "long",
    "lord",
    "luck",
    "lush",
    "mage",
    "mail",
    "many",
    "mars",
    "math",
    "memo",
    "menu",
    "meta",
    "mild",
    "mini",
    "moon",
    "must",
    "nail",
    "name",
    "navy",
    "neck",
    "need",
    "next",
    "noon",
    "norm",
    "nuts",
    "oath",
    "once",
    "orca",
    "oval",
    "over",
    "page",
    "paid",
    "palm",
    "path",
    "pawn",
    "ping",
    "pins",
    "play",
    "pool",
    "poor",
    "port",
    "puff",
    "pump",
    "quit",
    "race",
    "raid",
    "rain",
    "ramp",
    "rash",
    "rats",
    "rear",
    "redo",
    "reef",
    "ring",
    "risk",
    "room",
    "ruby",
    "rust",
    "safe",
    "sail",
    "salt",
    "sand",
    "scar",
    "ship",
    "sick",
    "sign",
    "sing",
    "slab",
    "slow",
    "soda",
    "solo",
    "stay",
    "surf",
    "swim",
    "taco",
    "talk",
    "taxi",
    "team",
    "tech",
    "text",
    "tiny",
    "tips",
    "toad",
    "tofu",
    "tomb",
    "tool",
    "tour",
    "trap",
    "tuna",
    "turf",
    "twig",
    "twin",
    "type",
    "ugly",
    "undo",
    "urge",
    "user",
    "very",
    "veto",
    "vial",
    "vila",
    "void",
    "volt",
    "vote",
    "walk",
    "wall",
    "warn",
    "warp",
    "wash",
    "wear",
    "west",
    "wind",
    "wing",
    "wire",
    "wolf",
    "worm",
    "yank",
    "yard",
    "yeah",
    "yell",
    "yoga",
    "zeus",
    "zone",
]

REVERSE_WORDLIST: dict[str, int] = {word: i for i, word in enumerate(WORDLIST)}


class DecodeError(Exception):
    """Unable to decode pricklybird words."""


class CRCError(DecodeError):
    """Invalid CRC detected while decoding."""


def calculate_crc8(data: bytearray, polynominal: int) -> bytes:
    """Calculate CRC-8 checksum for the given bytearray."""
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
    """Return a string with each input byte mapped to matching pricklybird word.

    ## Usage
    >>> bytes_to_words(bytearray([1, 2, 3, 4]))
    ['also', 'anti', 'arch', 'area']
    """
    return [WORDLIST[int(b)] for b in data]


def convert_to_pricklybird(data: bytearray) -> str:
    """Convert arbitrary data to pricklybird words and attach CRC.

    The attached CRC is a CRC-8 with polynominal 0x07.
    The words are sperated using a colon `-`.

    ## Usage
    >>> convert_to_pricklybird(bytearray([1, 2, 3, 4]))
    'also-anti-arch-area-undo'
    """
    return "-".join(bytes_to_words(data + calculate_crc8(data, 0x07)))


def words_to_bytes(words: list[str]) -> bytearray:
    r"""Map a list of pricklybird words to their coresponding bytes.

    ## Usage
    >>> words_to_bytes(["evil", "lady", "chip", "tutu"])
    bytearray(b'\x01\x02\x03\x04')
    """
    data = bytearray(len(words))
    for i, word in enumerate(words):
        index = REVERSE_WORDLIST.get(word)
        if index is None:
            error_msg = f"{word} at index {i} is not a valid pricklybird keyword."
            raise DecodeError(error_msg)
        data[i] = index
    return data


def convert_from_pricklybird(words: str, ignore_crc: bool = False) -> bytearray:
    r"""Convert pricklybird words to bytearray and check CRC.

    Setting `ignore_crc` to True will ignore an incorrect CRC
    otherwise it raises a `CRCError`.

    ## Usage
    >>> convert_from_pricklybird("evil-lady-chip-tutu-hull")
    bytearray(b'\x01\x02\x03\x04')
    """
    if not words.strip():
        raise DecodeError("Empty input string.")

    word_list = words.split("-")
    if len(word_list) < 2:  # Need at least data + CRC
        raise DecodeError("Input to short, must contain at least 2 words.")

    data = words_to_bytes(word_list)
    if not ignore_crc and calculate_crc8(data, 0x07) != b"\x00":
        raise CRCError("Invalid CRC while decoding words.")
    return data[:-1]


def _selftest(seed: int = 1) -> int:
    def generate_test_data(seed: int) -> bytearray:
        """Implement the Lehmer64 PRNG."""
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
        "also",
        "anti",
        "arch",
        "area",
    ]
    assert convert_to_pricklybird(bytearray([1, 2, 3, 4])) == "also-anti-arch-area-undo"
    assert words_to_bytes(["also", "anti", "arch", "area"]) == bytearray(
        b"\x01\x02\x03\x04"
    )
    assert convert_from_pricklybird("also-anti-arch-area-undo") == bytearray(
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
    except CRCError:  # Incorrect CRC was detected
        pass
    else:
        raise AssertionError

    print("Selftest passed.")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(_selftest())
