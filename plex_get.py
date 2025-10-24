"""
plex_get.py

Command-line tool to interact with your Plex Media Server. 
Allows you to list all libraries and display the media items for a specific library by name or key.

Usage:
    python plex_get.py libraries
    python plex_get.py items --library-name "Movies"
    python plex_get.py items --library-key 1

Requirements:
    - Python 3.7+
    - plexapi
    - click
    - python-dotenv
    - terminaltables
    - .env file with PLEX_URL and PLEX_TOKEN set to your Plex server's details
"""

import os

import click
from plexapi.server import PlexServer

from dotenv import load_dotenv
from terminaltables import AsciiTable

load_dotenv()

# Read Plex server configuration from environment variables
PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")


class PlexService:
    """
    Service class to encapsulate PlexServer interaction and provide 
    methods for retrieving and displaying Plex libraries and their items.
    """
    __plex = None

    def __init__(self):
        """
        Initializes the PlexService by connecting to the Plex server using credentials from environment variables.
        """
        server_url = PLEX_URL
        access_token = PLEX_TOKEN
        self.__plex = PlexServer(server_url, access_token)

    def get_libraries(self):
        """
        Fetch all available libraries from the Plex server.

        Returns:
            list[dict]: List of libraries with metadata (key, title, type, total_items).
        """
        libraries = []

        # Iterate all sections (libraries) on the Plex server
        for section in self.__plex.library.sections():
            section_dict = {
                'key': section.key,
                'title': section.title,
                'type': section.type,
                'total_items': len(section.all()) if hasattr(section, 'all') else 'Unknown'
            }
            libraries.append(section_dict)

        return libraries

    def get_library_items_by_key(self, library_key):
        """
        Fetch all items from a library by its key/ID.

        Args:
            library_key (str or int): Library key/ID (e.g., "1", "2", "3")

        Returns:
            list[dict]: List of media items with 'title' and 'year'.
        """
        library_items_list = []
        # Get library section by ID then fetch all items
        library = self.__plex.library.sectionByID(library_key)
        library_items = library.all()
        for item in library_items:
            item_dict = {
                "title": item.title,
                "year": item.year if hasattr(item, 'year') and item.year else 'N/A'
            }
            library_items_list.append(item_dict)

        return library_items_list

    def get_library_items_by_name(self, library_name):
        """
        Fetch all items from a library by its name.

        Args:
            library_name (str): Name of the library (e.g., "Movies", "TV Shows")

        Returns:
            list[dict]: List of media items with 'title' and 'year'.
        """
        library_items_list = []
        library = self.__plex.library.section(library_name)
        library_items = library.all()
        for item in library_items:
            item_dict = {
                "title": item.title,
                "year": item.year if hasattr(item, 'year') and item.year else 'N/A'
            }
            library_items_list.append(item_dict)

        return library_items_list

    def print_libraries_00(self):
        """
        Debug utility: print raw library dictionaries (not formatted as table).
        """
        libraries = self.get_libraries()
        for library in libraries:
            print(library)

    def print_libraries(self):
        """
        Print all Plex libraries in a formatted ASCII table.
        """
        libraries = self.get_libraries()

        # Prepare table data
        table_data = [
            ['Key', 'Title', 'Type', 'Total Items']  # Header row
        ]

        for library in libraries:
            table_data.append([
                str(library['key']),
                library['title'],
                library['type'],
                str(library['total_items'])
            ])

        # Create and print the table (styled for readability)
        table = AsciiTable(table_data)
        table.title = 'Plex Libraries'

        # Set column alignment for improved display
        table.justify_columns[0] = 'center'  # Key column centered
        table.justify_columns[3] = 'right'   # Total items right-aligned

        print(table.table)

    def print_library_items_00(self, library_name):
        """
        Debug utility: print media items as raw dictionaries (not formatted as table).
        """
        items = self.get_library_items_by_name(library_name)
        for item in items:
            print(item)

    def print_library_items_by_key(self, library_key):
        """
        Print items from a library specified by key, as a formatted table.

        Args:
            library_key (str or int): Key/ID of library.
        """
        items = self.get_library_items_by_key(library_key)
        self.print_library_items(items)

    def print_library_items_by_name(self, library_name):
        """
        Print items from a library specified by name, as a formatted table.

        Args:
            library_name (str): Name of the library.
        """
        items = self.get_library_items_by_name(library_name)
        self.print_library_items(items)

    def print_library_items(self, items: list[dict]):
        """
        Given a list of items (dicts with 'title' and 'year'), print them in an ASCII table.

        Args:
            items (list[dict]): List of media item dictionaries.
        """
        # Prepare table data
        table_data = [
            ['#', 'Title', 'Year']  # Header row
        ]

        for index, item in enumerate(items, 1):
            table_data.append([
                str(index),
                item['title'],
                str(item['year'])
            ])

        # Create table and set display properties
        table = AsciiTable(table_data)
        table.title = "Library Items"

        table.justify_columns[0] = 'center'  # Index column centered
        table.justify_columns[2] = 'center'  # Year column centered

        if len(table_data) > 1:
            table.inner_column_border = True
            table.outer_border = True

        print(table.table)
        print(f"\nTotal items: {len(items)}")


@click.group()
def cli():
    """Main entry point: defines the CLI group."""
    pass


@cli.command("libraries")
def libraries():
    """
    CLI command to list all available libraries.

    Usage:
        python plex_get.py libraries
    """
    PlexService().print_libraries()


@cli.command("items")
@click.option("-k", "--library-key", type=int, help="Key/ID of the library (e.g., 1, 2, 3)")
@click.option("-n", "--library-name", type=str, help="Name of the library (e.g., 'Movies', 'TV Shows')")
def items(library_key, library_name):
    """
    CLI command to print library items by name or key.

    Usage:
        python plex_get.py items --library-name "TV Shows"
        python plex_get.py items --library-key 3

    Args:
        library_key (int): Key of the library (e.g., 1, 2, 3)
        library_name (str): Name of the library (e.g., "Movies", "TV Shows")
    """
    # Ensure the user does not provide both or neither key/name
    if not library_name and not library_key:
        click.echo("Error: You must specify either --library-name (-n) or --library-key (-k)")
        click.echo("Use 'python plex_get.py items --help' for more information")
        return

    if library_name and library_key:
        click.echo("Error: Please specify either --library-name (-n) OR --library-key (-k), not both")
        return

    # Query by key or name and display items
    if library_key:
        PlexService().print_library_items_by_key(library_key=library_key)
    elif library_name:
        PlexService().print_library_items_by_name(library_name=library_name)


if __name__ == "__main__":
    cli()
