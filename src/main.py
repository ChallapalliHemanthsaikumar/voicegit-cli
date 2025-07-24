import asyncio
import os 
import json
from pathlib import Path
import time 
from model import azure_llm,aws_llm
from langgraph.prebuilt import create_react_agent
from mcp_tools import client
from colorama import init, Fore, Back, Style

init(autoreset=True)

def show_config_location():
    """Show where config file is stored"""
    config_path = get_config_path()
    print(f"📁 Config file location: {config_path}")
    if config_path.exists():
        print("✅ Config file exists")
    else:
        print("⚠️ Config file not found")
    return config_path

def greet():
    try:
    

        config_data = read_config()

        if config_data and "user" in config_data:
            user = config_data["user"]
            return f"Hello {user["name"]}"

        return "Hello Hemanth you can do it"
    except Exception as e:
        print("Error ",e)


def config(name,email):
    try:

        """ Create or update config.json with user details"""

        config_file = Path("src/config.json")
        import time
        user_config = { 
            "user": {
                "name": name,
                "email": email,
                "created_at": str(time.time())
            }
        }

        if config_file.exists():
            with open(config_file,'r',encoding='utf-8') as f:
                existing_config = json.load(f)
            
            existing_config["user"]['name'] = name
            existing_config["user"]["email"] = email

            with open(config_file,'w',encoding='utf-8') as f:
                json.dump(existing_config,f,indent=4,ensure_ascii=False)

            print(f" Updated Config for :{name}, {email}")
        else:
                # Create new config file
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(user_config, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Created new config for: {name} ({email})")
            
        return config_file
    except Exception as e:
        print(f"❌ Error managing config: {e}")
        return None
    


def  get_config_path():
    """ Get Consistent COnfig file path regardless of the current directory"""

    return Path(__file__).parent / "config.json"


def read_config():
    
    """Read and return config data"""
    config_file = get_config_path()
    
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("⚠️ Config file not found")
            return None
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return None
    

def llm_call(messages):

    if len(messages) > 5:
        response = azure_llm.invoke(messages[-5:])
    else:
        response = azure_llm.invoke(messages)
        

    
    # print(response.content)
    return response.content



def filter(messages):
    if len(messages)> 5:
        context_messages = messages[-5:]
    else:
        context_messages = messages
    return context_messages

async def azure_agent(messages):

    tools = await client.get_tools()
    # tools = []

    

    GitAgent = create_react_agent(model=azure_llm,prompt="Your are a Git Agent which does takes for Git Actions if your asks give about me use get_me tool first gather user info ",tools=tools)
    context_messages = filter(messages)
  
    async for chunk in GitAgent.astream({"messages": context_messages}):
    # Check if this chunk contains agent messages
        if "agent" in chunk:
            if "messages" in chunk["agent"]:
                for message in chunk["agent"]["messages"]:
                    if hasattr(message, 'content') and message.content:
                        yield message.content




async def aws_agent(messages):

    tools = await client.get_tools()

    # tools = []

    GitAgent = create_react_agent(model=aws_llm,prompt="Your are a Git Agent which does takes for Git Actions if your asks give about me use get_me tool first gather user info ",tools=tools)
    context_messages = filter(messages)
    
    
    # return  response["messages"][-1].content
    async for chunk in GitAgent.astream({"messages": context_messages}):
        if "agent" in chunk:
            if "messages" in chunk["agent"]:
                for message in chunk["agent"]["messages"]:
                    if hasattr(message, 'content'):
                        # Handle different content types
                        if isinstance(message.content, str):
                            yield message.content
                        elif isinstance(message.content, list):
                            for content_item in message.content:
                                if isinstance(content_item, dict):
                                    if content_item.get('type') == 'text':
                                        yield content_item.get('text', '')
                                else:
                                    yield str(content_item)
                        else:
                            yield str(message.content)
        # Handle tool execution chunks
        elif "tools" in chunk:
                if "messages" in chunk["tools"]:
                    for message in chunk["tools"]["messages"]:
                        if hasattr(message, 'content') and message.content:
                            yield f"\n🔧 Tool executed: {message.content}\n"


async def interactive():

    messages = []
    config_data = read_config()

    if config_data and "user" in config_data:
        user = config_data["user"]
        # return f"Hello {user["name"]}"

    print(f"{Fore.CYAN}{Style.BRIGHT} Git Agent Chat started!")
    print(f"{Fore.YELLOW}Type 'quit', 'q', or 'stop' to exit{Style.RESET_ALL}")
    # print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}")

    



    while True:

        ### User chat 
        try:
            if user:
                user_prompt = f"{Fore.CYAN}{Style.BRIGHT} {user['name']}: {Style.RESET_ALL}"
            else: 
                user_prompt = f"{Fore.CYAN}{Style.BRIGHT} User: {Style.RESET_ALL}"
            text = input(user_prompt)

            if text.lower() in ["quit", "q", "stop"]:
                print(f"{Fore.MAGENTA}{Style.BRIGHT} Goodbye! Thanks for using VoiceGit!{Style.RESET_ALL}")
                break
            else:
                messages.append({"role":"user","content":text})

            # assistant_reply = llm_call(messages)
            print(f"\n{Fore.GREEN}{Style.BRIGHT} Assistant: {Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}", end="", flush=True)
            full_response = ""
            async for chunk in aws_agent(messages):
                print(chunk, end="", flush=True)
                
                full_response += chunk

            messages.append({"role": 'assistant',"content":full_response})
            # print(f"{Fore.GREEN}{Style.BRIGHT} Assistant:{Style.RESET_ALL}")
            print(f"{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'*' * 50}{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}{Style.BRIGHT}⚠️ Chat interrupted by user{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}{Style.BRIGHT}❌ Error: {e}{Style.RESET_ALL}")



# interactive()
asyncio.run(interactive())






    


