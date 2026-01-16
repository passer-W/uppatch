# Modular Python Automated Patching Architecture Plan

I will refactor the monolithic `auto_patcher.py` into a robust, modular architecture with separate scripts for each responsibility. Each script will be designed as a standalone module with a class-based structure and independent execution capability.

## 1. Architecture Overview

The system will be split into the following components:

1.  **`config.py`**: Centralized configuration management.
2.  **`scanner.py`**: Dependency analysis and CVE detection module.
3.  **`pom_updater.py`**: POM file manipulation module.
4.  **`builder.py`**: Build execution and log parsing module.
5.  **`fixer.py`**: AI-powered code repair module.
6.  **`main.py`**: The orchestration entry point.

## 2. Detailed Module Design

### 2.1 Configuration (`config.py`)
*   **Responsibility**: Store API keys, URLs, and constants.
*   **Features**: Load from environment variables or use defaults.

### 2.2 Dependency Scanner (`scanner.py`)
*   **Class**: `DependencyScanner`
*   **Methods**:
    *   `get_dependencies(project_path)`: Runs Maven command to list dependencies.
    *   `check_cve(group, artifact, version)`: Queries OSV.dev.
    *   `scan_project(project_path)`: Orchestrates the scan and returns a report of vulnerable dependencies with recommended fixes.
*   **Standalone Mode**: Can be run to just scan a project and print vulnerabilities.

### 2.3 POM Updater (`pom_updater.py`)
*   **Class**: `PomUpdater`
*   **Methods**:
    *   `update_dependency(file_path, group, artifact, new_version)`: Safely updates the version in `pom.xml` using `lxml`.
*   **Standalone Mode**: Can be run to update a specific dependency.

### 2.4 Build Manager (`builder.py`)
*   **Class**: `BuildManager`
*   **Methods**:
    *   `compile_project(project_path)`: Runs `mvn clean compile`.
    *   `parse_errors(log_output)`: Extracts structured error data (file, line, message).
*   **Standalone Mode**: Can be run to compile and see parsed errors.

### 2.5 AI Fixer (`fixer.py`)
*   **Class**: `AIFixer`
*   **Methods**:
    *   `generate_fix(error_info, code_context)`: Calls DeepSeek API.
    *   `apply_fix(file_path, original_code, fixed_code)`: Applies the patch to the file.
*   **Standalone Mode**: Can be used to test the LLM connection.

### 2.6 Orchestrator (`main.py`)
*   **Responsibility**: Tie everything together.
*   **Flow**:
    1.  Initialize modules.
    2.  `Scanner` -> Find vulnerabilities.
    3.  Loop through vulnerabilities:
        *   `PomUpdater` -> Update version.
        *   `BuildManager` -> Compile.
        *   If Error -> `Fixer` -> Fix Code -> Retry Compile.
        *   Verify success.

## 3. Implementation Steps

1.  Create `config.py`.
2.  Create `scanner.py` with `DependencyScanner`.
3.  Create `pom_updater.py` with `PomUpdater`.
4.  Create `builder.py` with `BuildManager`.
5.  Create `fixer.py` with `AIFixer`.
6.  Create `main.py` to coordinate the workflow.
7.  (Optional) Remove the old `auto_patcher.py`.

This approach ensures maintainability, testability, and clear separation of concerns, fulfilling the requirement for "complete architecture" in each script.