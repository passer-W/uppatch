# uppatch (AutoPatcher)

uppatch is an automated tool for patching and repairing dependencies in Maven projects. It scans for dependencies with known vulnerabilities, automatically updates `pom.xml` to safe versions, and uses AI to intelligently fix compilation errors caused by version upgrades.

[中文文档](README_zh.md)

## Core Features

- **Vulnerability Scanning**: Uses the OSV.dev API to scan for known vulnerabilities in Maven dependencies.
- **Automated Upgrades**: Automatically parses and modifies `pom.xml` to upgrade risky dependencies to safe versions.
- **Intelligent Repair**: Automatically runs Maven builds, captures compilation errors, and uses Large Language Models (e.g., DeepSeek) to fix code compatibility issues.
- **Closed-Loop Process**: Scan -> Upgrade -> Build -> Fix -> Rebuild, continuing until the project compiles successfully.

## Requirements

- Python 3.8+
- Maven (must be configured in system PATH)
- Java JDK (version must be compatible with the target project)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd uppatch_proj
   ```

2. Install Python dependencies:
   ```bash
   pip install -r tools/requirements.txt
   ```

## Configuration

The tool uses the DeepSeek API for code repair by default. You can configure the API Key and other options via environment variables.

It is recommended to set the following environment variables before running:

- `LLM_API_KEY`: Your LLM API key (default is a sample DeepSeek key, please replace with your own)
- `LLM_BASE_URL`: LLM API base URL (default is `https://api.deepseek.com`)
- `GITHUB_TOKEN`: (Optional) Token for the GitHub crawler to avoid rate limits

See `tools/config.py` for detailed configuration logic.

## Usage

### Auto Patch Project

Run the main program and enter the Maven project path when prompted:

```bash
python tools/main.py
```

The program will execute the following steps:
1. **Scan**: Check project dependencies for known vulnerabilities.
2. **Upgrade**: For each vulnerable dependency found, upgrade it to a safe version in `pom.xml`.
3. **Build & Fix**:
   - Attempt to compile the project.
   - If compilation succeeds, proceed to the next dependency.
   - If compilation fails, parse error logs to locate the failing file.
   - Call AI to analyze the error and generate fix code.
   - Apply the fix and retry compilation (default max 3 retries).

### Other Tools

- **GitHub Crawler**: `tools/github_crawler.py`
  Used to crawl high-star Maven projects on GitHub, useful for building test datasets.

## Project Structure

- `tools/main.py`: Entry point, coordinates scanning, updating, and fixing processes.
- `tools/scanner.py`: Dependency vulnerability scanning module, interfaces with OSV.dev.
- `tools/pom_updater.py`: `pom.xml` parsing and updating module.
- `tools/builder.py`: Maven build management and error log analysis module.
- `tools/fixer.py`: AI repair module, handles interaction with LLM to generate patches.
- `tools/config.py`: Global configuration file.
