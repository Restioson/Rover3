//! Configuration structs and serialization

use std;
use std::time;
use log::LogLevel;
use serial::*;

pub const SERIAL_DATA_LABELS: &[&'static str] = &[
    "latitude",
    "longitude",
    "altitude",
    "course",
    "heading",
    "speed",
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "temperature",
    "humidity",
    "pitch",
    "roll",
    "object_distance_front",
    "object_distance_back",
];
pub const SERIAL_SEPARATOR: char = ' ';
pub const SERIAL_TERMINATOR: char = '\n';

/// A struct representing the configuration for the rover
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, Clone)]
pub struct Config {
    /// The logging config
    pub logging: LoggingConfig,

    /// The data recording config
    pub records: DataRecordingConfig,

    /// The serial config
    pub serial: SerialConfig,
}

/// A struct representing the logging configuration for the Rover
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, Clone)]
pub struct LoggingConfig {
    /// The directory to write log files to
    pub directory: String,

    /// If the first-choice for directory is not available, log to the second
    pub fallback_directory: String,

    /// The log4rs encoder pattern
    pub pattern: String,

    /// The filename for the log -- the iso datetime will be added to the end
    pub filename: String,

    /// The log level
    #[serde(with = "LogLevelDef")]
    pub level: LogLevel,
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, Clone)]
pub struct DataRecordingConfig {
    /// The directory to write data records to
    pub directory: String,

    /// If the first-choice for directory is not available, record to the second
    pub fallback_directory: String,

    /// The data recording filename -- the iso datetime will be added to the end
    pub filename: String,

    /// The output csv separator
    pub separator: char,

    /// The output csv terminator
    pub terminator: char,
}
/// Configuration for the serial port
#[derive(Serialize, Deserialize, Debug, PartialEq, Eq, Clone)]
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

impl Default for Config {
    fn default() -> Config {
        Config {
            logging: LoggingConfig {
                directory: "/mnt/missiondata/log/".to_string(),
                fallback_directory: "log/".to_string(),
                pattern: "{d} {h({l})} - {m}{n}".to_string(),
                filename: "rover".to_string(),
                level: LogLevel::Debug,
            },

            records: DataRecordingConfig {
                directory: "/mnt/missiondata/data/".to_string(),
                fallback_directory: "data/".to_string(),
                filename: "data".to_string(),
                separator: ';',
                terminator: '\n',
            },

            serial: SerialConfig {
                port: "/dev/ttyAMA0".to_string(),
                baud: Baud57600,
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

impl Config {
    /// Validates a config
    pub fn validate(config: &Config) -> std::result::Result<(), ValidationError> {

        // Check that the logging directory is not the same as the fallback
        if config.logging.directory == config.logging.fallback_directory {
            return Err(ValidationError::LoggingDirectoryIsFallback);
        }

        Ok(())
    }
}

/// Returned from `validate` if the config is invalid
#[derive(Debug)]
pub enum ValidationError {
    LoggingDirectoryIsFallback,
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
pub enum LogLevelDef {
    #[serde(rename = "error")]
    Error = 1,
    #[serde(rename = "warn")]
    Warn,
    #[serde(rename = "info")]
    Info,
    #[serde(rename = "debug")]
    Debug,
    #[serde(rename = "trace")]
    Trace,
}

#[cfg(test)]
mod test {

    use super::*;
    use toml;

    #[test]
    // Check that the correct names have been set, etc
    fn deserialization_correct() {

        let config_toml = r#"
            [logging]
            directory = "/mnt/missiondata/log/"
            fallback_directory = "log/"
            pattern = "{d} {h({l})} - {m}{n}"
            filename = "rover"
            level = "debug"

            [records]
            directory = "/mnt/missiondata/data/"
            fallback_directory = "data/"
            filename = "data"
            separator = ';'
            terminator = "\n"

            [serial]
            port = "/dev/ttyAMA0"
            char_size = "8"
            parity = "none"
            stop_bits = "1"
            flow_control = "none"
            baud = "57600"

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
                level: LogLevel::Debug,
            },

            records: DataRecordingConfig {
                directory: "/mnt/missiondata/data/".to_string(),
                fallback_directory: "data/".to_string(),
                filename: "data".to_string(),
                separator: ';',
                terminator: '\n',
            },

            serial: SerialConfig {
                port: "/dev/ttyAMA0".to_string(),
                baud: Baud57600,
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


    #[test]
    fn serial_terminator_is_not_separator() {
        assert_ne!(SERIAL_SEPARATOR, SERIAL_TERMINATOR);
    }

    #[test]
    fn serial_data_labels_have_no_duplicates() {
        let mut deduped = SERIAL_DATA_LABELS.to_vec();
        deduped.sort();
        deduped.dedup();

        let mut sorted = SERIAL_DATA_LABELS.to_vec();
        sorted.sort();

        assert_eq!(sorted, deduped);
    }
}
