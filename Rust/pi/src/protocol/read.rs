use std;
use std::io::BufRead;
use protocol::{Parser, Message, ParseError};
use config;

/// A struct to read and parse data from serial
pub struct Reader<W: BufRead> {
    parser: Parser,
    inner: W,
    buf: Vec<u8>, // Buf kept to avoid needless allocations
}

impl<W: BufRead> Reader<W> {
    pub fn new(serial_port: W) -> Self {
        Reader {
            parser: Parser::new(),
            inner: serial_port,
            buf: Vec::new(),
        }
    }

    pub fn read(&mut self) -> Result<Message, ReadError> {

        self.buf.clear();

        debug!("Reading from serial port...");

        if let Err(error) = self.inner.read_until(
            config::SERIAL_TERMINATOR as u8,
            &mut self.buf,
        )
        {
            error!("Error reading from serial port: {}", error);
            return Err(ReadError::SerialReadError(error));
        }

        trace!("Parsing data as a utf8 string...");

        let data =
            handle_err![(std::str::from_utf8(self.buf.as_slice())) with err => {
                error!("Error parsing packet as a utf-8 string: {:?}", err);
                return Err(ReadError::UtfParseError(err));
        }];

        debug!("Parsing serial packet...");

        let message_option =
            handle_err![(self.parser.parse(data)) with err => {
                error!("Error parsing serial packet: {:?}", err);
                return Err(ReadError::ParseError(err));
        }];

        trace!("Checking for data from parse...");

        let message =
            handle_option![message_option => {
                error!("Reached EOF -- not enough data? Was the data malformed?");
                return Err(ReadError::EofError);
        }];

        trace!("Read done!");

        Ok(message)
    }

    pub fn get_mut(&mut self) -> &mut W {
        &mut self.inner
    }
}

/// Enum representing error reading data from serial
#[derive(Debug)]
pub enum ReadError {
    SerialReadError(std::io::Error),
    UtfParseError(std::str::Utf8Error),
    ParseError(ParseError),
    EofError,
}
