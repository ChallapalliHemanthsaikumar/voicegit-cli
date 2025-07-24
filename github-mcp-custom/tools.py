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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_TOKEN = ""
github_api = GitHubAPI(GITHUB_TOKEN)

@mcp.tool()
async def get_authenticated_user() -> str:
    """Get details of the authenticated GitHub user"""
    try:
        user_data = await github_api.make_request("/user")
        # return json.dumps({
        #     "login": user_data.get("login"),
        #     "name": user_data.get("name"),
        #     "email": user_data.get("email"),
        #     "bio": user_data.get("bio"),
        #     "company": user_data.get("company"),
        #     "location": user_data.get("location"),
        #     "blog": user_data.get("blog"),
        #     "public_repos": user_data.get("public_repos"),
        #     "followers": user_data.get("followers"),
        #     "following": user_data.get("following"),
        #     "created_at": user_data.get("created_at"),
        #     "avatar_url": user_data.get("avatar_url"),
        #     "html_url": user_data.get("html_url")
        # }, indent=2)

        return user_data
    except Exception as e:
        return f"Error getting authenticated user: {str(e)}"

# @mcp.tool()
# async def get_user_by_username(username: str) -> str:
#     """Get public details of a GitHub user by username"""
#     try:
#         user_data = await github_api.make_request(f"/users/{username}")
#         return json.dumps({
#             "login": user_data.get("login"),
#             "name": user_data.get("name"),
#             "bio": user_data.get("bio"),
#             "company": user_data.get("company"),
#             "location": user_data.get("location"),
#             "blog": user_data.get("blog"),
#             "public_repos": user_data.get("public_repos"),
#             "followers": user_data.get("followers"),
#             "following": user_data.get("following"),
#             "created_at": user_data.get("created_at"),
#             "avatar_url": user_data.get("avatar_url"),
#             "html_url": user_data.get("html_url")
#         }, indent=2)
#     except Exception as e:
#         return f"Error getting user {username}: {str(e)}"

# @mcp.tool()
# async def get_user_repositories(username: Optional[str] = None, per_page: int = 30, page: int = 1) -> str:
#     """Get repositories for a user (authenticated user if no username provided)"""
#     try:
#         endpoint = "/user/repos" if username is None else f"/users/{username}/repos"
#         params = {"per_page": min(per_page, 100), "page": max(page, 1)}
        
#         repos_data = await github_api.make_request(endpoint, params)
        
#         repos_summary = []
#         for repo in repos_data:
#             repos_summary.append({
#                 "name": repo.get("full_name"),
#                 "description": repo.get("description"),
#                 "language": repo.get("language"),
#                 "stars": repo.get("stargazers_count"),
#                 "forks": repo.get("forks_count"),
#                 "private": repo.get("private"),
#                 "created_at": repo.get("created_at"),
#                 "updated_at": repo.get("updated_at")
                
#             })
        
#         return json.dumps({
#             "total_repos": len(repos_summary),
#             "page": page,
#             "per_page": per_page,
#             "repositories": repos_summary
#         }, indent=2)
#         return repos_data
#     except Exception as e:
#         return f"Error getting repositories: {str(e)}"

@mcp.tool()
async def list_user_organizations(username: Optional[str] = None) -> str:
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


        # return orgs_data
        
        return json.dumps({
            "total_organizations": len(orgs_summary),
            "organizations": orgs_summary
        }, indent=2)
    except Exception as e:
        return f"Error getting organizations: {str(e)}"



# @mcp.tool()
# async def get_org_members(org: str) -> str:
#     """Get public members of an organization"""
#     try:
#         # Remove the trailing slash - this was causing the 404 error
#         endpoint = f"/orgs/{org}/members"
#         members_data = await github_api.make_request(endpoint)
        
#         members_summary = []
#         for member in members_data:
#             members_summary.append({
#                 "login": member.get("login"),
#                 "id": member.get("id"),
#                 "html_url": member.get("html_url"),
#                 "avatar_url": member.get("avatar_url"),
#                 "type": member.get("type")
#             })
        
#         return json.dumps({
#             "organization": org,
#             "total_public_members": len(members_summary),
#             "members": members_summary
#         }, indent=2)
        
#     except Exception as e:
#         return f"Error getting members for organization {org}: {str(e)}"


