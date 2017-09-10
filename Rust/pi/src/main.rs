//! A Rust port of the Pi side of the Rover project, aimed to be safe and performant
//!
//! # Goals
//!
//! ## Safety
//!
//! Hopefully, this port will make the Rover more stable and less prone to errors or issues
//! at runtime
//!
//! ## Performance
//!
//! Python is simply not fast enough to be run with high performance on a processor as limited
//! as the Pi has -- performance is a priority, and this port should help achieve it
//!
//! ## Image Recognition
//!
//! Image recognition could be a seriously cool feature to implement, perhaps using cv-rs

#[macro_use]
extern crate log;
extern crate log4rs;
extern crate serial;
extern crate serde;
extern crate toml;
#[macro_use]
extern crate serde_derive;

mod config;

use std::thread;
use serial::prelude::*;
use serial::PortSettings;
use config::Config;

fn main() {

    info!("Rover3 Pi started!");

    let config = match Config::search_and_parse(
        "rover.toml",
        &[
        "/etc/rover/",
        "~/.config/rover/",
        "~/.rover",
        "" // Current working directory
    ],
    ) {
        Ok(config) => config,
        Err(error) => {
            error!(
                "Error loading config file: \"{:?}\". Falling back to default config",
                error
            );
            Config::default()
        }
    };

    let mut port = &mut *match setup_serial_port(&config) {
        Ok(port) => port,
        Err(error) => {
            warn!(
                "Error opening serial port: \"{}\" -- is the baudrate unsupported?",
                error
            );
            warn!("Operating in limited mode; serial not available");

            loop {}
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

/// Set up the serial port
fn setup_serial_port(config: &Config) -> Result<Box<SerialPort>, serial::Error> {

    loop {
        let mut port: Box<SerialPort> = loop {
            match serial::open(&config.serial.port) {
                Ok(port) => break Box::new(port),
                Err(error) => {
                    warn!(
                        "Couldn't acquire serial port: \"{}\" -- Trying again in 5 seconds",
                        error
                    );
                    thread::sleep(config.serial.retry_delay);
                }
            }
        };

        port.set_timeout(config.serial.timeout)?;

        port.configure(&PortSettings {
            baud_rate: config.serial.baud,
            char_size: config.serial.char_size,
            parity: config.serial.parity,
            stop_bits: config.serial.stop_bits,
            flow_control: config.serial.flow_control,
        })?;

        break Ok(port);
    }

}

#[cfg(test)]
mod test {

    use super::*;
    use serial::ErrorKind::NoDevice;

    // Dummy port for serial test - should point to virtual serial port for mocking
    #[cfg(target_os = "windows")]
    const PORT: &'static str = "CNCA0"; // For mocking, one option is com0com

    #[cfg(not(target_os = "windows"))]
    const PORT: &'static str = "/dev/ptyS10"; // For mocking, one option is socat

    // Check that setup_serial_port actually uses the config it is passed
    // This whole test is something of a sanity check
    #[test]
    fn setup_serial_port_obeys_config() {

        let mut config = Config::default();
        config.serial.port = self::PORT.to_string();

        // Sanity check: check port is not open and exists

        match serial::open(&config.serial.port) {
            Ok(port) => drop(port),
            Err(error) => panic!(format!("Sanity check failed: \"{}\"", error))
        }

        let mut port = setup_serial_port(&config).unwrap();

        // Assertion will fail if device not in use
        // Device being in use shows us that the method has opened the right device
        if let Err(error) = serial::open(&config.serial.port) {
            assert_eq!(error.kind(), NoDevice);
        }

        assert!(port.timeout() == config.serial.timeout);

        port.reconfigure(&|settings| {
            assert_eq!(settings.baud_rate().unwrap(), config.serial.baud);
            assert_eq!(settings.char_size().unwrap(), config.serial.char_size);
            assert_eq!(settings.flow_control().unwrap(), config.serial.flow_control);
            assert_eq!(settings.parity().unwrap(), config.serial.parity);
            assert_eq!(settings.stop_bits().unwrap(), config.serial.stop_bits);
            Ok(())
        }).unwrap();

    }

}
