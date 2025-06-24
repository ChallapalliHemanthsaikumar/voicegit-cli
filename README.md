<!-- ## Create a Github agent with mcp 


## Create a Code Agent with CMD access 

Code agent new repo and commit in that tab should handle  on that particular cmd line 

which does commands in git repo 

cmd message  -->


## VoiceGIT CLI TOOL


### Prerequisites 

- Python 3.7 or higher 
- Git Installed on your system 
- Windows OS 

### Installation 

### Option 1: Quick Setup (Recommended):

``` bash 

git clone <url>
cd assistantagent

python -m venv venv 
venv\Scripts\activate

## install 

pip install -r requirements.txt

## Build standalone app 
pyinstaller --onefile src/cli.py --name voicegit

## it adds path as autoinstaller 

python setup.py develop 


###### test 

voicegit 
```




