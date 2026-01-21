import os

class Config:
    """Central configuration for the Auto Patcher system."""
    
    # LLM Configuration
    LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-ac065af7b7b6460896608fd750c100d8")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
    
    # Tool Configuration
    MAX_RETRIES = 3
    MAVEN_CMD = "mvn"
    PIP_CMD = "pip"
    NPM_CMD = "npm"
    
    # API URLs
    OSV_QUERY_URL = "https://api.osv.dev/v1/query"
    GITHUB_API_URL = "https://api.github.com/search/repositories"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Optional: for higher rate limits

    @classmethod
    def print_config(cls):
        print("Loaded Configuration:")
        print(f"  LLM Model: {cls.LLM_MODEL}")
        print(f"  Max Retries: {cls.MAX_RETRIES}")
        if cls.GITHUB_TOKEN:
            print("  GitHub Token: [Present]")
        else:
            print("  GitHub Token: [Missing] (Rate limits may apply)")

if __name__ == "__main__":
    Config.print_config()
