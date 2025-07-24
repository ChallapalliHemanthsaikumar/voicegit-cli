import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# GitHub API Configuration
GITHUB_API_BASE = "https://api.github.com"

# Initialize FastMCP server
mcp = FastMCP("GitHub")

class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to GitHub API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_BASE}{endpoint}",
                headers=self.headers,
                params=params or {}
            )
            response.raise_for_status()
            return response.json()

# Initialize GitHub API with token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "ACCESS_TOKEN")
github_api = GitHubAPI(GITHUB_TOKEN)

@mcp.tool()
async def get_authenticated_user() -> str:
    """Get details of the authenticated GitHub user"""
    try:
        user_data = await github_api.make_request("/user")
        return json.dumps({
            "login": user_data.get("login"),
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "bio": user_data.get("bio"),
            "company": user_data.get("company"),
            "location": user_data.get("location"),
            "blog": user_data.get("blog"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "following": user_data.get("following"),
            "created_at": user_data.get("created_at"),
            "avatar_url": user_data.get("avatar_url"),
            "html_url": user_data.get("html_url")
        }, indent=2)
    except Exception as e:
        return f"Error getting authenticated user: {str(e)}"

@mcp.tool()
async def get_user_by_username(username: str) -> str:
    """Get public details of a GitHub user by username"""
    try:
        user_data = await github_api.make_request(f"/users/{username}")
        return json.dumps({
            "login": user_data.get("login"),
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "company": user_data.get("company"),
            "location": user_data.get("location"),
            "blog": user_data.get("blog"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "following": user_data.get("following"),
            "created_at": user_data.get("created_at"),
            "avatar_url": user_data.get("avatar_url"),
            "html_url": user_data.get("html_url")
        }, indent=2)
    except Exception as e:
        return f"Error getting user {username}: {str(e)}"

@mcp.tool()
async def get_user_repositories(username: Optional[str] = None, per_page: int = 30, page: int = 1) -> str:
    """Get repositories for a user (authenticated user if no username provided)"""
    try:
        endpoint = "/user/repos" if username is None else f"/users/{username}/repos"
        params = {"per_page": min(per_page, 100), "page": max(page, 1)}
        
        repos_data = await github_api.make_request(endpoint, params)
        
        repos_summary = []
        for repo in repos_data:
            repos_summary.append({
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "private": repo.get("private"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "html_url": repo.get("html_url")
            })
        
        return json.dumps({
            "total_repos": len(repos_summary),
            "page": page,
            "per_page": per_page,
            "repositories": repos_summary
        }, indent=2)
    except Exception as e:
        return f"Error getting repositories: {str(e)}"

@mcp.tool()
async def get_user_organizations(username: Optional[str] = None) -> str:
    """Get organizations for a user (authenticated user if no username provided)"""
    try:
        endpoint = "/user/orgs" if username is None else f"/users/{username}/orgs"
        orgs_data = await github_api.make_request(endpoint)
        
        orgs_summary = []
        for org in orgs_data:
            orgs_summary.append({
                "login": org.get("login"),
                "description": org.get("description"),
                "html_url": org.get("html_url"),
                "avatar_url": org.get("avatar_url")
            })
        
        return json.dumps({
            "total_organizations": len(orgs_summary),
            "organizations": orgs_summary
        }, indent=2)
    except Exception as e:
        return f"Error getting organizations: {str(e)}"

@mcp.tool()
async def get_repository_details(owner: str, repo: str) -> str:
    """Get detailed information about a specific repository"""
    try:
        repo_data = await github_api.make_request(f"/repos/{owner}/{repo}")
        
        return json.dumps({
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "watchers": repo_data.get("watchers_count"),
            "open_issues": repo_data.get("open_issues_count"),
            "default_branch": repo_data.get("default_branch"),
            "private": repo_data.get("private"),
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "pushed_at": repo_data.get("pushed_at"),
            "size": repo_data.get("size"),
            "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
            "topics": repo_data.get("topics", []),
            "html_url": repo_data.get("html_url"),
            "clone_url": repo_data.get("clone_url")
        }, indent=2)
    except Exception as e:
        return f"Error getting repository {owner}/{repo}: {str(e)}"

@mcp.tool()
async def search_repositories(query: str, sort: str = "stars", order: str = "desc", per_page: int = 10) -> str:
    """Search for repositories on GitHub"""
    try:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(per_page, 100)
        }
        
        search_data = await github_api.make_request("/search/repositories", params)
        
        repos_summary = []
        for repo in search_data.get("items", []):
            repos_summary.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "html_url": repo.get("html_url"),
                "owner": repo.get("owner", {}).get("login")
            })
        
        return json.dumps({
            "total_count": search_data.get("total_count"),
            "query": query,
            "repositories": repos_summary
        }, indent=2)
    except Exception as e:
        return f"Error searching repositories: {str(e)}"

@mcp.tool()
async def get_user_followers(username: Optional[str] = None, per_page: int = 30) -> str:
    """Get followers for a user (authenticated user if no username provided)"""
    try:
        endpoint = "/user/followers" if username is None else f"/users/{username}/followers"
        params = {"per_page": min(per_page, 100)}
        
        followers_data = await github_api.make_request(endpoint, params)
        
        followers_summary = []
        for follower in followers_data:
            followers_summary.append({
                "login": follower.get("login"),
                "html_url": follower.get("html_url"),
                "avatar_url": follower.get("avatar_url")
            })
        
        return json.dumps({
            "total_followers": len(followers_summary),
            "followers": followers_summary
        }, indent=2)
    except Exception as e:
        return f"Error getting followers: {str(e)}"

@mcp.tool()
async def get_user_following(username: Optional[str] = None, per_page: int = 30) -> str:
    """Get users that a user is following (authenticated user if no username provided)"""
    try:
        endpoint = "/user/following" if username is None else f"/users/{username}/following"
        params = {"per_page": min(per_page, 100)}
        
        following_data = await github_api.make_request(endpoint, params)
        
        following_summary = []
        for user in following_data:
            following_summary.append({
                "login": user.get("login"),
                "html_url": user.get("html_url"),
                "avatar_url": user.get("avatar_url")
            })
        
        return json.dumps({
            "total_following": len(following_summary),
            "following": following_summary
        }, indent=2)
    except Exception as e:
        return f"Error getting following: {str(e)}"

# Test function
async def test_tools():
    """Test all the GitHub tools"""
    print("🔧 Testing GitHub MCP Tools...")
    
    # Test authenticated user
    print("\n1. Testing get_authenticated_user:")
    result = await get_authenticated_user()
    print(result)
    
    # Test user by username
    print("\n2. Testing get_user_by_username:")
    result = await get_user_by_username("hemanth")
    print(result)
    
    # Test user repositories
    print("\n3. Testing get_user_repositories:")
    result = await get_user_repositories(per_page=5)
    print(result)
    
    # Test user organizations
    print("\n4. Testing get_user_organizations:")
    result = await get_user_organizations()
    print(result)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests
        asyncio.run(test_tools())
    else:
        # Run as MCP server
        mcp.run(transport="stdio")