# # from setuptools import setup,find_packages
# # from setuptools.command.install import install 
# # import os 
# # import sys 
# # import subprocess



# # class CustomInstallCommand(install):
# #     ''' Custom Installation command that adds dist to PATH'''

# #     def run(self):
# #         install.run(self)

# #         if sys.platform == 'win32':
# #             try:
# #                 project_root = os.path.dirname(os.path.abspath(__file__))
# #                 dist_path = os.path.join(project_root,'dist')
# #                 if os.path.exists(dist_path):
# #                     cmd = f'setx PATH "%PATH%;{dist_path}"'
# #                     result = subprocess.run(cmd,shell=True,capture_output=True,text=True)
# #                     if result.returncode == 0:
# #                         print(f"Successfully added path")
# #                     else:
# #                         print(f"Failed to add path { result.stderr}")
# #                 else:
# #                     print(f"Dist direcotry {dist_path}")
# #             except Exception as e:
# #                 print(f" Error Modifying path:{e}")
    

# # setup(
# #     name="gitagent",
# #     version='0.1.0',
# #     packages=find_packages(where='src'),
# #     package_dir={'':'src'},
# #     include_package_data=True,
# #     install_requires=['Click'],
# #     entry_points={
# #         'console_scripts':['voicegit=cli:cli',],
# #     },
# #     cmdclass={
# #         'install':CustomInstallCommand
# #     },
# #     author="Hemanth Challapalli",
# #     description="Voice Controlled Git CLI Tool",
# #     python_requires=">=3.7"
# #     )

# from setuptools import setup, find_packages
# from setuptools.command.install import install
# from setuptools.command.develop import develop
# import os 
# import sys 
# import subprocess

# def add_to_path():
#     """Add dist directory to PATH"""
#     if sys.platform == 'win32':
#         try:
#             project_root = os.path.dirname(os.path.abspath(__file__))
#             dist_path = os.path.join(project_root, 'dist')
#             if os.path.exists(dist_path):
#                 cmd = f'setx PATH "%PATH%;{dist_path}"'
#                 result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#                 if result.returncode == 0:
#                     print(f"✅ Successfully added {dist_path} to PATH")
#                     print("⚠️  Please restart your command prompt for changes to take effect")
#                 else:
#                     print(f"❌ Failed to add path: {result.stderr}")
#             else:
#                 print(f"⚠️  Dist directory not found: {dist_path}")
#         except Exception as e:
#             print(f"❌ Error modifying path: {e}")

# class CustomInstallCommand(install):
#     """Custom Installation command that adds dist to PATH"""
#     def run(self):
#         install.run(self)
#         add_to_path()

# class CustomDevelopCommand(develop):
#     """Custom Development command that adds dist to PATH"""
#     def run(self):
#         develop.run(self)
#         add_to_path()

# setup(
#     name="gitagent",
#     version='0.1.0',
#     packages=find_packages(where='src'),
#     package_dir={'':'src'},
#     include_package_data=True,
#     install_requires=['Click'],
#     entry_points={
#         'console_scripts':['voicegit=cli:cli',],
#     },
#     cmdclass={
#         'install': CustomInstallCommand,
#         'develop': CustomDevelopCommand,  # This handles 'pip install -e .'
#     },
#     author="Hemanth Challapalli",
#     description="Voice Controlled Git CLI Tool",
#     python_requires=">=3.7"
# )

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os 
import sys 
import subprocess

def add_to_path():
    """Add dist directory to PATH"""
    print("🔧 Attempting to add to Windows PATH...")
    if sys.platform == 'win32':
        try:
            # Use sys.argv[0] to get the script path when __file__ might not be available
            if '__file__' in globals():
                script_path = __file__
            else:
                script_path = sys.argv[0] if sys.argv else os.getcwd()
            
            project_root = os.path.dirname(os.path.abspath(script_path))
            dist_path = os.path.join(project_root, 'dist')
            print(f"Looking for executable at: {dist_path}")
            
            if os.path.exists(dist_path):
                # Check if already in PATH
                current_path = os.environ.get('PATH', '')
                if dist_path not in current_path:
                    cmd = f'setx PATH "%PATH%;{dist_path}"'
                    print(f"Running: {cmd}")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ Successfully added {dist_path} to PATH")
                        print("⚠️  Please restart your command prompt for changes to take effect")
                    else:
                        print(f"❌ Failed to add path: {result.stderr}")
                else:
                    print(f"✅ {dist_path} already in PATH")
            else:
                print(f"⚠️  Dist directory not found: {dist_path}")
                print("   Run 'pyinstaller --onefile src/cli.py --name voicegit' first")
        except Exception as e:
            print(f"❌ Error modifying path: {e}")

class CustomInstallCommand(install):
    """Custom Installation command that adds dist to PATH"""
    def run(self):
        print("🚀 Running custom install...")
        install.run(self)
        add_to_path()

class CustomDevelopCommand(develop):
    """Custom Development command that adds dist to PATH"""
    def run(self):
        print("🚀 Running custom develop...")
        develop.run(self)
        add_to_path()

setup(
    name="gitagent",
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'':'src'},
    include_package_data=True,
    install_requires=['Click'],
    entry_points={
        'console_scripts':['voicegit=cli:cli',],
    },
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    },
    author="Hemanth Challapalli",
    description="Voice Controlled Git CLI Tool",
    python_requires=">=3.7"
)

# Force execution when setup.py is run directly
if __name__ == "__main__" and len(sys.argv) > 1:
    if any(arg in sys.argv for arg in ['install', 'develop']):
        add_to_path()