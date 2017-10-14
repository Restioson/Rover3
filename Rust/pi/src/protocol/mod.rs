//! A module grouping things to handle the serial data protocol

pub mod parse;
pub mod handle;
pub mod read;
pub use self::parse::*;
pub use self::handle::*;
pub use self::read::*;

/// A struct representing data received from serial
// Data are my favourite star trek character
#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Data {
    // Telemetry data
    latitude: f64,
    longitude: f64,
    altitude: f64,
    course: f32,
    heading: f32,
    speed: f32,

    // Time data
    year: u16,
    month: u8,
    day: u8,
    hour: u8,
    minute: u8,
    second: u8,

    // Environment data
    temperature: f32,
    humidity: f32,

    // 'Physical state' data
    pitch: f32,
    roll: f32,

    /// The distance of the object in front of the Rover
    object_distance_front: u16,

    /// The distance of the object behind the rover
    object_distance_back: f32,
}

#[derive(Debug, PartialEq)]
pub enum Message {
    Data(Data),
    Command(Command),
}

/// An enum representing serial commands
#[derive(Debug, PartialEq, Eq)]
pub enum Command {
    Shutdown,
}
