// pricklybird rust reference implementation
// Copyright (c) 2025 N. Dornseif
//
// Licensed under the MIT license
// <LICENSE or https://opensource.org/licenses/MIT>.
// This file may not be copied, modified, or distributed
// except according to those terms.

//! # pricklybird
//! Convert binary data into a human friendly format.
//!

#![warn(
    missing_docs,
    missing_debug_implementations,
    rust_2018_idioms,
    clippy::missing_docs_in_private_items,
    clippy::missing_errors_doc,
    clippy::missing_panics_doc,
    clippy::pedantic,
    clippy::redundant_clone,
    clippy::needless_pass_by_value
)]

mod constants;

use crate::constants::{BYTE_WORDLIST, CRC8_TABLE, HASH_TABLE, word_hash};
use std::fmt;

/// An error occured while trying to decode pricklybird words.
#[derive(Debug, Clone)]
pub enum DecodeError {
    /// General decoding error
    General(String),
    /// Invalid CRC
    CRCError,
}

impl fmt::Display for DecodeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DecodeError::General(msg) => write!(f, "Unable to decode pricklybird words: {msg}"),
            DecodeError::CRCError => write!(f, "Invalid CRC detected."),
        }
    }
}

impl std::error::Error for DecodeError {}

/// Result used in decode functions that can fail.
type Result<T> = std::result::Result<T, DecodeError>;

/// Calculate a CRC-8 based on the precomputed table.
///
/// # CRC parameters
/// - Output width of 8 bits
/// - Division using the polynominal `0x1D`
/// - An inital value of zero
/// - No input or output reflection
/// - No XOR operation on the output
/// - Remainder after division of data with correct CRC appended is zero
///
/// # Usage
/// ```
/// use pricklybird::calculate_crc8;
/// let crc = calculate_crc8(b"123456789");
/// assert_eq!(crc, 0x37);
/// ```
#[must_use]
pub fn calculate_crc8(data: &[u8]) -> u8 {
    let mut crc = 0u8;

    for &byte in data {
        crc = CRC8_TABLE[(crc ^ byte) as usize];
    }
    crc
}

/// Return a vector of words with each input byte mapped to matching pricklybird word.  
///
/// The words are encoded as four byte arrays of UTF-8.
///
/// # Usage
/// ```
/// use pricklybird::bytes_to_words;
/// let data = [0x42u8, 0x43];
/// let words = bytes_to_words(&data);
/// assert_eq!(words, [[102, 108, 101, 97], [102, 108, 117, 120]]);
/// ```
#[must_use]
pub fn bytes_to_words(data: &[u8]) -> Vec<[u8; 4]> {
    let mut result_words = Vec::with_capacity(data.len());

    for &byte in data {
        result_words.push(BYTE_WORDLIST[byte as usize]);
    }
    result_words
}

/// Return a vector of bytes coresponding to the pricklybird words supplied as input.
///
/// # Errors
/// Will return `DecodeError::General` if:
/// - The input contains non ASCII compatible characters
/// - The words in the input are not all four characters long
/// - Words in the input dont appear in the wordlist
///
/// # Usage
/// ```
/// use pricklybird::words_to_bytes;
/// let words = vec!["flea", "flux"];
/// let data = words_to_bytes(&words).unwrap();
/// assert_eq!(data, vec![0x42, 0x43]);
/// ```
pub fn words_to_bytes(words: &Vec<&str>) -> Result<Vec<u8>> {
    let mut bytevector = Vec::<u8>::with_capacity(words.len());

    for word in words {
        if !word.is_ascii() {
            return Err(DecodeError::General(
                "Input must only contain ASCII compatible UTF-8.".into(),
            ));
        }
        let word_lower = word.to_lowercase();
        let word_bytes = word_lower.as_bytes();
        if word_bytes.len() != 4 {
            return Err(DecodeError::General(
                "Input words must be four characters long.".into(),
            ));
        }
        let recovered_byte = HASH_TABLE[word_hash(word_bytes[0], word_bytes[3])];

        // Verify that the byte from the lookup operation matches the word.
        if word_bytes != BYTE_WORDLIST[recovered_byte as usize] {
            return Err(DecodeError::General(
                "Invalid word detected in input.".into(),
            ));
        }
        bytevector.push(recovered_byte);
    }
    Ok(bytevector)
}