@mcp.tool()
async def list_org_repos(org: str, type: str = "all", sort: str = "created", direction: str = "desc", per_page: int = 30, page: int = 1) -> str:
    """List repositories in an organization
    
    Args:
        org: Organization name
        type: Repository type (all, public, private, forks, sources, member)
        sort: Sort by (created, updated, pushed, full_name)
        direction: Sort direction (asc, desc)
        per_page: Results per page (max 100)
        page: Page number
    """
    try:
        endpoint = f"/orgs/{org}/repos"
        params = {
            "type": type,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),
            "page": max(page, 1)
        }
        
        repos_data = await github_api.make_request(endpoint, params)
        
        repos_summary = []
        for repo in repos_data:
            repos_summary.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "watchers": repo.get("watchers_count"),
                "open_issues": repo.get("open_issues_count"),
                "private": repo.get("private"),
                "fork": repo.get("fork"),
                "archived": repo.get("archived"),
                "disabled": repo.get("disabled"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "size": repo.get("size"),
                "default_branch": repo.get("default_branch"),
                "license": repo.get("license", {}).get("name") if repo.get("license") else None,
                "topics": repo.get("topics", []),
                "html_url": repo.get("html_url"),
                "clone_url": repo.get("clone_url"),
                "ssh_url": repo.get("ssh_url"),
                "git_url": repo.get("git_url")
            })
        # return repos_data
        return json.dumps({
            "organization": org,
            "type_filter": type,
            "sort": sort,
            "direction": direction,
            "page": page,
            "per_page": per_page,
            "total_repos_on_page": len(repos_summary),
            "repositories": repos_summary
        }, indent=2)
    except Exception as e:
        print("Error",e)

@mcp.tool()
async def get_org_file_contents(org: str, repo: str, path: str = "", ref: str = "main") -> str:
    """
    Get file or directory contents from a GitHub repository
    
    Args:
        org: Organization name (e.g., 'People-tech-qg')
        repo: Repository name (e.g., 'apple-multiagent-cdk') 
        path: File/directory path (empty for root, e.g., 'src/app.py', 'README.md')
        ref: Branch or commit reference (default: 'main')
    """
    try:
        # Build endpoint
        if path:
            endpoint = f"/repos/{org}/{repo}/contents/{path}"
        else:
            endpoint = f"/repos/{org}/{repo}/contents"
        
        params = {"ref": ref}
        content_data = await github_api.make_request(endpoint, params)
        
        # Handle single file
        if isinstance(content_data, dict):
            # Decode file content if it's base64 encoded
            file_content = ""
            if content_data.get("content") and content_data.get("encoding") == "base64":
                import base64
                try:
                    file_content = base64.b64decode(content_data.get("content")).decode('utf-8')
                except:
                    file_content = "[Binary file - cannot display as text]"
            
            return json.dumps({
                "repository": f"{org}/{repo}",
                "type": "file",
                "path": content_data.get("path"),
                "name": content_data.get("name"),
                "size": content_data.get("size"),
                "content": file_content
            }, indent=2)
        
        # Handle directory listing
        else:
            files = []
            directories = []
            
            for item in content_data:
                item_info = {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "size": item.get("size"),
                    "type": item.get("type"),
                    
                }
                
                if item.get("type") == "file":
                    files.append(item_info)
                elif item.get("type") == "dir":
                    directories.append(item_info)
            
            return json.dumps({
                "repository": f"{org}/{repo}",
                "type": "directory", 
                "path": path or "/",
                "ref": ref,
                "summary": {
                    "total_items": len(content_data),
                    "directories": len(directories),
                    "files": len(files)
                },
                "directories": sorted(directories, key=lambda x: x["name"]),
                "files": sorted(files, key=lambda x: x["name"])
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get contents for {org}/{repo}/{path}",
            "message": str(e)
        }, indent=2)




@mcp.tool()
async def list_org_repos_branches(org: str,repo:str, type: str = "all", sort: str = "created", direction: str = "desc", per_page: int = 30, page: int = 1) -> str:
    """List repositories in an organization
    
    Args:
        org: Organization name
        type: Repository type (all, public, private, forks, sources, member)
        sort: Sort by (created, updated, pushed, full_name)
        direction: Sort direction (asc, desc)
        per_page: Results per page (max 100)
        page: Page number
    """
    try:
        
        endpoint = f"/repos/{org}/{repo}/branches"
        params = {
            "type": type,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),
            "page": max(page, 1)
        }
        
        repos_data = await github_api.make_request(endpoint, params)
        
        repos_summary = []
        for repo in repos_data:
            repos_summary.append({
                "name": repo.get("name"),
               
            })
        return repos_summary

  


     
        
    except Exception as e:
        return f"Error getting repositories for organization {org}: {str(e)}"


