use anyhow::{Context, Result, bail};
use rmcp::{
    ServiceExt, handler::server::wrapper::Parameters, schemars, tool, tool_router, transport::stdio,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{collections::HashSet, env, path::Path};

const CATALOG_JSON: &str = include_str!("../../../tools/catalog.json");
const SUPPORTED_SURFACES: [&str; 3] = ["tools", "labs", "core"];
const ROUTE_PROFILES: [&str; 10] = [
    "discovery",
    "historical",
    "static-web",
    "high-throughput-web",
    "dynamic-web",
    "authenticated-browser",
    "semantic-browser",
    "protocol-observation",
    "replay-capture",
    "complex-document",
];

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
    #[serde(default)]
    upstream: Option<String>,
    #[serde(default)]
    selection_role: Option<String>,
    #[serde(default)]
    safety_boundary: Option<String>,
    notes: String,
}

#[derive(Debug, Deserialize, schemars::JsonSchema)]
struct AcquisitionRouteRequest {
    #[schemars(
        description = "Deterministic acquisition profile. One of: discovery, historical, static-web, high-throughput-web, dynamic-web, authenticated-browser, semantic-browser, protocol-observation, replay-capture, complex-document."
    )]
    profile: String,
    #[serde(default)]
    #[schemars(
        description = "Add selective replayable preservation (Browsertrix/WARC/WACZ) as a sidecar when the acquired evidence is mutable or high value."
    )]
    preserve: bool,
    #[serde(default)]
    #[schemars(
        description = "Add authorized protocol observation (mitmproxy, optionally mitmproxy2swagger) as a sidecar for interoperability/debugging on traffic the operator is permitted to inspect."
    )]
    inspect_protocol: bool,
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
                "upstream": tool.upstream,
                "selection_role": tool.selection_role,
                "safety_boundary": tool.safety_boundary,
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

fn normalize_profile(profile: &str) -> String {
    profile.trim().to_ascii_lowercase().replace('_', "-")
}

fn push_unique<'a>(items: &mut Vec<&'a str>, value: &'a str) {
    if !items.contains(&value) {
        items.push(value);
    }
}

fn acquisition_route(profile: &str, preserve: bool, inspect_protocol: bool) -> Result<Value> {
    let profile = normalize_profile(profile);

    let (primary, fallbacks): (Vec<&str>, Vec<&str>) = match profile.as_str() {
        "discovery" => (
            vec!["surfsense", "searxng", "last30days"],
            vec!["gdelt", "common-crawl"],
        ),
        "historical" => (
            vec!["common-crawl", "gdelt", "arctic-shift"],
            vec!["surfsense"],
        ),
        "static-web" => (
            vec!["curl-cffi", "crawl4ai", "trafilatura"],
            vec!["crawlee", "scrapy"],
        ),
        "high-throughput-web" => (vec!["crawlee", "scrapy"], vec!["crawl4ai", "curl-cffi"]),
        "dynamic-web" => (
            vec!["crawl4ai", "playwright"],
            vec!["browser-control", "stagehand"],
        ),
        "authenticated-browser" => (
            vec!["browser-control"],
            vec!["playwright", "stagehand", "camoufox", "cloakbrowser"],
        ),
        "semantic-browser" => (vec!["stagehand"], vec!["browser-control", "playwright"]),
        "protocol-observation" => (vec!["mitmproxy"], vec!["mitmproxy2swagger"]),
        "replay-capture" => (vec!["browsertrix-crawler"], vec![]),
        "complex-document" => (vec!["docling"], vec!["trafilatura"]),
        _ => bail!(
            "unknown acquisition profile '{profile}'; expected one of: {}",
            ROUTE_PROFILES.join(", ")
        ),
    };

    let mut sidecars = Vec::new();
    if inspect_protocol && profile != "protocol-observation" {
        push_unique(&mut sidecars, "mitmproxy");
        push_unique(&mut sidecars, "mitmproxy2swagger");
    }
    if preserve && profile != "replay-capture" {
        push_unique(&mut sidecars, "browsertrix-crawler");
    }

    Ok(json!({
        "profile": profile,
        "primary": primary,
        "fallbacks": fallbacks,
        "sidecars": sidecars,
        "policy": {
            "preference": "Use the cheapest structured/reproducible path that preserves the required information, then escalate only when measured acquisition needs justify it.",
            "authorization": "Only public or otherwise authorized targets and sessions are eligible. Authentication, CAPTCHA and anti-abuse challenges are explicit outcomes, not permission to bypass controls.",
            "provenance": "Record tool/version identity, timestamps, target/source identity, challenge/failure state and artifact references for acquired evidence.",
            "separation": "Acquisition produces observations/artifacts. Scientific interpretation remains in Ninja Labs."
        }
    }))
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

    #[tool(
        description = "Return Ninja's deterministic acquisition routing plan for a declared workload profile. This recommends bounded tools and optional preservation/protocol-observation sidecars; it never executes arbitrary shell commands or changes authorization boundaries."
    )]
    fn ninja_tool_route(
        &self,
        Parameters(AcquisitionRouteRequest {
            profile,
            preserve,
            inspect_protocol,
        }): Parameters<AcquisitionRouteRequest>,
    ) -> String {
        match acquisition_route(&profile, preserve, inspect_protocol) {
            Ok(route) => serde_json::to_string_pretty(&route)
                .unwrap_or_else(|error| json!({ "error": error.to_string() }).to_string()),
            Err(error) => json!({ "error": error.to_string() }).to_string(),
        }
    }
}

