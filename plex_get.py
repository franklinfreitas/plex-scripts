import os

import click
from plexapi.server import PlexServer

from dotenv import load_dotenv
from terminaltables import AsciiTable

load_dotenv()

# Configuration
PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")


class PlexService:
    __plex = None

    def __init__(self):
        server_url = PLEX_URL
        access_token = PLEX_TOKEN
        self.__plex = PlexServer(server_url, access_token)

    def get_libraries(self):
        libraries = []

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
        Get library items by library key/ID.

        Args:
            library_key (str or int): Library key/ID (e.g., "1", "2", "3")
        """
        library_items_list = []
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
        Get library items by library name instead of key.

        Args:
            library_name (str): Name of the library (e.g., "Movies", "TV Shows")
        """
        library_items_list = []
        library = self.__plex.library.section(library_name)
        library_items = library.all()
        for item in library_items:
            item_dict = {
                "title": item.title,
                "year": item.year
            }
            library_items_list.append(item_dict)

        return library_items_list

    def print_libraries_00(self):
        libraries = self.get_libraries()
        for library in libraries:
            print(library)

    def print_libraries(self):
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

        # Create and print the table
        table = AsciiTable(table_data)
        table.title = 'Plex Libraries'

        # Optional: Set column alignment
        table.justify_columns[0] = 'center'  # Key column centered
        table.justify_columns[3] = 'right'  # Total items right-aligned

        print(table.table)

    def print_library_items_00(self, library_name):
        items = self.get_library_items_by_name(library_name)
        for item in items:
            print(item)

    def print_library_items_by_key(self, library_key):
        items = self.get_library_items_by_key(library_key)
        self.print_library_items(items)

    def print_library_items_by_name(self, library_name):
        items = self.get_library_items_by_name(library_name)
        self.print_library_items(items)

    def print_library_items(self, items: list[dict]):
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

        # Create and print the table
        table = AsciiTable(table_data)
        table.title = "Library Items"

        # Optional: Set column alignment
        table.justify_columns[0] = 'center'  # Index column centered
        table.justify_columns[2] = 'center'  # Year column centered

        # Set max width for title column to handle long titles
        if len(table_data) > 1:  # Check if we have data beyond header
            table.inner_column_border = True
            table.outer_border = True

        print(table.table)
        print(f"\nTotal items: {len(items)}")


@click.group()
def cli():
    pass


@cli.command("libraries")
def libraries():
    """
    List all available libraries.

    Returns:
        List of library sections with their keys and names
    """
    PlexService().print_libraries()


@cli.command("items")
@click.option("-k", "--library-key", type=int, help="Key/ID of the library (e.g., 1, 2, 3)")
@click.option("-n", "--library-name", type=str, help="Name of the library (e.g., 'Movies', 'TV Shows')")
def items(library_key, library_name):
    """
    Print library items by library name instead of key.

    Args:
        library_key (int) Key of the library (e.g., 1, 2, 3)
        library_name (str): Name of the library (e.g., "Movies", "TV Shows")
    """
    if not library_name and not library_key:
        click.echo("Error: You must specify either --library-name (-n) or --library-key (-k)")
        click.echo("Use 'python script.py items --help' for more information")
        return

    if library_name and library_key:
        click.echo("Error: Please specify either --library-name (-n) OR --library-key (-k), not both")
        return

    if library_key:
        PlexService().print_library_items_by_key(library_key=library_key)
    elif library_name:
        PlexService().print_library_items_by_name(library_name=library_name)


if __name__ == "__main__":
    cli()
