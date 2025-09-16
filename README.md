# Vespa Nexla Plugin CLI

A cross-platform CLI tool that generates Vespa applications from Nexla Nexsets.

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

## Troubleshooting

If you encounter issues:
1. Ensure you have internet connectivity
2. On Linux/macOS, you may need to run with `sudo` if Python installation is required
3. Make sure the script is run from the plugin directory containing `main.py`