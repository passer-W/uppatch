import requests
import time
from typing import List, Dict

class GitHubProjectSearcher:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com/search/repositories"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "WebProjectSearcher/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def search_projects(self, language: str, topics: List[str], min_stars: int = 1000, per_page: int = 20) -> List[Dict]:
        """
        搜索指定语言和主题的 GitHub 项目，按星数降序排列
        """
        # 构建搜索查询
        topic_query = " ".join([f"topic:{topic}" for topic in topics])
        query = f"language:{language} {topic_query} stars:>={min_stars}"
        
        params = {
            "q": query,
            "sort": "stars",  # 按星数排序
            "order": "desc",  # 降序排列
            "per_page": per_page
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            projects = []
            
            for item in data.get("items", []):
                project = {
                    "name": item["name"],
                    "full_name": item["full_name"],
                    "html_url": item["html_url"],
                    "description": item["description"],
                    "stars": item["stargazers_count"],
                    "language": item["language"],
                }
                projects.append(project)
            
            return projects
            
        except requests.exceptions.RequestException as e:
            print(f"搜索失败: {e}")
            return []

def get_top_projects():
    """获取星数最高的 Node.js 和 Python 项目"""

    token = "xxx"
    
    searcher = GitHubProjectSearcher(token)
    
    # Node.js Web 开发相关主题
    nodejs_topics = [
        "web", "webapp", "web-framework", "javascript", "nodejs",
        "react", "vue", "angular", "nextjs", "nuxtjs",
        "express", "koa", "nestjs", "fullstack", "spa"
    ]
    
    # Python Web 开发相关主题
    python_topics = [
        "web", "webapp", "web-framework", "python", "django",
        "flask", "fastapi", "api", "rest-api", "graphql",
        "backend", "fullstack", "sqlalchemy", "pydantic", "asgi"
    ]
    
    print("🚀 正在搜索 GitHub 上星数最高的 Web 项目...")
    print("⏳ 这可能需要几秒钟时间...")
    
    # 搜索 Node.js 项目（已按星数降序）
    nodejs_projects = searcher.search_projects(
        language="javascript",
        topics=nodejs_topics,
        min_stars=1000,
        per_page=20
    )
    
    # 搜索 Python 项目（已按星数降序）
    python_projects = searcher.search_projects(
        language="python",
        topics=python_topics,
        min_stars=1000,
        per_page=20
    )
    
    return nodejs_projects, python_projects

def main():
    # 获取项目数据（已按星数排序）
    nodejs_projects, python_projects = get_top_projects()
    
    print("\n" + "="*80)
    print("⭐ GitHub Web 项目 URL（按星数从高到低排序）")
    print("="*80)
    
    # 输出 Node.js 项目
    print(f"\n🔥 Node.js 项目（{len(nodejs_projects)}个）:")
    print("-" * 50)
    for i, project in enumerate(nodejs_projects, 1):
        print(f"{project['html_url']}")  # 只输出 URL
    
    # 输出 Python 项目
    print(f"\n🐍 Python 项目（{len(python_projects)}个）:")
    print("-" * 50)
    for i, project in enumerate(python_projects, 1):
        print(f"{project['html_url']}")  # 只输出 URL
    
    # 显示详细信息（可选）
    print(f"\n📊 项目详情（前5名）:")
    print("="*60)
    
    print(f"\n🏆 Node.js Top 5:")
    for i, project in enumerate(nodejs_projects[:5], 1):
        print(f"{i}. {project['full_name']} - ⭐ {project['stars']:,}")
    
    print(f"\n🏆 Python Top 5:")
    for i, project in enumerate(python_projects[:5], 1):
        print(f"{i}. {project['full_name']} - ⭐ {project['stars']:,}")

if __name__ == "__main__":
    main()