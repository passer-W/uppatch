import os
import requests
import subprocess
import json
from config import Config

class GitHubCrawler:
    """Module to crawl high-star Maven projects from GitHub."""

    def __init__(self, output_dir="projects"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def search_repositories(self, min_stars=1000, limit=5):
        """Search for Java Maven projects with high stars."""
        print(f"Searching for Java projects with >{min_stars} stars...")
        
        # Query: language:java AND topic:maven AND stars:>min_stars
        query = f"language:java topic:maven stars:>{min_stars}"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if Config.GITHUB_TOKEN:
            headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"

        try:
            response = requests.get(Config.GITHUB_API_URL, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                print(f"Found {len(items)} repositories.")
                return items
            else:
                print(f"GitHub API Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Network error: {e}")
            return []

    def clone_repository(self, repo_url, repo_name):
        """Clone a single repository."""
        target_path = os.path.join(self.output_dir, repo_name)
        
        if os.path.exists(target_path):
            print(f"  [SKIP] {repo_name} already exists.")
            return target_path

        print(f"  [CLONE] Cloning {repo_name}...")
        try:
            subprocess.run(
                ["git", "clone", repo_url, target_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"  [SUCCESS] Cloned to {target_path}")
            return target_path
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to clone {repo_name}: {e}")
            return None

    def save_list(self, repos):
        """Save the list of found repositories to a JSON file."""
        file_path = os.path.join(self.output_dir, "repos_list.json")
        data = []
        for repo in repos:
            data.append({
                "name": repo["name"],
                "full_name": repo["full_name"],
                "stars": repo["stargazers_count"],
                "url": repo["html_url"],
                "clone_url": repo["clone_url"]
            })
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Repository list saved to {file_path}")

    def run(self):
        # Interactive mode
        try:
            min_stars = int(input("Minimum stars (default 1000): ") or 1000)
            limit = int(input("Number of repos to fetch (default 5): ") or 5)
        except ValueError:
            print("Invalid input, using defaults.")
            min_stars = 1000
            limit = 5

        repos = self.search_repositories(min_stars, limit)
        if not repos:
            return

        self.save_list(repos)

        # Print summary
        print("\nTop Repositories Found:")
        for i, repo in enumerate(repos):
            print(f"{i+1}. {repo['full_name']} ({repo['stargazers_count']} stars) - {repo['html_url']}")

        clone_choice = input("\nDo you want to clone these repositories? (y/n): ").lower().strip()
        if clone_choice == 'y':
            for repo in repos:
                self.clone_repository(repo["clone_url"], repo["name"])
        else:
            print("Skipping clone.")

if __name__ == "__main__":
    crawler = GitHubCrawler()
    crawler.run()
