//! Configuration structs and serialization

use std;
use std::time;
use std::path::Path;
use std::fs::File;
use std::io::Read;
use toml;
use serial::*;

/// A struct representing the configuration for the rover
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct Config {
    /// The logging config
    pub logging: LoggingConfig,

    /// The serial config
    pub serial: SerialConfig,
}

/// A struct representing the logging configuration for the Rover
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct LoggingConfig {
    /// The directory to write log files to
    pub directory: String,

    /// If the first-choice for directory is not available, log to the second
    pub fallback_directory: String,

    /// The log4rs encoder pattern
    pub pattern: String,

    /// The filename for the log -- the iso datetime will be added to the end
    pub filename: String,
}

/// Configuration for the serial port
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct SerialConfig {
    /// The serial port path/name. Can be a path, such as `/dev/tty...` or a name,
    /// such as `COM...`
    pub port: String,

    /// The serial character size
    #[serde(with = "CharSizeDef")]
    pub char_size: CharSize,

    /// The serial parity
    #[serde(with = "ParityDef")]
    pub parity: Parity,

    /// The number of serial stop bits
    #[serde(with = "StopBitsDef")]
    pub stop_bits: StopBits,

    /// The serial flow control style
    #[serde(with = "FlowControlDef")]
    pub flow_control: FlowControl,

    /// The serial baudrate
    #[serde(with = "BaudRateDef")]
    pub baud: BaudRate,

    /// The retry delay for connecting to serial. When failed to connect to
    /// serial, this delay will be waited
    pub retry_delay: time::Duration,

    /// The serial timeout -- after an operation takes longer than the timeout
    /// value it will be terminated
    pub timeout: time::Duration,
}

impl Config {
    /// Searches for the config file in the specified directories, prioritising
    /// the directories nearer to the beginning
    pub fn search_and_parse(
        name: &'static str,
        directories: &[&'static str],
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
                        return toml::from_slice(buf.as_slice()).map_err(ConfigReadError::TomlError);
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
}

/// In the event of an error reading the config file, this will be
/// returned
#[derive(Debug)]
pub enum ConfigReadError {
    TomlError(toml::de::Error),
    IoError(std::io::Error),
    NotFound,
}

impl Default for Config {
    fn default() -> Config {
        Config {
            logging: LoggingConfig {
                directory: "/mnt/missiondata/log/".to_string(),
                fallback_directory: "log/".to_string(),
                pattern: "{d} {h({l})} - {m}{n}".to_string(),
                filename: "rover".to_string(),
            },

            serial: SerialConfig {
                port: "/dev/ttyAMA0".to_string(),
                baud: Baud9600,
                char_size: Bits8,
                parity: ParityNone,
                stop_bits: Stop1,
                flow_control: FlowNone,
                timeout: time::Duration::from_millis(5000),
                retry_delay: time::Duration::from_millis(5000),
            },
        }
    }
}

// Remote serialization defs

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
#[serde(remote = "BaudRate")]
pub enum BaudRateDef {
    #[serde(rename = "110")]
    Baud110,
    #[serde(rename = "300")]
    Baud300,
    #[serde(rename = "600")]
    Baud600,
    #[serde(rename = "1200")]
    Baud1200,
    #[serde(rename = "2400")]
    Baud2400,
    #[serde(rename = "4800")]
    Baud4800,
    #[serde(rename = "9600")]
    Baud9600,
    #[serde(rename = "19200")]
    Baud19200,
    #[serde(rename = "38400")]
    Baud38400,
    #[serde(rename = "57600")]
    Baud57600,
    #[serde(rename = "115200")]
    Baud115200,
    BaudOther(usize),
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
#[serde(remote = "CharSize")]
pub enum CharSizeDef {
    #[serde(rename = "5")]
    Bits5,
    #[serde(rename = "6")]
    Bits6,
    #[serde(rename = "7")]
    Bits7,
    #[serde(rename = "8")]
    Bits8,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
#[serde(remote = "Parity")]
pub enum ParityDef {
    #[serde(rename = "none")]
    ParityNone,
    #[serde(rename = "odd")]
    ParityOdd,
    #[serde(rename = "even")]
    ParityEven,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
#[serde(remote = "StopBits")]
pub enum StopBitsDef {
    #[serde(rename = "1")]
    Stop1,
    #[serde(rename = "2")]
    Stop2,
}

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
#[serde(remote = "FlowControl")]
pub enum FlowControlDef {
    #[serde(rename = "none")]
    FlowNone,
    #[serde(rename = "software")]
    FlowSoftware,
    #[serde(rename = "hardware")]
    FlowHardware,
}

#[cfg(test)]
mod test {

    use super::*;

    #[test]
    // Check that the correct names have been set, etc
    fn deserialization_correct() {

        let config_toml = r#"
            [logging]
            directory = "/mnt/missiondata/log/"
            fallback_directory = "log/"
            pattern = "{d} {h({l})} - {m}{n}"
            filename = "rover"

            [serial]
            port = "/dev/ttyAMA0"
            char_size = "8"
            parity = "none"
            stop_bits = "1"
            flow_control = "none"
            baud = "9600"

            [serial.retry_delay]
            secs = 5
            nanos = 0

            [serial.timeout]
            secs = 5
            nanos = 0
        "#;

        let config_struct = Config {
            logging: LoggingConfig {
                directory: "/mnt/missiondata/log/".to_string(),
                fallback_directory: "log/".to_string(),
                pattern: "{d} {h({l})} - {m}{n}".to_string(),
                filename: "rover".to_string(),
            },

            serial: SerialConfig {
                port: "/dev/ttyAMA0".to_string(),
                baud: Baud9600,
                char_size: Bits8,
                parity: ParityNone,
                stop_bits: Stop1,
                flow_control: FlowNone,
                timeout: time::Duration::from_millis(5000),
                retry_delay: time::Duration::from_millis(5000),
            },
        };

        assert_eq!(
            toml::from_str::<Config>(config_toml).unwrap(),
            config_struct
        );
    }
}
