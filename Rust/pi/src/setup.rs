//! A module for various setup functions

use std::thread;
use std::path::Path;
use serial;
use serial::prelude::*;
use serial::PortSettings;
use chrono::Local;
use log4rs;
use log4rs::append::console::ConsoleAppender;
use log4rs::encode::pattern::PatternEncoder;
use log4rs::append::file::FileAppender;
use log4rs::config::Appender;
use log4rs::config::Root;
use log::LogLevelFilter;
use config::Config;

// TODO test
/// Sets up logging
///
/// Programatically creates a logging config and sets values according to config.
/// If the first choice for logging directory (`directory` key in config) is not
/// available, it will fallback to the fallback directory (`fallback_directory`).
/// If neither of these are available, or there is an error setting up the file
/// appender, then it will only use stdout
///
/// # Panicking
///
/// Panicks if there is an error setting up the logger (`logger_config.build`),
/// or setting the logger (`init`)
// TODO don't panic!
pub fn logging(config: &Config) {

    // Build the standard output appender
    let stdout = ConsoleAppender::builder()
        .encoder(Box::new(
            PatternEncoder::new(config.logging.pattern.as_str()),
        ))
        .build();

    // If the first choice for the log file is not available, use the fallback
    let first_choice = Path::new(&config.logging.directory);

    let path = if first_choice.exists() {
        first_choice.join(&config.logging.filename)
    } else {
        println!("Using fallback directory");
        Path::new(&config.logging.fallback_directory).join(&config.logging.filename)
    };

    // Build the file appender
    let file_result = FileAppender::builder()
        .encoder(Box::new(
            PatternEncoder::new(config.logging.pattern.as_str()),
        ))
        .build(
            format!(
                "{}{}.log",
                path.to_string_lossy(),
                Local::now().to_string().replace(":", "-")
            ).as_str(),
        );

    // The main config builder
    let mut logger_config_builder = log4rs::config::Config::builder().appender(
        Appender::builder().build(
            "stdout",
            Box::new(stdout),
        ),
    );

    // The root builder
    let mut root = Root::builder();

    // Add the stdout appender
    root = root.appender("stdout");

    // Only add the file appender if it was set up correctly
    if let Ok(appender) = file_result {
        logger_config_builder =
            logger_config_builder.appender(Appender::builder().build("stdout", Box::new(appender)));
        root = root.appender("file")
    } else {
        println!("File not available, writing to stdout only");
    }

    // Finish building the logger config
    let logger_config = logger_config_builder
        .build(root.build(LogLevelFilter::Debug))
        .expect("Error setting up logger (logger_config.build)!");

    // Initialise logging
    log4rs::init_config(logger_config).expect("Error setting up logger (init_config)!");

}

/// Set up the serial port
///
/// Retries until the port is available. If configuring fails, then it will
/// return an error result
pub fn serial_port(config: &Config) -> Result<Box<SerialPort>, serial::Error> {

    // Retry until serial port available
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

    // Configure port

    port.set_timeout(config.serial.timeout)?;

    port.configure(&PortSettings {
        baud_rate: config.serial.baud,
        char_size: config.serial.char_size,
        parity: config.serial.parity,
        stop_bits: config.serial.stop_bits,
        flow_control: config.serial.flow_control,
    })?;

    Ok(port)

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

    // Check that serial_port actually uses the config it is passed
    // This whole test is something of a sanity check
    #[test]
    fn serial_port_obeys_config() {

        let mut config = Config::default();
        config.serial.port = self::PORT.to_string();

        // Sanity check: check port is not open and exists

        match serial::open(&config.serial.port) {
            Ok(port) => drop(port),
            Err(error) => panic!(format!("Sanity check failed: \"{}\"", error)),
        }

        let mut port = serial_port(&config).unwrap();

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