# @mcp.tool()
# async def get__org_file_contents():

    




@mcp.tool()
async def get_org_members(org: str, filter: str = "all", role: str = "all", per_page: int = 30, page: int = 1) -> str:
    """Get members of an organization with filtering options
    
    Args:
        org: Organization name
        filter: Filter members (all, 2fa_disabled, 2fa_insecure) - only for org owners
        role: Filter by role (all, admin, member) 
        per_page: Results per page (max 100)
        page: Page number
    """
    try:
        endpoint = f"/orgs/{org}/members"
        params = {
            "filter": filter,
            "role": role,
            "per_page": min(per_page, 100),
            "page": max(page, 1)
        }
        
        members_data = await github_api.make_request(endpoint, params)
        
        members_summary = []
        for member in members_data:
            members_summary.append({
                "login": member.get("login"),
                "id": member.get("id"),
                "node_id": member.get("node_id"),
                "html_url": member.get("html_url"),
                "avatar_url": member.get("avatar_url"),
                "type": member.get("type"),
                "site_admin": member.get("site_admin", False),
                "url": member.get("url")
            })
        
        return json.dumps({
            "organization": org,
            "filter_applied": filter,
            "role_filter": role,
            "page": page,
            "per_page": per_page,
            "total_members_on_page": len(members_summary),
            "members": members_summary
        }, indent=2)
        
    except Exception as e:
        return f"Error getting members for organization {org}: {str(e)}"






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
    


# @mcp.tool()
# async def get_user_followers(username: Optional[str] = None, per_page: int = 30) -> str:
#     """Get followers for a user (authenticated user if no username provided)"""
#     try:
#         endpoint = "/user/followers" if username is None else f"/users/{username}/followers"
#         params = {"per_page": min(per_page, 100)}
        
#         followers_data = await github_api.make_request(endpoint, params)
        
#         followers_summary = []
#         for follower in followers_data:
#             followers_summary.append({
#                 "login": follower.get("login"),
#                 "html_url": follower.get("html_url"),
#                 "avatar_url": follower.get("avatar_url")
#             })
        
#         return json.dumps({
#             "total_followers": len(followers_summary),
#             "followers": followers_summary
#         }, indent=2)
#     except Exception as e:
#         return f"Error getting followers: {str(e)}"

# @mcp.tool()
# async def get_user_following(username: Optional[str] = None, per_page: int = 30) -> str:
#     """Get users that a user is following (authenticated user if no username provided)"""
#     try:
#         endpoint = "/user/following" if username is None else f"/users/{username}/following"
#         params = {"per_page": min(per_page, 100)}
        
#         following_data = await github_api.make_request(endpoint, params)
        
#         following_summary = []
#         for user in following_data:
#             following_summary.append({
#                 "login": user.get("login"),
#                 "html_url": user.get("html_url"),
#                 "avatar_url": user.get("avatar_url")
#             })
        
#         return json.dumps({
#             "total_following": len(following_summary),
#             "following": following_summary
#         }, indent=2)
#     except Exception as e:
#         return f"Error getting following: {str(e)}"

# Test function
async def test_tools():
    """Test all the GitHub tools"""
    print("🔧 Testing GitHub MCP Tools...")
    
    # Test authenticated user
    print("\n1. Testing get_authenticated_user:")
    result = await get_authenticated_user()
    print(result)
    
    # # Test user by username
    # print("\n2. Testing get_user_by_username:")
    # result = await get_user_by_username("hemanth")
    # print(result)
    
    # # Test user repositories
    # print("\n3. Testing get_user_repositories:")
    # result = await list_user_repositories(per_page=5)
    # print(result)
    
    # # # Test user organizations
    # print("\n4. Testing get_user_organizations:")
    result = await list_user_organizations()
    # print(result)

    result = await get_org_members("People-tech-qg")
    print(result)

    result = await list_org_repos("People-tech-qg")
    print(result)

    result = await list_org_repos_branches("People-tech-qg","apple-multiagent-cdk")
    print(result)


    print("\n4. Getting ORG file Contents:")

    result = await get_org_file_contents("People-tech-qg","apple-multiagent-cdk","src/agent")

    print(result)


    print("\n Get Username repos")






if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests
        asyncio.run(test_tools())
    else:
        # Run as MCP server
        mcp.run(transport="stdio")