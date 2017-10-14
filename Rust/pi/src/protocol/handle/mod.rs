//! A module for grouping things that handle serial data
pub mod command;
pub use self::command::*;

use std::io::Write;
use csv::Writer;
use setup;
use protocol::Message;
use config::DataRecordingConfig;

/// A struct to handle serial data
pub struct SerialHandler {
    data_records: Writer<Box<Write>>,
}

impl SerialHandler {
    pub fn new(config: &DataRecordingConfig) -> Self {
        SerialHandler { data_records: setup::data_recording(config) }
    }

    pub fn handle(&mut self, message: Message) {
        match message {
            Message::Command(command) => command::CommandHandler::handle(command),
            Message::Data(data) => {
                if let Err(error) = self.data_records.serialize(data) {
                    error!(
                        "Error serializing data to write to records: \"{:?}\"",
                        error
                    );
                } else if let Err(error) = self.data_records.flush() {
                    error!("Error flushing csv data record writer: \"{:?}\"", error);
                }
            }
        }
    }
}
