import click
from .database import init_db, check_tables_exist

@click.group()
def cli():
    """Database management commands"""
    pass

@cli.command()
def init():
    """Initialize database tables"""
    if check_tables_exist():
        click.echo("Database tables already exist")
        return
    
    init_db()
    click.echo("Database initialized successfully")

@cli.command()
def check():
    """Check if database tables exist"""
    if check_tables_exist():
        click.echo("Database tables exist")
    else:
        click.echo("Database tables do not exist")

if __name__ == '__main__':
    cli() 