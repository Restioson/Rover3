//! A module for serial protocol parsing

use std;
use std::io::Cursor;
use std::io::Write;
use csv;
use config;
use protocol::{Data, Message, Command};

/// Enum representing errors returned from `parse` from `Parser`
#[derive(Debug)]
pub enum ParseError {
    CsvError(csv::Error),
    PacketTooShort,
    NoTag,
    InvalidTag(String),
    InvalidCommand(String),
}

/// Parser for serial protocol packets
///
/// It must be fed with the `feed` method with data from serial
pub struct Parser {
    data_records: csv::DeserializeRecordsIntoIter<Cursor<Vec<u8>>, Data>,
}

impl Parser {
    pub fn new() -> Self {
        let mut reader = csv::ReaderBuilder::new()
            .delimiter(config::SERIAL_SEPARATOR as u8)
            .terminator(csv::Terminator::Any(config::SERIAL_TERMINATOR as u8))
            .from_reader(Cursor::new(Vec::new()));

        let mut headers: String = config::SERIAL_DATA_LABELS
            .iter()
            .map(|it| it.to_string())
            .collect::<Vec<_>>()
            .join(config::SERIAL_SEPARATOR.encode_utf8(&mut [0u8; 2]));
        headers.push(config::SERIAL_TERMINATOR);

        write_csv(&mut reader, headers.as_bytes());

        Parser { data_records: reader.into_deserialize() }
    }

    pub fn parse<'a>(&mut self, packet: &'a str) -> Result<Option<Message>, ParseError> {

        let tag = match packet.split(config::SERIAL_SEPARATOR).next() {
            Some(tag) => tag,
            None => return Err(ParseError::NoTag),
        };

        if packet.len() < tag.len() + 1 {
            return Err(ParseError::PacketTooShort);
        }

        // Remove the tag and delimiter, and trim leading/trailing spaces
        let data = packet[tag.len() + 1..].trim();

        write_csv(self.data_records.reader_mut(), data.as_bytes());

        match tag {
            "DATA" => {
                match self.data_records.next() {
                    Some(Ok(data)) => Ok(Some(Message::Data(data))),
                    Some(Err(error)) => Err(ParseError::CsvError(error)),
                    None => Ok(None),
                }
            }
            "CMD" => {
                match data {
                    "SHUTDOWN" => Ok(Some(Message::Command(Command::Shutdown))),
                    _ => Err(ParseError::InvalidCommand(data.to_string())), // Unknown command
                }
            }
            _ => Err(ParseError::InvalidTag(tag.to_string())), // Unknown tag
        }
    }
}

#[cfg(test)]
mod test {

    use super::*;

    #[test]
    fn parse_parses_correctly() {
        let mut parser = Parser::new();

        // Real world example
        // Latitude/longitude/altitude censored
        let raw = "DATA -100.00 100.00 100.00 77.39 195.9 1.111 ".to_owned() +
            "2017 9 29 13 14 48 0 0 2.1 -1.3 82 67.3\n";

        let expected_data = Data {
            latitude: -100.0,
            longitude: 100.0,
            altitude: 100.0,
            course: 77.39,
            heading: 195.9,
            speed: 1.111,
            year: 2017,
            month: 9,
            day: 29,
            hour: 13,
            minute: 14,
            second: 48,
            temperature: 0.0,
            humidity: 0.0,
            pitch: 2.1,
            roll: -1.3,
            object_distance_front: 82,
            object_distance_back: 67.3,
        };

        let data = parser.parse(&raw).unwrap().unwrap();

        assert_eq!(data, Message::Data(expected_data));
    }
}

// Thanks to daschl & burntsushi
// https://github.com/BurntSushi/rust-csv/issues/91
fn write_csv(reader: &mut csv::Reader<Cursor<Vec<u8>>>, data: &[u8]) {
    let mut position = reader.position().clone();
    position.set_byte(0);

    {
        let cursor = reader.get_mut();

        cursor.set_position(position.byte());
        cursor.get_mut().clear();
        cursor.write_all(data).unwrap();
        cursor.set_position(position.byte());
    }

    reader
        .seek_raw(std::io::SeekFrom::Start(position.byte()), position.clone())
        .unwrap();
}
