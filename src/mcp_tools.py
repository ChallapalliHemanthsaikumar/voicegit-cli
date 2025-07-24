import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent



from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent



client = MultiServerMCPClient({

      "github": {
        "command": "C:/Users/Hemanth/Desktop/assistantagent/github-mcp-server/github-mcp-server.exe",
        "args": ["stdio"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "ACCESS_TOKEN"
        },
        "transport": "stdio"
      }
})