/// Convert arbitrary data to pricklybird words and attach CRC.
///
/// # Usage
/// ```
/// use pricklybird::convert_to_pricklybird;
/// let data = [0x42u8, 0x43];
/// let code = convert_to_pricklybird(&data);
/// assert_eq!(code, "flea-flux-full");
/// ```
#[allow(clippy::missing_panics_doc)]
#[must_use]
pub fn convert_to_pricklybird(data: &[u8]) -> String {
    if data.is_empty() {
        return String::new();
    }
    let crc = calculate_crc8(data);
    let mut data_with_crc = Vec::with_capacity(data.len() + 1);
    data_with_crc.extend_from_slice(data);
    data_with_crc.push(crc);

    // Unwrap is safe here since we know the wordlist and seperator are valid UTF-8.
    String::from_utf8(bytes_to_words(&data_with_crc).join(&b'-')).unwrap()
}

/// Convert pricklybird words to bytearray and check CRC.
///
/// # Errors
/// Will return `DecodeError::General` if:
/// - The input is less than two words long,
/// - The input contains non ASCII compatible characters
/// - The words in the input are not all four characters long
/// - Words in the input dont appear in the wordlist
///
/// Will return `DecodeError::CRCError` if the CRC value does not match the input.
///
///
/// # Usage
/// ```
/// use pricklybird::convert_from_pricklybird;
/// let code = "flea-flux-full";
/// let data = convert_from_pricklybird(code).unwrap();
/// assert_eq!(data, [0x42u8, 0x43]);
/// ```
pub fn convert_from_pricklybird(words: &str) -> Result<Vec<u8>> {
    let word_vec: Vec<&str> = words.split('-').collect();

    if word_vec.len() < 2 {
        return Err(DecodeError::General(
            "Input must be at least two words long.".into(),
        ));
    }

    let mut data = words_to_bytes(&word_vec)?;
    if calculate_crc8(&data) != 0 {
        return Err(DecodeError::CRCError);
    }
    // Remove CRC
    data.pop();
    Ok(data)
}

/// Test the conversion from and to pricklybird.
#[cfg(test)]
mod pricklybird_tests {
    use super::*;
    /// Seed used to generate test data using the PRNG implemented in `generate_test_data`.
    const TEST_DATA_SEED: u128 = 1;
    /// How many byes of test data to use for conversion tests.
    const TEST_DATA_BYTES: usize = 4096;

    /// Generates pseudorandom test data using the Lehmer64 LCG.
    #[allow(clippy::cast_possible_truncation)]
    fn generate_test_data(seed: u128) -> Vec<u8> {
        const MULTIPLIER: u128 = 0xDA942042E4DD58B5;
        const WARMUP_ITERATIONS: usize = 128;
        let mut state = seed;
        // Mix up the state a little to compensate for potentialy small seed.
        for _ in 0..WARMUP_ITERATIONS {
            state = state.wrapping_mul(MULTIPLIER);
        }

        let mut result = Vec::<u8>::with_capacity(TEST_DATA_BYTES);
        for _ in 0..(TEST_DATA_BYTES / 8) {
            state = state.wrapping_mul(MULTIPLIER);
            let random_val = (state >> 64) as u64;
            result.extend_from_slice(&random_val.to_le_bytes());
        }
        result
    }

    /// Test the standard vectors supplied with the specification.
    #[test]
    fn test_vectors() {
        let test_vectors = vec![
            (vec![0xDEu8, 0xAD, 0xBE, 0xEF], "turf-port-rust-warn-void"),
            (vec![0x42u8, 0x43], "flea-flux-full"),
            (
                vec![0x12u8, 0x34, 0x56, 0x78, 0x90],
                "blob-eggs-hair-king-meta-yell",
            ),
            (vec![0u8; 5], "acid-acid-acid-acid-acid-acid"),
            (vec![0xFFu8; 5], "zone-zone-zone-zone-zone-sand"),
        ];

        for (data, words) in test_vectors {
            // Test converting bytes to pricklybird.
            assert_eq!(
                words,
                convert_to_pricklybird(&data),
                "Converter failed to convert {:?} test vector to pricklybird",
                data
            );

            // Test converting pricklybird to bytes.
            assert_eq!(
                data,
                convert_from_pricklybird(words).unwrap(),
                "Converter failed to convert {} test vector to bytes",
                words
            );
        }
    }

