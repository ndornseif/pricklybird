// pricklybird rust reference implementation
// Copyright (c) 2025 N. Dornseif
//
// Licensed under the MIT license
// <LICENSE or https://opensource.org/licenses/MIT>.
// This file may not be copied, modified, or distributed
// except according to those terms.

//! Convert binary data into a human-friendly format.
//!
//! This is the pricklybird command line tool.

use std::fmt;
use std::io::{self, Read as _, Write as _};

use clap::Parser;

use pricklybirdlib::{DecodeError, convert_from_pricklybird, convert_to_pricklybird};

/// The conversion failed.
pub enum AppError {
    /// The conversion failed due to some IO error.
    Io(io::Error),
    /// The conversion failed due to an error while decoding a pricklybird string.
    Decode(DecodeError),
    /// Incorrect arguments were supplied via the CLI.
    ArgumentError(String),
}

impl From<io::Error> for AppError {
    fn from(error: io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<DecodeError> for AppError {
    fn from(error: DecodeError) -> Self {
        Self::Decode(error)
    }
}

// Implement Display for AppError to format both error types properly
impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(err) => write!(f, "IO error: {err}"),
            Self::Decode(err) => write!(f, "{err}"),
            Self::ArgumentError(msg) => write!(f, "Invalid arguments. {msg}"),
        }
    }
}

impl fmt::Debug for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Delegate to Display implementation
        fmt::Display::fmt(self, f)
    }
}

#[derive(Parser)]
#[command(
    name = clap::crate_name!(),
    version = clap::crate_version!(),
    about = clap::crate_description!(),
)]
/// Collect arguments supplied via command line.
struct Cli {
    /// Attempt conversion from pricklybird string to bytes.
    #[arg(short = 'b', long = "convert-from-pricklybird")]
    convert_from: bool,

    /// Convert bytes to pricklybird string.
    #[arg(short = 'p', long = "convert-to-pricklybird")]
    convert_to: bool,
}

/// Read from stdin and output to stdout.
/// By default conversion from a pricklybird string to bytes is attemped.
/// Setting the `-c` flag will instead convert bytes to a pricklybird string.
pub fn main() -> Result<(), AppError> {
    let cli = Cli::parse();
    if cli.convert_to && cli.convert_from {
        return Err(AppError::ArgumentError(
            "Can not convert from and to pricklybird at the same time.".to_owned(),
        ));
    }
    if cli.convert_to {
        let mut buffer = Vec::<u8>::new();
        let _ = io::stdin().read_to_end(&mut buffer)?;
        let output = convert_to_pricklybird(&buffer);
        print!("{}", &output);
        io::stdout().flush()?;
    } else {
        let mut buffer = String::new();
        let _ = io::stdin().read_to_string(&mut buffer)?;
        let output = convert_from_pricklybird(&buffer)?;
        io::stdout().write_all(&output)?;
        io::stdout().flush()?;
    }
    Ok(())
}