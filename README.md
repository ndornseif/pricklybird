# pricklybird
Convert binary data into a human friendly format.

## Overview
Binary data like encryption keys, wallet addresses and hash digests are most 
often represented using hexadecimal when humans are supposed to interact with them. 
Large strings of hexadecimal are however almost impossible to remember, 
annoying and error-prone to write on paper and hard to give to another person orally, 
over the phone for example.   
`pricklybird` is a method for conversion of arbitrary binary data into more
human-friendly words, where each word represents a single byte. A CRC8 sum is 
attached to reduce the chance of incorrect decoding.  
`0xDEADBEEF` becomes `skit-most-opal-rash-ruin` for example.

## Wordlist
The words used to represent byte values were chosen for a constant length of
four characters. Similarly spelled words that could lead to confusion were not 
included. All words are in the English language and made up of only ASCII-compatible
characters.

The entire wordlist has 256 entries and is 1024 bytes long if not including null terminators.
It can be found in the [wordlist](wordlist.txt) file. The words appear in order
and are separated by newlines, meaning that the first word corresponds to a 
byte value of `0x00`, the second to `0x01`, continuing this pattern until the 256th word that corresponds to `0xFF`.

## Specification
- The binary data `b` to be transmitted must be supplied in multiples of eight bits (bytes).
- A CRC-8 checksum `c` with polynomial `0x07` is calculated over `b`.
- `c` is then appended to `b`.
- An output string `s` is constructed. 
- For each byte in the extended data (`b` with `c` appended), 
the corresponding word from the wordlist is added to `s`. 
- Each word, except the last one, is immediately followed by a Hyphen-Minus character (`-`).

## Implementation
Reference implementations in the following programming languages can be found
in the `impl` directory:
- Python
- Rust
- C

## License
This project may be licensed under the MIT License.