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
extern crate chrono;
extern crate serial;
#[macro_use]
extern crate serde_derive;

mod config;
mod setup;

use std::time::Duration;
use std::thread;

fn main() {

    println!("Rover3 Pi started!");

    let config = setup::config();
    setup::logging(&config);

    info!("Logging started!");
    info!("Setup finished");

    let port = &mut *match setup::serial_port(&config) {
        Ok(port) => port,

        // In the event of a failure acquiring the serial port (e.g baudrate unsupported)
        // then sleep forever to let the other threads run
        Err(error) => {
            warn!(
                "Error opening serial port: \"{}\" -- is the baudrate unsupported?",
                error
            );
            warn!("Operating in limited mode; serial not available");

            let sleep_duration = Duration::from_secs(60);

            loop {
                thread::sleep(sleep_duration);
            }
        }
    };

    // Mainloop - just echo 256 bytes of data at a time (for now)
    loop {

        let mut buf: Vec<u8> = (0..255).collect();

        if let Err(error) = port.read(&mut buf[..]) {
            error!("Error reading from serial port: {}", error);
            continue;
        }

        if let Err(error) = port.write(&buf[..]) {
            error!("Error writing to serial port: {}", error)
        }

    }

}
