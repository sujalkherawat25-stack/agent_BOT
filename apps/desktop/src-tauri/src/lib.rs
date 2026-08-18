use keyring::Entry;
use std::{path::PathBuf, process::{Child, Command, Stdio}, sync::Mutex};
use tauri::{AppHandle, Manager, State};

struct RuntimeState(Mutex<Option<Child>>);

impl Drop for RuntimeState {
    fn drop(&mut self) {
        if let Ok(mut slot) = self.0.lock() {
            if let Some(mut child) = slot.take() { let _ = child.kill(); }
        }
    }
}

fn agent_command(app: &AppHandle) -> Result<Command, String> {
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let exe_dir = exe.parent().unwrap_or_else(|| std::path::Path::new("."));
    let packaged = [exe_dir.join("agentd.exe"), app.path().resource_dir().unwrap_or_else(|_| exe_dir.to_path_buf()).join("agentd.exe")]
        .into_iter().find(|path| path.exists());
    if let Some(packaged) = packaged {
        let mut command = Command::new(packaged);
        command.env("MEMENTO_PORT", "8765");
        return Ok(command);
    }
    let cwd = std::env::current_dir().map_err(|e| e.to_string())?;
    let script = [cwd.join("apps/agentd/agentd.py"), cwd.join("../agentd/agentd.py"), PathBuf::from("apps/agentd/agentd.py")]
        .into_iter().find(|path| path.exists()).ok_or_else(|| "Local agent runtime was not found. Package agentd.exe next to Memento.exe or run from the repository.".to_string())?;
    let mut command = Command::new("python");
    command.arg(script).env("MEMENTO_PORT", "8765");
    Ok(command)
}

#[tauri::command]
fn start_agent(app: AppHandle, state: State<RuntimeState>) -> Result<String, String> {
    let mut slot = state.0.lock().map_err(|_| "Runtime lock unavailable".to_string())?;
    if let Some(child) = slot.as_mut() {
        if child.try_wait().map_err(|e| e.to_string())?.is_none() { return Ok("http://127.0.0.1:8765".into()); }
    }
    let mut command = agent_command(&app)?;
    let child = command.stdout(Stdio::null()).stderr(Stdio::null()).spawn().map_err(|e| format!("Could not start local agent runtime: {e}"))?;
    *slot = Some(child);
    Ok("http://127.0.0.1:8765".into())
}

#[tauri::command]
fn stop_agent(state: State<RuntimeState>) -> Result<(), String> {
    if let Some(mut child) = state.0.lock().map_err(|_| "Runtime lock unavailable".to_string())?.take() { let _ = child.kill(); }
    Ok(())
}

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
        .manage(RuntimeState(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![save_provider_secret, provider_secret_configured, start_agent, stop_agent])
        .run(tauri::generate_context!())
        .expect("error while running Memento desktop")
}