fn print_help() {
    eprintln!(
        "ninja-tooling\n\nUSAGE:\n  ninja-tooling catalog   Print the canonical capability/instrument catalog\n  ninja-tooling doctor    Probe locally discoverable CLI tools\n  ninja-tooling route <profile> [--preserve] [--inspect-protocol]\n                         Print a deterministic acquisition routing plan\n  ninja-tooling mcp       Serve catalog + diagnostics + routing over MCP stdio\n"
    );
}

fn route_from_cli() -> Result<()> {
    let mut args = env::args().skip(2);
    let profile = args
        .next()
        .context("route requires a profile; run `ninja-tooling help` for supported profiles")?;

    let mut preserve = false;
    let mut inspect_protocol = false;

    for flag in args {
        match flag.as_str() {
            "--preserve" => preserve = true,
            "--inspect-protocol" => inspect_protocol = true,
            other => bail!("unknown route flag '{other}'"),
        }
    }

    println!(
        "{}",
        serde_json::to_string_pretty(&acquisition_route(&profile, preserve, inspect_protocol)?)?
    );
    Ok(())
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
        Some("route") => route_from_cli()?,
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

    #[test]
    fn field_kit_tools_are_catalogued() {
        let catalog = load_catalog().expect("embedded catalog must validate");
        let ids: HashSet<&str> = catalog.tools.iter().map(|tool| tool.id.as_str()).collect();

        for expected in [
            "crawl4ai",
            "browser-control",
            "stagehand",
            "mitmproxy",
            "mitmproxy2swagger",
            "browsertrix-crawler",
        ] {
            assert!(ids.contains(expected), "missing field-kit tool: {expected}");
        }
    }

    #[test]
    fn authenticated_browser_route_prefers_browser_control() {
        let route =
            acquisition_route("authenticated-browser", false, false).expect("route must be valid");
        assert_eq!(route["primary"][0], "browser-control");
    }

    #[test]
    fn route_sidecars_are_explicit_and_additive() {
        let route = acquisition_route("dynamic-web", true, true).expect("route must be valid");
        let sidecars = route["sidecars"]
            .as_array()
            .expect("sidecars must be an array");
        assert!(sidecars.iter().any(|value| value == "mitmproxy"));
        assert!(sidecars.iter().any(|value| value == "mitmproxy2swagger"));
        assert!(sidecars.iter().any(|value| value == "browsertrix-crawler"));
    }

    #[test]
    fn unknown_route_profile_is_rejected() {
        assert!(acquisition_route("unknown", false, false).is_err());
    }
}
