use pyo3::prelude::*;
#[cfg(feature = "telemetry")]
use opentelemetry::global;
#[cfg(feature = "telemetry")]
use opentelemetry_sdk::propagation::TraceContextPropagator;

#[cfg(feature = "telemetry")]
use opentelemetry_otlp::WithExportConfig;
#[cfg(feature = "telemetry")]
use once_cell::sync::Lazy;
#[cfg(feature = "telemetry")]
use tokio::runtime::Runtime;
#[cfg(feature = "telemetry")]
use opentelemetry_sdk::trace::{TracerProvider, Config};
// trait import removed

#[cfg(feature = "telemetry")]
use std::collections::HashMap;
#[cfg(feature = "telemetry")]
use tonic::metadata::{MetadataMap, MetadataValue};

// Global runtime for background telemetry tasks (Only used if telemetry enabled)
#[cfg(feature = "telemetry")]
static RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    Runtime::new().expect("Failed to create Tokio runtime for telemetry")
});

#[pyfunction]
#[pyo3(signature = (endpoint=None, headers=None, console=false))]
pub fn init_telemetry(endpoint: Option<String>, headers: Option<HashMap<String, String>>, console: bool) {
    #[cfg(feature = "telemetry")]
    {
        // Set global propagator
        global::set_text_map_propagator(TraceContextPropagator::new());
    
        // Enter runtime for async OTLP tasks
        let _guard = RUNTIME.enter();
    
        let mut provider_builder = TracerProvider::builder()
            .with_config(Config::default());
    
        // 1. Add Console Exporter (if requested)
        if console {
            let console_exporter = opentelemetry_stdout::SpanExporter::default();
            // Use SimpleSpanProcessor for stdout (immediate printing)
            provider_builder = provider_builder
                .with_simple_exporter(console_exporter);
        }
    
        // 2. Add OTLP Exporter (always trying to add it unless we want strict opt-in?)
        let should_add_otlp = endpoint.is_some() || !console;
    
        if should_add_otlp {
             // Construct the Exporter manually.
             let mut exporter_builder = opentelemetry_otlp::new_exporter()
                .tonic();
            
            if let Some(url) = endpoint {
                exporter_builder = exporter_builder.with_endpoint(url);
            }

            if let Some(hdrs) = headers {
                let mut map = MetadataMap::with_capacity(hdrs.len());
                for (k, v) in hdrs {
                    if let (Ok(key), Ok(val)) = (tonic::metadata::MetadataKey::from_bytes(k.as_bytes()), v.parse::<MetadataValue<tonic::metadata::Ascii>>()) {
                         map.insert(key, val);
                    } else {
                        eprintln!("Invalid header: {}={}", k, v);
                    }
                }
                exporter_builder = exporter_builder.with_metadata(map);
            }

             let otlp_exporter_result = exporter_builder.build_span_exporter();
    
            if let Ok(exporter) = otlp_exporter_result {
                let batch_processor = opentelemetry_sdk::trace::BatchSpanProcessor::builder(
                    exporter, 
                    opentelemetry_sdk::runtime::Tokio
                ).build();
                
                provider_builder = provider_builder.with_span_processor(batch_processor);
            } else {
                // Log error to console?
                eprintln!("Failed to initialize OTLP exporter");
            }
        }
    
        let provider = provider_builder.build();
        global::set_tracer_provider(provider);
    }

    #[cfg(not(feature = "telemetry"))]
    {
        // No-op: Telemetry feature disabled
        let _ = endpoint;
        let _ = headers;
        let _ = console;
    }
}

#[pyfunction]
pub fn shutdown_telemetry() {
    #[cfg(feature = "telemetry")]
    global::shutdown_tracer_provider();
}
