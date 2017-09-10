//! Configuration structs and serialization

use std;
use std::time;
use std::path::Path;
use std::fs::File;
use std::io::Read;
use toml;
use serial::*;
use log::LogLevel;

/// A struct representing the configuration for the rover
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct Config {
    pub logging: LoggingConfig,
    pub serial: SerialConfig,
}

/// A struct representing the logging configuration for the Rover
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct LoggingConfig {
    /// The path to the log4rs configuration file
    pub config_path: String,

    /// The maximum log level
    #[serde(with = "LogLevelDef")]
    pub level: LogLevel, // TODO
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Eq)]
pub struct SerialConfig {
    /// The serial port path/name. Can be a path, such as `/dev/tty...` or a name, such as `COM...`
    pub port: String,

    #[serde(with = "CharSizeDef")]
    pub char_size: CharSize,
    #[serde(with = "ParityDef")]
    pub parity: Parity,
    #[serde(with = "StopBitsDef")]
    pub stop_bits: StopBits,
    #[serde(with = "FlowControlDef")]
    pub flow_control: FlowControl,
    #[serde(with = "BaudRateDef")]
    pub baud: BaudRate,

    /// The retry delay for connecting to serial. When failed to connect to serial, this delay will
    /// be waited
    pub retry_delay: time::Duration,
    pub timeout: time::Duration,
}

impl Config {
    /// Searches for the config file in the specified directories, prioritising the directories
    /// nearer to the beginning
    pub fn search_and_parse(
        name: &'static str,
        directories: &[&'static str],
    ) -> std::result::Result<Config, ConfigReadError> {

        info!("Searching for configuration file named \"{}\"", name);
        for directory in directories.iter() {

            let path = Path::new(directory).join(name);
            debug!("Searching \"{}\"", directory);

            if path.exists() {
                info!("Found \"{}\" in \"{}\"", name, directory);

                match File::open(&path) {
                    Ok(mut file) => {
                        debug!("Reading file...");
                        let mut buf = Vec::new();

                        if let Err(error) = file.read_to_end(&mut buf) {
                            return Err(ConfigReadError::IoError(error));
                        }

                        debug!("Deserializing...");
                        return match toml::from_slice(buf.as_slice()) {
                            Ok(config) => Ok(config),
                            Err(error) => Err(ConfigReadError::TomlError(error)),
                        };
                    }

                    Err(error) => {
                        warn!(
                            "Error reading config file \"{}\": \"{}\"",
                            path.to_string_lossy(),
                            error
                        );
                        warn!("Skipping...");
                    }
                }
            } else {
                debug!("\"{}\" not found in \"{}\"", name, directory);
            }
        }

        warn!("Config file not found!");
        Err(ConfigReadError::NotFound)
    }
}

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
                config_path: "log4rs.yml".to_string(),
                level: LogLevel::Info,
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

#[allow(dead_code)]
#[derive(Serialize, Deserialize)]
#[serde(remote = "LogLevel")]
#[serde(rename_all = "snake_case")]
pub enum LogLevelDef {
    Error = 1,
    Warn,
    Info,
    Debug,
    Trace,
}

#[cfg(test)]
mod test {

    use super::*;

    #[test]
    // Check that the correct names have been set, etc
    fn deserialization_correct() {

        let config_toml = r#"
            [logging]
            config_path = "log4rs.yml"
            level = "info"

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
                config_path: "log4rs.yml".to_string(),
                level: LogLevel::Info,
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
