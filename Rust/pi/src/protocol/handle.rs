use std::process;
use protocol::Command;

/// A struct that handles serial data
pub struct CommandHandler;

impl CommandHandler {

    /// Handle a command
    pub fn handle(command: Command) {
        match command {
            Command::Shutdown => CommandHandler::shutdown()
        }
    }

    /// Handle a shutdown command
    fn shutdown() {
        info!("Received shutdown command. Shutting down...");

        process::Command::new("sh")
            .arg("-c")
            .args(&["sudo", "halt"]);
    }
}