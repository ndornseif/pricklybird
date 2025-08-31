# pricklybird
Convert binary data into a human-friendly format.

## Notice

These specifications describe a development version.
Parameters are subject to change until a proper version is defined.

## Overview

Binary data blocks like encryption keys, wallet addresses, and hash digests are most 
often represented using hexadecimal when humans are supposed to interact with them. 
Large strings of hexadecimal are, however, almost impossible to remember, 
annoying and error-prone to write on paper and hard to communicate to another person orally, 
over the phone for example.   
`pricklybird` is a method for conversion of arbitrary binary data into more
human-friendly words, where each word represents a single byte. A CRC-8 checksum is 
attached to allow the detection of errors during decoding.  
`0xDEADBEEF` becomes `turf-port-rust-warn-void`, for example.

## Wordlist

The words used to represent byte values were chosen for a constant length of
four characters. Words that could lead to confusion due to similar pronunciation were avoided. 
All words appear in English language dictionaries and are made up of only ASCII-compatible
characters. No two words share the same first and last character. 

The entire wordlist has 256 alphabetically sorted entries, one for every possible byte value.
It can be found in the [wordlist](wordlist.txt) file. 
The words appear in order and are separated by newlines, 
meaning that the first word corresponds to a byte value of `0x00`, the second to `0x01`, 
continuing this pattern until the 256th word, which corresponds to `0xFF`.

## Specification

This specification applies to version `dev` of pricklybird.  
The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Cyclic redundancy check

The CRC to be used shall be defined as follows:  

- Output width of 8 bits
- Division using the polynomial `0x1D`
- An initial value of zero
- No input or output reflection
- No XOR operation on the output
- Remainder after division of data with correct CRC appended is zero
- Check value of the ASCII string `"123456789"` as input is `0x37`

In testing this configuration showed an error detection rate close to the maximum
value `255 / 256 ≈ 99.6%` that can be achieved for an 8-bit checksum. 
These tests were performed with the expected error scenarios of two adjacent bytes being swapped and a byte being replaced by a random incorrect one. 

### Conversion to pricklybird format

- The binary data `b` to be converted must be supplied in multiples of eight bits
- If the length of `b` is less than one byte, an empty string must be returned.
- A CRC checksum `c` with the previously defined parameters is calculated over `b`
- `c` is then appended to `b` to obtain the intermediate binary data `i`
- An output string `s` is constructed.
- For each byte in `i`, the corresponding word from the wordlist is added to `s`
- The words should be output in all lowercase.
- Each word, except the last one, is immediately followed by a Hyphen-Minus character (-)
- `s` is returned as the output

### Conversion from pricklybird format

- The pricklybird input string `s` must be a valid UTF-8 string.
- If `s` is empty the implementation must return an error.
- ASCII whitespace is trimmed from the beginning and end of `s` to get the shortened input string `u`, the implementaion may also trim non ASCII whitespace as defined by the unicode standard.
- If `u` contains any character that is not a Hyphen-Minus or a letter from A-Z (case-insensitive) the input is considered invalid and an error must be returned
- `u` is split into a list of words `l` at every Hyphen-Minus character (-)
- If `l` is shorter than two words the input is invalid, since with checksum attached, every
pricklybird value must be at least two words long. The implementation must return an error
- The intermediate binary data `i` is constructed by appending the corresponding byte
according to the wordlist for each word in `l`
- The lookup in the wordlist must be case *insensitive*
- If a word does not appear in the wordlist the implementation must return an error
- Calculating a CRC checksum using the previously defined parameters over `i` should return a remainder of zero
- If the checksum remainder does not equal zero an error must be returned
- The last byte of `i` is removed to obtain the decoded binary data `b`
- `b` is returned as the output

### Word lookup hash table

Given the fact that no two words share the same first and last letter, a perfect hash function can be
trivially constructed. The reference implementations assign a numeric value to each letter of the alphabet
in order. Meaning `A` gets assigned the value `0`, `B` the value `1`, continuing in this pattern until `Z` that gets assigned `25`.
An index into a lookup table is calculated by adding the letter value of the words first letter to the value of the last letter multiplied by 26.  
In python code:   
```python
def lookup_index(word): return letter_value(word[0]) + letter_value(word[-1]) * 26
```
Example: For the word `"turf"`, first letter `t` (value 19), last letter `f` (value 5). The index is `19 + 5 * 26 = 149`.

The highest value returned by this function for all words in the wordlist is 655, and the lowest is 0.
For input with invalid words the highest value becomes 675 with a word that has `z` as its first and last letter, since `25 + 25 * 26 = 675`. 
Meaning a 656 entry lookup array that maps the hash values to the byte values can be constructed,
to obtain the byte value given the first and last letter of a word. The implementation must still check that the other two letters actually match the word 
that is assigned to the recovered byte value.
If the additional memory overhead imposed by the lookup table cannot be afforded, the wordlist can also be searched via linear
or binary search given it is alphabetically sorted.

### Test vectors

A functioning implementation should be able to convert these bytes and pricklybird values into each other.

| Bytes          | Pricklybird                     |
| :------------- | :------------------------------ |
| `0xDEADBEEF`   | `turf-port-rust-warn-void`      |
| `0x4243`       | `flea-flux-full`                |
| `0x1234567890` | `blob-eggs-hair-king-meta-yell` |
| `0x0000000000` | `acid-acid-acid-acid-acid-acid` |
| `0xFFFFFFFFFF` | `zone-zone-zone-zone-zone-sand` |

The following test vectors should raise decoding errors in a functioning implementation.

| Pricklybird                | Reason                        |
| :------------------------- | :---------------------------- |
| `a®¿a-orca`                | Contains invalid characters   |
| `gäsp-risk-king-orca-husk` | Contains invalid characters   |
| `-risk-king-orca-husk`     | Incorrectly formatted         |
| `flea- \t \t-full`         | Contains internal whitespace  |
| `flea-aaa\0-full`          | Contains null byte            |
| `flea-\x7faaa-full`        | Contains control character    |

## Implementations

Reference implementations in the following programming languages can be found
in the `impl` directory:

- Python
- Rust

### Command line utility
A command line utility for conversion is provided in the rust implementation.
Input is read from stdin and output written to stdout.

By default conversion from pricklybird to bytes is attempted.
This can be explicitly set using the `-b` flag.
```bash
% echo "flea-flux-full" | pricklybird -b | xxd -ps
4243
```

To convert bytes to pricklybird use the `-p` flag.
```bash
% echo "4243" | xxd -r -p | pricklybird -p
flea-flux-full
```

## License

This project is licensed under the MIT License.