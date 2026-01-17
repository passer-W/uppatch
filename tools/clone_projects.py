import os
import sys

# Add the current directory to sys.path so we can import from local modules if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_crawler import GitHubCrawler

def main():
    # Define paths
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(tools_dir)
    projects_file = os.path.join(tools_dir, "projects.txt")
    output_dir = os.path.join(project_root, "projects")

    # Initialize crawler
    # GitHubCrawler creates the directory if it doesn't exist
    crawler = GitHubCrawler(output_dir=output_dir)
    
    # Read projects list
    if not os.path.exists(projects_file):
        print(f"Error: {projects_file} not found.")
        return

    print(f"Reading projects from {projects_file}...")
    with open(projects_file, "r") as f:
        lines = f.readlines()

    # Process each line
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        # Extract repo name from URL
        # URL format: https://github.com/user/repo
        parts = line.rstrip('/').split("/")
        if len(parts) >= 2:
            repo_name = parts[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            
            # Use GitHubCrawler's clone functionality
            print(f"Processing: {line}")
            crawler.clone_repository(line, repo_name)
        else:
            print(f"Skipping invalid URL: {line}")

if __name__ == "__main__":
    main()
