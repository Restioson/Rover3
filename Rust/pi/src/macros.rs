#[macro_export]
macro_rules! handle_err {
    [($value:expr) with $error_name:ident => $handler:block] => {
        match $value {
            Ok(ok_value) => ok_value,
            Err($error_name) => $handler
        }
    };
}

#[macro_export]
macro_rules! handle_option {
    [$value:expr => $handler:block] => {
        match $value {
            Some(some_value) => some_value,
            None => $handler
        }
    }
}
