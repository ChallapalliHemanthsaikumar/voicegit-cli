import os
from pathlib import Path
import sys
import click
import subprocess
from main import config ,greet,interactive



@click.group()
def cli():
    "Voice Git CLI "
    pass

@cli.command()
def status():
    try:
        result = subprocess.run(['git','status'],capture_output=True,text=True)
        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"Error {result.stderr}")

    except Exception as e:
        click.echo(f"Error :{result.stderr} ",err=True)


@cli.command()
def author():
    try:
        click.echo("Author is Hemanth Chowdary")
    except Exception as e:
        print("Error Getting Author Name ")


@cli.command()
def diff():
    try:
        result = subprocess.run(['git','diff'],capture_output=True,text=True)
        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"Error {result.stderr}")

    except Exception as e:
        click.echo(f"Error :{result.stderr} ",err=True)

@cli.command()
@click.option('--name', prompt='Your name', help='Your full name')
@click.option('--email', prompt='Your email', help='Your email address')
def configure(name, email):
    """Configure user name and email for VoiceGit"""
    try:
        # Call the config function from main.py
        result = config(name, email)
        
        if result:
            click.echo(f"✅ Configuration saved successfully!")
            click.echo(f"👤 Name: {name}")
            click.echo(f"📧 Email: {email}")
        else:
            click.echo("❌ Failed to save configuration", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error configuring user: {e}", err=True)

@cli.command()
def greeter():
    """Greet user with personalized message"""
    try:
        greeting = greet()
        click.echo(greeting)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

# Add this debug command to your CLI
@cli.command()
def debug():
    """Debug configuration paths"""
    print("add code to debug")

@cli.command()
def chat():
    """Start interactive chat with the assistant"""
    try:
        import asyncio
        from main import interactive
        asyncio.run(interactive())
    except Exception as e:
        click.echo(f"❌ Error starting chat: {e}", err=True)