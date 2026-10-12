use anyhow::{Context, Result, bail};
use rmcp::{ServiceExt, tool, tool_router, transport::stdio};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{collections::HashSet, env, path::Path};

const CATALOG_JSON: &str = include_str!("../../../tools/catalog.json");
const SUPPORTED_SURFACES: [&str; 3] = ["tools", "labs", "core"];

#[derive(Debug, Clone, Deserialize, Serialize)]
struct Catalog {
    schema_version: u32,
    policy: CatalogPolicy,
    tools: Vec<ToolSpec>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct CatalogPolicy {
    resident_core: String,
    external_tooling: String,
    python_boundary: String,
    implementation_rule: String,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct ToolSpec {
    id: String,
    surface: String,
    category: String,
    kind: String,
    role: String,
    adapter_status: String,
    #[serde(default)]
    probe_binary: Option<String>,
    notes: String,
}

fn validate_catalog(catalog: &Catalog) -> Result<()> {
    if catalog.schema_version != 2 {
        bail!(
            "unsupported tools/catalog.json schema_version: {}",
            catalog.schema_version
        );
    }

    let mut ids = HashSet::new();
    for tool in &catalog.tools {
        if !SUPPORTED_SURFACES.contains(&tool.surface.as_str()) {
            bail!(
                "tool '{}' has unsupported surface '{}'; expected one of {:?}",
                tool.id,
                tool.surface,
                SUPPORTED_SURFACES
            );
        }

        if !ids.insert(tool.id.as_str()) {
            bail!("duplicate tool id in catalog: '{}'", tool.id);
        }
    }

    Ok(())
}

fn load_catalog() -> Result<Catalog> {
    let catalog: Catalog =
        serde_json::from_str(CATALOG_JSON).context("invalid tools/catalog.json")?;
    validate_catalog(&catalog)?;
    Ok(catalog)
}

fn binary_on_path(binary: &str) -> bool {
    let candidate = Path::new(binary);
    if candidate.components().count() > 1 {
        return candidate.is_file();
    }

    env::var_os("PATH")
        .map(|path| {
            env::split_paths(&path)
                .map(|directory| directory.join(binary))
                .any(|path| path.is_file())
        })
        .unwrap_or(false)
}

fn doctor_report(catalog: &Catalog) -> Value {
    let tools: Vec<Value> = catalog
        .tools
        .iter()
        .map(|tool| {
            let available = tool.probe_binary.as_deref().map(binary_on_path);

            json!({
                "id": tool.id,
                "surface": tool.surface,
                "category": tool.category,
                "kind": tool.kind,
                "adapter_status": tool.adapter_status,
                "probe_binary": tool.probe_binary,
                "available": available,
            })
        })
        .collect();

    json!({
        "schema_version": catalog.schema_version,
        "resident_core": catalog.policy.resident_core,
        "implementation_rule": catalog.policy.implementation_rule,
        "tools": tools,
    })
}

#[derive(Clone, Default)]
struct NinjaTooling;

#[tool_router(server_handler)]
impl NinjaTooling {
    #[tool(
        description = "Return the canonical Ninja external capability and instrument catalog, classified by Tools, Labs or core surface. Use this before assuming a crawler, browser, archive, data, scientific, optimization or backtesting capability is part of the project."
    )]
    fn ninja_tool_catalog(&self) -> String {
        CATALOG_JSON.to_owned()
    }

    #[tool(
        description = "Inspect the local environment and report which catalogued CLI binaries are currently discoverable on PATH, including their Ninja surface classification. A missing binary means unavailable, not permission to install it silently."
    )]
    fn ninja_tool_doctor(&self) -> String {
        match load_catalog() {
            Ok(catalog) => serde_json::to_string_pretty(&doctor_report(&catalog))
                .unwrap_or_else(|error| json!({ "error": error.to_string() }).to_string()),
            Err(error) => json!({ "error": error.to_string() }).to_string(),
        }
    }
}

fn print_help() {
    eprintln!(
        "ninja-tooling\n\nUSAGE:\n  ninja-tooling catalog   Print the canonical capability/instrument catalog\n  ninja-tooling doctor    Probe locally discoverable CLI tools\n  ninja-tooling mcp       Serve catalog + diagnostics over MCP stdio\n"
    );
}

#[tokio::main]
async fn main() -> Result<()> {
    match env::args().nth(1).as_deref() {
        Some("catalog") => println!("{CATALOG_JSON}"),
        Some("doctor") => {
            let catalog = load_catalog()?;
            println!(
                "{}",
                serde_json::to_string_pretty(&doctor_report(&catalog))?
            );
        }
        Some("mcp") => {
            let service = NinjaTooling.serve(stdio()).await?;
            service.waiting().await?;
        }
        Some("help") | Some("--help") | Some("-h") | None => print_help(),
        Some(other) => {
            print_help();
            bail!("unknown subcommand: {other}");
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn embedded_catalog_is_valid() {
        let catalog = load_catalog().expect("embedded catalog must validate");
        assert!(!catalog.tools.is_empty());
    }

    #[test]
    fn catalog_has_all_three_surfaces() {
        let catalog = load_catalog().expect("embedded catalog must validate");
        let surfaces: HashSet<&str> = catalog
            .tools
            .iter()
            .map(|tool| tool.surface.as_str())
            .collect();

        for expected in SUPPORTED_SURFACES {
            assert!(surfaces.contains(expected), "missing surface: {expected}");
        }
    }
}
