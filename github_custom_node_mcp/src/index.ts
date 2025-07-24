import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { GitHubAPI } from "./github-api.js";

// GitHub API Configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || "";
const githubAPI = new GitHubAPI({ token: GITHUB_TOKEN });

// Create MCP Server
const server = new McpServer({
  name: "github-custom-mcp",
  version: "1.0.0",
  description: "Custom MCP server for GitHub operations including user management, repositories, and organizations."
});

// Tool: Get Authenticated User
server.registerTool(
  "get_authenticated_user",
  {
    title: "Get Authenticated User",
    description: "Get details of the authenticated GitHub user",
    inputSchema: {}
  },
  async () => {
    try {
      const userData = await githubAPI.makeRequest("/user");
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            login: userData.login,
            name: userData.name,
            email: userData.email,
            bio: userData.bio,
            company: userData.company,
            location: userData.location,
            blog: userData.blog,
            public_repos: userData.public_repos,
            followers: userData.followers,
            following: userData.following,
            created_at: userData.created_at,
            avatar_url: userData.avatar_url,
            html_url: userData.html_url
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error getting authenticated user: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Tool: Get User Organizations
server.registerTool(
  "get_user_organizations",
  {
    title: "Get User Organizations",
    description: "Get organizations for a user (authenticated user if no username provided)",
    inputSchema: {
      username: z.string().optional().describe("GitHub username (optional)")
    }
  },
  async ({ username }) => {
    try {
      const endpoint = username ? `/users/${username}/orgs` : "/user/orgs";
      const orgsData = await githubAPI.makeRequest(endpoint);
      
      const orgsSummary = orgsData.map((org: any) => ({
        login: org.login,
        description: org.description,
        html_url: org.html_url,
        avatar_url: org.avatar_url
      }));

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            total_organizations: orgsSummary.length,
            organizations: orgsSummary
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error getting organizations: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Tool: List Organization Repositories
server.registerTool(
  "list_org_repos",
  {
    title: "List Organization Repositories",
    description: "List repositories in an organization",
    inputSchema: {
      org: z.string().describe("Organization name"),
      type: z.enum(["all", "public", "private", "forks", "sources", "member"]).default("all").describe("Repository type"),
      sort: z.enum(["created", "updated", "pushed", "full_name"]).default("created").describe("Sort by"),
      direction: z.enum(["asc", "desc"]).default("desc").describe("Sort direction"),
      per_page: z.number().min(1).max(100).default(30).describe("Results per page"),
      page: z.number().min(1).default(1).describe("Page number")
    }
  },
  async ({ org, type, sort, direction, per_page, page }) => {
    try {
      const params = {
        type,
        sort,
        direction,
        per_page,
        page
      };
      
      const reposData = await githubAPI.makeRequest(`/orgs/${org}/repos`, params);
      
      const reposSummary = reposData.map((repo: any) => ({
        name: repo.name,
        full_name: repo.full_name,
        description: repo.description,
        language: repo.language,
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        watchers: repo.watchers_count,
        open_issues: repo.open_issues_count,
        private: repo.private,
        fork: repo.fork,
        archived: repo.archived,
        disabled: repo.disabled,
        created_at: repo.created_at,
        updated_at: repo.updated_at,
        pushed_at: repo.pushed_at,
        size: repo.size,
        default_branch: repo.default_branch,
        license: repo.license?.name || null,
        topics: repo.topics || [],
        html_url: repo.html_url,
        clone_url: repo.clone_url,
        ssh_url: repo.ssh_url,
        git_url: repo.git_url
      }));

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            organization: org,
            type_filter: type,
            sort,
            direction,
            page,
            per_page,
            total_repos_on_page: reposSummary.length,
            repositories: reposSummary
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error getting repositories for organization ${org}: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Tool: Get Organization Members
server.registerTool(
  "get_org_members",
  {
    title: "Get Organization Members",
    description: "Get members of an organization with filtering options",
    inputSchema: {
      org: z.string().describe("Organization name"),
      filter: z.enum(["all", "2fa_disabled", "2fa_insecure"]).default("all").describe("Filter members"),
      role: z.enum(["all", "admin", "member"]).default("all").describe("Filter by role"),
      per_page: z.number().min(1).max(100).default(30).describe("Results per page"),
      page: z.number().min(1).default(1).describe("Page number")
    }
  },
  async ({ org, filter, role, per_page, page }) => {
    try {
      const params = {
        filter,
        role,
        per_page,
        page
      };
      
      const membersData = await githubAPI.makeRequest(`/orgs/${org}/members`, params);
      
      const membersSummary = membersData.map((member: any) => ({
        login: member.login,
        id: member.id,
        node_id: member.node_id,
        html_url: member.html_url,
        avatar_url: member.avatar_url,
        type: member.type,
        site_admin: member.site_admin || false,
        url: member.url
      }));

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            organization: org,
            filter_applied: filter,
            role_filter: role,
            page,
            per_page,
            total_members_on_page: membersSummary.length,
            members: membersSummary
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error getting members for organization ${org}: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Tool: Get File Contents
server.registerTool(
  "get_file_contents",
  {
    title: "Get File Contents",
    description: "Get file or directory contents from a GitHub repository",
    inputSchema: {
      org: z.string().describe("Organization name"),
      repo: z.string().describe("Repository name"),
      path: z.string().default("").describe("File/directory path (empty for root)"),
      ref: z.string().default("main").describe("Branch or commit reference")
    }
  },
  async ({ org, repo, path, ref }) => {
    try {
      const endpoint = path ? `/repos/${org}/${repo}/contents/${path}` : `/repos/${org}/${repo}/contents`;
      const params = { ref };
      
      const contentData = await githubAPI.makeRequest(endpoint, params);
      
      // Handle single file
      if (!Array.isArray(contentData)) {
        let fileContent = "";
        if (contentData.content && contentData.encoding === "base64") {
          try {
            fileContent = Buffer.from(contentData.content, 'base64').toString('utf-8');
          } catch {
            fileContent = "[Binary file - cannot display as text]";
          }
        }
        
        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              repository: `${org}/${repo}`,
              type: "file",
              path: contentData.path,
              name: contentData.name,
              size: contentData.size,
              content: fileContent,
              download_url: contentData.download_url,
              html_url: contentData.html_url
            }, null, 2)
          }]
        };
      }
      
      // Handle directory listing
      const files: any[] = [];
      const directories: any[] = [];
      
      contentData.forEach((item: any) => {
        const itemInfo = {
          name: item.name,
          path: item.path,
          size: item.size,
          type: item.type,
          html_url: item.html_url,
          download_url: item.download_url
        };
        
        if (item.type === "file") {
          files.push(itemInfo);
        } else if (item.type === "dir") {
          directories.push(itemInfo);
        }
      });
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            repository: `${org}/${repo}`,
            type: "directory",
            path: path || "/",
            ref,
            summary: {
              total_items: contentData.length,
              directories: directories.length,
              files: files.length
            },
            directories: directories.sort((a, b) => a.name.localeCompare(b.name)),
            files: files.sort((a, b) => a.name.localeCompare(b.name))
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            error: `Failed to get contents for ${org}/${repo}/${path}`,
            message: error instanceof Error ? error.message : String(error)
          }, null, 2)
        }]
      };
    }
  }
);

// Tool: List Repository Branches
server.registerTool(
  "list_repo_branches",
  {
    title: "List Repository Branches",
    description: "List branches in a repository",
    inputSchema: {
      org: z.string().describe("Organization name"),
      repo: z.string().describe("Repository name"),
      protected: z.boolean().optional().describe("Filter by protected status"),
      per_page: z.number().min(1).max(100).default(30).describe("Results per page"),
      page: z.number().min(1).default(1).describe("Page number")
    }
  },
  async ({ org, repo, protected: isProtected, per_page, page }) => {
    try {
      const params: any = {
        per_page,
        page
      };
      
      if (isProtected !== undefined) {
        params.protected = isProtected.toString();
      }
      
      const branchesData = await githubAPI.makeRequest(`/repos/${org}/${repo}/branches`, params);
      
      const branchesSummary = branchesData.map((branch: any) => ({
        name: branch.name,
        commit: {
          sha: branch.commit?.sha,
          url: branch.commit?.url
        },
        protected: branch.protected || false,
        protection: branch.protection || null,
        protection_url: branch.protection_url
      }));

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            repository: `${org}/${repo}`,
            page,
            per_page,
            total_branches_on_page: branchesSummary.length,
            branches: branchesSummary
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error getting branches for repository ${org}/${repo}: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Tool: Search Repositories
server.registerTool(
  "search_repositories",
  {
    title: "Search Repositories",
    description: "Search for repositories on GitHub",
    inputSchema: {
      query: z.string().describe("Search query"),
      sort: z.enum(["stars", "forks", "help-wanted-issues", "updated"]).default("stars").describe("Sort by"),
      order: z.enum(["asc", "desc"]).default("desc").describe("Sort order"),
      per_page: z.number().min(1).max(100).default(10).describe("Results per page")
    }
  },
  async ({ query, sort, order, per_page }) => {
    try {
      const params = {
        q: query,
        sort,
        order,
        per_page
      };
      
      const searchData = await githubAPI.makeRequest("/search/repositories", params);
      
      const reposSummary = searchData.items?.map((repo: any) => ({
        name: repo.name,
        full_name: repo.full_name,
        description: repo.description,
        language: repo.language,
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        html_url: repo.html_url,
        owner: repo.owner?.login
      })) || [];

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            total_count: searchData.total_count,
            query,
            repositories: reposSummary
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error searching repositories: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Test function
async function testTools() {
  console.log("🔧 Testing GitHub MCP Tools...");
  
  try {
    // Test authenticated user
    console.log("\n1. Testing get_authenticated_user:");
    const userResult = await githubAPI.makeRequest("/user");
    console.log(JSON.stringify(userResult, null, 2));
    
    // Test user organizations
    console.log("\n2. Testing get_user_organizations:");
    const orgsResult = await githubAPI.makeRequest("/user/orgs");
    console.log(JSON.stringify(orgsResult, null, 2));
    
    console.log("\n✅ All tests completed successfully!");
  } catch (error) {
    console.error("❌ Test failed:", error);
  }
}

// Main function
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('test')) {
    await testTools();
    return;
  }
  
  // Start the MCP server
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("GitHub Custom MCP Server running on stdio");
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.error("\nShutting down GitHub MCP Server...");
  process.exit(0);
});

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});