    /// Test conversion to and from pricklybird on pseudorandom test data.
    #[test]
    fn test_simple_conversion() {
        let test_data = generate_test_data(TEST_DATA_SEED);
        let coded_words = convert_to_pricklybird(&test_data);
        let decoded_data = convert_from_pricklybird(&coded_words).unwrap();
        assert_eq!(
            test_data, decoded_data,
            "Converter did not correctly endcode or decode data."
        );
    }

    /// Test that pricklybird input containing mixed case is properly decoded.
    #[test]
    fn test_uppercase() {
        assert_eq!(
            vec![0xDEu8, 0xAD, 0xBE, 0xEF],
            convert_from_pricklybird("TUrF-Port-RUST-warn-vOid").unwrap(),
            "Converter did not correctly decode upercase data."
        );
    }

    /// Test that replacing a pricklybird word is detected using the CRC-8.
    #[test]
    fn test_error_detection_bit_flip() {
        let mut test_data = generate_test_data(TEST_DATA_SEED);
        let coded_words = convert_to_pricklybird(&test_data);
        test_data[0] ^= 1;
        let incorrect_word =
            String::from_utf8(bytes_to_words(&test_data[0..1])[0].to_vec()).unwrap();
        let incorrect_coded_words = format!("{}{}", &incorrect_word[..4], &coded_words[4..]);
        assert!(
            convert_from_pricklybird(&incorrect_coded_words).is_err(),
            "Converter did not detect error in corrupted input."
        );
    }

    /// Check that swapping two adjacent words is detected using the CRC-8.
    #[test]
    fn test_error_detection_adjacent_swap() {
        let test_data = generate_test_data(TEST_DATA_SEED);
        let coded_words = convert_to_pricklybird(&test_data);
        let mut word_vec: Vec<&str> = coded_words.split('-').collect();
        word_vec.swap(0, 1);
        let swapped_coded_words = word_vec.join("-");
        assert!(
            matches!(
                convert_from_pricklybird(&swapped_coded_words),
                Err(DecodeError::CRCError)
            ),
            "Converter did not detect error caused by word swap."
        );
    }

    /// Check that edge cases result in the correct errors.
    #[test]
    fn test_unusual_input() {
        let edge_cases = vec![
            ("", "empty input"),
            ("orca", "input to short"),
            ("®¿", "non ASCII iput."),
            ("gäsp-risk-king-orca-husk", "non ASCII iput."),
            ("-risk-king-orca-husk", "incorrectly formated input"),
            ("gasp-rock-king-orca-husk", "incorrect word in input"),
            // Check that no index out of bound error is thrown when the highest
            // possible value is used to index the hash table.
            ("zzzz-king", "incorrect word in input"),
        ];
        for (edge_case_input, error_reason) in edge_cases {
            assert!(
                convert_from_pricklybird(edge_case_input).is_err(),
                "{}",
                error_reason
            );
        }
    }

    /// Check that empty input results in empty output.
    #[test]
    fn test_empty_input() {
        assert_eq!("", convert_to_pricklybird(&[]));
        assert!(bytes_to_words(&[]).is_empty());
        assert!(words_to_bytes(&Vec::<&str>::new()).unwrap().is_empty());
    }
}

/// Check functionality of the cyclic redundancy check.
#[cfg(test)]
mod crc8_tests {
    use super::*;

    /// Check that CRC-8 of empty input is zero.
    #[test]
    fn test_empty_input() {
        let test_data: &[u8] = &[];
        let result = calculate_crc8(test_data);
        assert_eq!(0, result, "CRC-8 of empty data should be 0.");
    }

    /// Check that CRC-8 of single byte is equal to the precomputed table value.
    #[test]
    fn test_table_lookup() {
        let test_data = &[0x42u8];
        let result = calculate_crc8(test_data);
        let expected = CRC8_TABLE[test_data[0] as usize];
        assert_eq!(
            expected, result,
            "CRC-8 of single byte should match table value."
        );
    }

    /// Check that data with appended correct CRC-8 has a CRC remainder of zero.
    #[test]
    fn test_with_appended_crc() {
        let mut test_data = b"Test data".to_vec();
        let crc_value = calculate_crc8(&test_data);
        test_data.push(crc_value);

        let result = calculate_crc8(&test_data);
        assert_eq!(
            0, result,
            "Data with appended correct CRC-8 should result in remainder 0."
        );
    }
}
