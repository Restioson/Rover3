//! A module for various setup functions

use std;
use std::path::Path;
use std::fs::File;
use std::io::Read;
use std::thread;
use serial;
use serial::prelude::*;
use serial::PortSettings;
use chrono::Local;
use log::LogLevel;
use log::LogLevelFilter;
use log4rs;
use log4rs::config::{Appender, Root};
use log4rs::append::console::ConsoleAppender;
use log4rs::encode::pattern::PatternEncoder;
use log4rs::append::file::FileAppender;
use toml;
use config;
use config::Config;
use config::LoggingConfig;
use config::SerialConfig;

/// The filename of the config
const CONFIG_FILENAME: &'static str = "rover.toml";

/// The directories to search for the config
const CONFIG_DIRECTORIES: &[&'static str] = &[
    "/etc/rover/",
    "~/.config/rover/",
    "~/.rover",
    "" // Current working directory
];

/// Sets up config
pub fn config() -> Config {
    match find_and_parse_config(CONFIG_FILENAME, CONFIG_DIRECTORIES) {
        Ok(config) => config,
        Err(error) => {
            eprintln!("Error parsing config: \"{:?}\"", error);
            eprintln!("Using default config");
            Config::default()
        }
    }
}

/// Searches for the config file in the specified directories, prioritising
/// the directories nearer to the beginning
fn find_and_parse_config(
    name: &str,
    directories: &[&str],
) -> std::result::Result<Config, ConfigReadError> {

    // Search every directory in the directories slice...
    println!("Searching for configuration file named \"{}\"", name);
    for directory in directories.iter() {

        // Join the directory and the config file name
        let path = Path::new(directory).join(name);
        println!("Searching \"{}\"", directory);

        if path.exists() {
            println!("Found \"{}\" in \"{}\"", name, directory);

            // Open the file, and attempt to read and deserialize it
            match File::open(&path) {
                Ok(mut file) => {

                    // Attempt to read the file
                    println!("Reading file...");
                    let mut buf = Vec::new();

                    if let Err(error) = file.read_to_end(&mut buf) {
                        return Err(ConfigReadError::IoError(error));
                    }

                    // Attempt to deserialise the file
                    println!("Deserializing...");

                    let conf = toml::from_slice(buf.as_slice()).map_err(
                        ConfigReadError::TomlError,
                    )?;
                    config::Config::validate(&conf).map_err(
                        ConfigReadError::ValidationError,
                    )?;

                    return Ok(conf);
                }

                // In the event of an error reading the file, skip it
                Err(error) => {
                    println!(
                        "Error reading config file \"{}\": \"{}\"",
                        path.to_string_lossy(),
                        error
                    );
                    println!("Skipping...");
                }
            }
        } else {
            println!("\"{}\" not found in \"{}\"", name, directory);
        }
    }

    println!("Config file not found!");
    Err(ConfigReadError::NotFound)
}

/// In the event of an error in `find_and_parse_config`, this will be returned
#[derive(Debug)]
pub enum ConfigReadError {
    TomlError(toml::de::Error),
    IoError(std::io::Error),
    ValidationError(config::ValidationError),
    NotFound,
}


// TODO test
/// Sets up logging with log4rs
///
/// Programatically creates a logging config and sets values according to config.
/// If the first choice for logging directory (`directory` key in config) is not
/// available, it will fallback to the fallback directory (`fallback_directory`).
/// If neither of these are available, or there is an error setting up the file
/// appender, then it will only use stdout
///
/// # Panicking
///
/// Panics:
///     - if there is an error building the config (the config is invalid)
///     - if there is an error setting the logger (the logger is already set)
pub fn logging(config: &LoggingConfig) {

    // Build the standard output appender
    let stdout = ConsoleAppender::builder()
        .encoder(Box::new(PatternEncoder::new(config.pattern.as_str())))
        .build();

    // If the first choice for the log file is not available, use the fallback
    let first_choice = Path::new(&config.directory);

    let path = if first_choice.exists() {
        first_choice.join(&config.filename)
    } else {
        println!("Using fallback directory");
        Path::new(&config.fallback_directory).join(&config.filename)
    };

    // Build the file appender
    let file_result = FileAppender::builder()
        .encoder(Box::new(PatternEncoder::new(config.pattern.as_str())))
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
            logger_config_builder.appender(Appender::builder().build("file", Box::new(appender)));
        root = root.appender("file")
    } else {
        println!("File not available, writing to stdout only");
    }

    // Map log level to LogLevelFilter

    let level = match config.level {
        LogLevel::Error => LogLevelFilter::Error,
        LogLevel::Warn => LogLevelFilter::Warn,
        LogLevel::Info => LogLevelFilter::Info,
        LogLevel::Debug => LogLevelFilter::Debug,
        LogLevel::Trace => LogLevelFilter::Trace,
    };

    // Finish building the logger config
    let logger_config = logger_config_builder.build(root.build(level)).expect(
        "Error building config -- this is a bug! Is the config invalid?",
    );

    // Initialise logging
    log4rs::init_config(logger_config).expect(
        "Error setting logger -- this is a bug! Has the logger already been set?",
    );
}

/// Set up the serial port
///
/// Retries until the port is available. If configuring fails, then it will
/// return an error result
pub fn serial_port(config: &SerialConfig) -> Result<Box<SerialPort>, serial::Error> {

    // Retry until serial port available
    let mut port: Box<SerialPort> = loop {
        match serial::open(&config.port) {
            Ok(port) => break Box::new(port),
            Err(error) => {
                warn!(
                    "Couldn't acquire serial port: \"{}\" -- Trying again in 5 seconds",
                    error
                );
                thread::sleep(config.retry_delay);
            }
        }
    };

    // Configure port

    port.set_timeout(config.timeout)?;

    port.configure(&PortSettings {
        baud_rate: config.baud,
        char_size: config.char_size,
        parity: config.parity,
        stop_bits: config.stop_bits,
        flow_control: config.flow_control,
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

    #[cfg(unix)]
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

        let mut port = serial_port(&config.serial).unwrap();

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
