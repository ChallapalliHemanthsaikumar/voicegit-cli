import os
import sys
import click

# Add current executable directory to PATH if not already there
def ensure_in_path():
    if getattr(sys, 'frozen', False):  # Running as PyInstaller executable
        exe_dir = os.path.dirname(sys.executable)
    else:  # Running as Python script
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    current_path = os.environ.get('PATH', '')
    if exe_dir not in current_path:
        os.environ['PATH'] = f"{exe_dir};{current_path}"

# Call this at the start of your CLI
ensure_in_path()

@click.command()
def cli():
    """Voice Git CLI is working"""
    click.echo("Voice Git CLI is working")

if __name__ == '__main__':
    cli()