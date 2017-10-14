//! A Rust port of the Pi side of the Rover project, aimed to be safe and performant
//!
//! # Goals
//!
//! ## Safety
//!
//! Hopefully, this port will make the Rover more stable and less prone to errors
//! or issues at runtime
//!
//! ## Performance
//!
//! Python is simply not fast enough to be run with high performance on a processor
//! while doing complex and expensive tasks such as image processing and recognition
//! as limited as the Pi has -- performance is a priority, and this port should help
//! achieve it
//!
//! ## Image Recognition
//!
//! Image recognition could be a seriously cool feature to implement, perhaps using
//! cv-rs

#[macro_use]
extern crate log;
extern crate log4rs;
extern crate toml;
extern crate csv;
extern crate chrono;
extern crate serial;
#[macro_use]
extern crate serde_derive;

#[macro_use]
mod macros;
mod config;
mod setup;
mod protocol;

use std::time::Duration;
use std::thread;
use std::io::{Read, BufRead, BufReader};
use std::ascii::AsciiExt;
use protocol::{Message, CommandHandler};

fn main() {

    println!("Rover3 Pi started!");

    let config = setup::config();
    setup::logging(&config.logging);

    info!("Logging started!");
    info!("Setting up serial port...");

    let mut port = &mut *handle_err![(setup::serial_port(&config.serial)) with err => {
        // In the event of a failure acquiring the serial port (e.g baudrate unsupported)
        // then sleep forever to let the other threads run
        warn!(
            "Error opening serial port: \"{}\" -- is the baudrate unsupported?",
            err
        );

        limited_mode("serial not available");
    }];

    info!("Serial port setup finished!");
    info!("Setting up data recording...");

    let mut data_records = setup::data_recording(&config.records);

    info!("Data recording setup finished!");
    info!("All setup finished!");

    let mut port_reader = BufReader::new(&mut port);

    let mut parser = protocol::SerialParser::new();
    let mut packet = Vec::new();

    // Check that data is well formed
    // This lets us check that the baudrate is set correctly
    debug!("Reading from port to analyse whether the baudrate is set correctly...");
    let mut buf: [u8; 100] = [0; 100];

    loop {
        if let Err(error) = port_reader.read_exact(&mut buf) {
            error!("Error reading from port for analysis: {:?}", error);
            debug!("Retrying...");
        } else {
            debug!("Read successfully from port for analysis");
            break;
        }
    }

    if !buf.is_ascii() {
        error!("First 100 bytes received from arduino not ascii! Is the baudrate misconfigured?");
        trace!("{:?}", &buf.to_vec());

        limited_mode("serial not configured correctly");
    }

    // Clear state of port
    debug!("Reading from port to clear state...");

    loop {
        let throw_away = &mut Vec::new();

        if let Err(error) = port_reader.read_until(config::SERIAL_TERMINATOR as u8, throw_away) {
            error!("Error reading from port to clear state: {:?}", error);
            debug!("Retrying...");
        } else {
            debug!("Read successfully from port to clear state");
            break;
        }
    }

    loop {
        debug!("Reading...");

        // Clear packet of previous data
        packet.clear();

        if let Err(error) = port_reader.read_until(config::SERIAL_TERMINATOR as u8, &mut packet) {
            error!("Error reading from serial port: {}", error);
            continue;
        }

        trace!("Read finished");
        debug!("Parsing...");

        let data =
            handle_err![(std::str::from_utf8(packet.as_slice())) with err => {
                error!("Error parsing packet as a utf-8 string: {:?}", err);
                continue;
        }];

        // TODO extract to handle function

        let message_option =
            handle_err![(parser.parse(data)) with err => {
                error!("Error parsing serial packet: {:?}", err);
                continue;
        }];

        let message =
            handle_option![message_option => {
                error!("Reached EOF -- not enough data? Was the data malformed?");
                continue;
        }];

        trace!("Parsing complete");

        info!("Received message from Arduino");

        match message {
            Message::Data(data) => {
                info!("Data (see data records)");
                if let Err(error) = data_records.serialize(data) {
                    error!(
                        "Error serializing data to write to records: \"{:?}\"",
                        error
                    );
                } else if let Err(error) = data_records.flush() {
                        error!("Error flushing csv data record writer: \"{:?}\"", error);
                }
            }
            Message::Command(command) => {
                info!("Command: {:?}", command);
                CommandHandler::handle(command);
            }
        }
    }
}

/// Run 'limited mode' loop.
///
/// Will be run if **near-fatal** errors occur, such as failure to open serial
/// port. This should never happen, as it probably means that the baudrate is unsupported
/// by the raspberry pi, which it should be.
/// **Under normal operation, this should never run.**.
fn limited_mode(reason: &str) -> ! {
    error!("Operating in limited mode -- {}", reason);

    let sleep_duration = Duration::from_secs(60);

    loop {
        thread::sleep(sleep_duration);
    }
}
