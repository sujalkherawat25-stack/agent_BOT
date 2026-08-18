use keyring::Entry;

#[tauri::command]
fn save_provider_secret(provider: String, secret: String) -> Result<(), String> {
    if provider.trim().is_empty() || secret.trim().is_empty() {
        return Err("Provider and API key are required.".into());
    }
    let entry = Entry::new("Memento Personal Agent", &format!("provider-api-key:{provider}"))
        .map_err(|error| error.to_string())?;
    entry.set_password(&secret).map_err(|error| error.to_string())
}

#[tauri::command]
fn provider_secret_configured(provider: String) -> Result<bool, String> {
    let entry = Entry::new("Memento Personal Agent", &format!("provider-api-key:{provider}"))
        .map_err(|error| error.to_string())?;
    match entry.get_password() {
        Ok(_) => Ok(true),
        Err(keyring::Error::NoEntry) => Ok(false),
        Err(error) => Err(error.to_string()),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![save_provider_secret, provider_secret_configured])
        .run(tauri::generate_context!())
        .expect("error while running Memento desktop")
}
