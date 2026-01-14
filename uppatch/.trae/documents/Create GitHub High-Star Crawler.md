# GitHub High-Star Project Crawler Plan

I will implement a new script `github_crawler.py` that fetches high-star Maven/Java projects from GitHub. This script will be designed to integrate with the existing modular architecture (or run standalone) to provide test targets for the patching system.

## 1. Features
*   **Search Criteria**: Fetch repositories based on language (Java), build tool (Maven), and star count (e.g., > 1000).
*   **API Usage**: Use GitHub REST API (Search Repositories endpoint).
*   **Output**: Save the list of repositories (clone URL, name, stars) to a JSON or CSV file.
*   **Cloning (Optional)**: Provide a utility to clone these repositories locally for analysis.

## 2. Implementation Details
*   **Script Name**: `github_crawler.py`
*   **Class**: `GitHubCrawler`
*   **Configuration**: Add `GITHUB_TOKEN` to `config.py` (optional but recommended for rate limits).
*   **Dependencies**: `requests` (already in `requirements.txt`).

## 3. Integration
*   I will update `config.py` to include GitHub-related configs.
*   The crawler will be a standalone tool but can be used to populate a "workspace" for the `AutoPatcher` to process in batch.

## 4. Execution Flow
1.  User runs `github_crawler.py`.
2.  Script queries GitHub API: `q=language:java+topic:maven&sort=stars`.
3.  Script prints top N repositories.
4.  (Optional) Script asks if user wants to clone them to a `projects/` directory.

## 5. Next Steps
1.  Update `config.py`.
2.  Create `github_crawler.py`.
3.  Run and verify.