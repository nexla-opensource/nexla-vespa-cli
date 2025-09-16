# Vespa Nexla Plugin CLI

A cross-platform CLI tool that generates Vespa applications from Nexla Nexsets.

## About Vespa and Nexla Integration

**Vespa** is a powerful, open-source big data serving engine that excels at real-time computation over large datasets. It combines search, recommendation, personalization, and analytics in a single platform, enabling applications to serve results with low latency at massive scale.

**Benefits of using Vespa with Nexla:**
- **Seamless Data Flow**: Nexla provides native Vespa connectors for effortless data retrieval and ingestion to Vespa instances
- **Real-time Analytics**: Process and serve data insights instantly as new data flows through your Nexla pipelines
- **Scalable Search**: Transform your Nexla datasets into powerful, searchable applications with Vespa's advanced query capabilities
- **Unified Platform**: Leverage Nexla's data integration capabilities with Vespa's serving engine for end-to-end data solutions

This plugin bridges the gap between your Nexla data transformations and Vespa deployments, automatically generating production-ready Vespa applications from your Nexsets.

**For comprehensive information about Vespa, visit the official documentation:**
https://docs.vespa.ai/en/getting-started.html

## Quick Start

### Windows
Double-click `vespa-nexla-cli.bat` or run from Command Prompt:
```cmd
vespa-nexla-cli.bat
```

### Linux/macOS
Run from terminal:
```bash
./vespa-nexla-cli.sh
```

## What it does

1. **Auto-installs Python** if not present (with your permission)
2. **Creates a virtual environment** to isolate dependencies
3. **Installs required packages** from requirements.txt
4. **Runs the interactive CLI** where you'll:
   - Provide your Nexla session token
   - Enter your Nexset ID
   - Generate a ready-to-deploy Vespa application

## Requirements

- Internet connection for downloading dependencies
- Administrative privileges (if Python installation is needed)

## Output

The tool generates a complete Vespa application in the `vespa_app/` directory, ready for deployment on your machine.

### Important: services.xml Configuration

The generated `services.xml` file is a **default template** that provides a basic Vespa configuration. You will need to review and customize it according to:

- Your specific use case requirements
- Your Vespa instance settings and topology
- Performance and scaling needs

**Please refer to the official Vespa services.xml documentation for detailed configuration options:**
https://docs.vespa.ai/en/reference/services.html

Common customizations may include:
- Adjusting node configurations and resource allocation
- Configuring content clusters and document processing
- Setting up search chains and ranking profiles
- Modifying container clusters for your application needs

## Troubleshooting

If you encounter issues:
1. Ensure you have internet connectivity
2. On Linux/macOS, you may need to run with `sudo` if Python installation is required
3. Make sure the script is run from the plugin directory containing `main.py`
