from plexapi.server import PlexServer
import os
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
PLEX_URL = os.getenv("PLEX_URL")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")

def get_library_items(library_key, server_url=PLEX_URL, token=PLEX_TOKEN):
    """
    Get all items from a Plex library by library key/ID.
    
    Args:
        library_key (str or int): The library key/ID (e.g., "1", "2", "3")
        server_url (str): Plex server URL
        token (str): Plex access token
    
    Returns:
        List of library items
    """
    # Connect to Plex server
    plex = PlexServer(server_url, token)
    
    # Get the library by key
    library = plex.library.sectionByID(library_key)
    
    # Get all items in the library
    items = library.all()
    
    return items

def get_library_by_name(library_name, server_url=PLEX_URL, token=PLEX_TOKEN):
    """
    Get library items by library name instead of key.
    
    Args:
        library_name (str): Name of the library (e.g., "Movies", "TV Shows")
        server_url (str): Plex server URL  
        token (str): Plex access token
    """
    plex = PlexServer(server_url, token)
    library = plex.library.section(library_name)
    return library.all()

def list_all_libraries(server_url=PLEX_URL, token=PLEX_TOKEN):
    """
    List all available libraries.
    
    Returns:
        List of library sections with their keys and names
    """
    plex = PlexServer(server_url, token)
    libraries = []
    
    for section in plex.library.sections():
        libraries.append({
            'key': section.key,
            'title': section.title,
            'type': section.type,
            'agent': section.agent,
            'total_items': len(section.all()) if hasattr(section, 'all') else 'Unknown'
        })
    
    return libraries

def get_recently_added(library_key, count=50, server_url=PLEX_URL, token=PLEX_TOKEN):
    """
    Get recently added items from a library.
    
    Args:
        library_key (str or int): Library key
        count (int): Number of items to return
    """
    plex = PlexServer(server_url, token)
    library = plex.library.sectionByID(library_key)
    return library.recentlyAdded(maxresults=count)

def search_library(library_key, query, server_url=PLEX_URL, token=PLEX_TOKEN):
    """
    Search within a specific library.
    
    Args:
        library_key (str or int): Library key
        query (str): Search query
    """
    plex = PlexServer(server_url, token)
    library = plex.library.sectionByID(library_key)
    return library.search(query)

def export_all_libraries_to_csv(filename=None, server_url=PLEX_URL, token=PLEX_TOKEN):
    """
    Export all items from all Plex libraries to a CSV file.
    
    Args:
        filename (str): Output CSV filename. If None, uses timestamp.
        server_url (str): Plex server URL
        token (str): Plex access token
    
    Returns:
        str: Path to the created CSV file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plex_library_export_{timestamp}.csv"
    
    # Get all libraries
    libraries = list_all_libraries(server_url, token)
    
    # Define CSV columns
    fieldnames = [
        'library_key',
        'library_name',
        'library_type',
        'title',
        'type',
        'year',
        'rating_key',
        'duration_minutes',
        'file_size_mb',
        'added_at',
        'updated_at',
        'view_count',
        'summary',
        'genres',
        'directors',
        'actors',
        'studio',
        'content_rating',
        'rating',
        'guid'
    ]
    
    total_items = 0
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for library in libraries:
            print(f"Processing library: {library['title']} (Key: {library['key']})")
            
            try:
                items = get_library_items(library['key'], server_url, token)
                library_items = 0
                
                for item in items:
                    try:
                        # Extract item data with safe attribute access
                        row_data = {
                            'library_key': library['key'],
                            'library_name': library['title'],
                            'library_type': library['type'],
                            'title': getattr(item, 'title', ''),
                            'type': getattr(item, 'type', ''),
                            'year': getattr(item, 'year', ''),
                            'rating_key': getattr(item, 'ratingKey', ''),
                            'duration_minutes': getattr(item, 'duration', 0) // (1000 * 60) if getattr(item, 'duration', None) else '',
                            'file_size_mb': '',  # Will be calculated below
                            'added_at': getattr(item, 'addedAt', ''),
                            'updated_at': getattr(item, 'updatedAt', ''),
                            'view_count': getattr(item, 'viewCount', 0),
                            'summary': getattr(item, 'summary', '').replace('\n', ' ').replace('\r', '') if getattr(item, 'summary', None) else '',
                            'genres': ', '.join([genre.tag for genre in getattr(item, 'genres', [])]),
                            'directors': ', '.join([director.tag for director in getattr(item, 'directors', [])]),
                            'actors': ', '.join([actor.tag for actor in getattr(item, 'roles', [])][:5]),  # Limit to first 5 actors
                            'studio': getattr(item, 'studio', ''),
                            'content_rating': getattr(item, 'contentRating', ''),
                            'rating': getattr(item, 'rating', ''),
                            'guid': getattr(item, 'guid', '')
                        }
                        
                        # Calculate total file size for the item
                        try:
                            if hasattr(item, 'media') and item.media:
                                total_size = sum(
                                    part.size for media in item.media 
                                    for part in media.parts 
                                    if hasattr(part, 'size') and part.size
                                )
                                row_data['file_size_mb'] = round(total_size / (1024 * 1024), 2) if total_size else ''
                        except Exception as e:
                            # If file size calculation fails, leave it empty
                            pass
                        
                        writer.writerow(row_data)
                        library_items += 1
                        total_items += 1
                        
                        # Progress indicator
                        if library_items % 100 == 0:
                            print(f"  Processed {library_items} items from {library['title']}")
                    
                    except Exception as e:
                        print(f"  Error processing item '{getattr(item, 'title', 'Unknown')}': {e}")
                        continue
                
                print(f"  Completed: {library_items} items from {library['title']}")
            
            except Exception as e:
                print(f"  Error processing library {library['title']}: {e}")
                continue
    
    print(f"\nExport completed!")
    print(f"Total items exported: {total_items}")
    print(f"CSV file saved as: {filename}")
    
    return filename

def print_library_items(items, max_items=10):
    """
    Print library items in a readable format.
    
    Args:
        items: List of Plex media items
        max_items (int): Maximum number of items to print
    """
    print(f"Found {len(items)} items:")
    print("-" * 60)
    
    for i, item in enumerate(items[:max_items]):
        print(f"{i+1}. {item.title}")
        print(f"   Type: {item.type}")
        if hasattr(item, 'year') and item.year:
            print(f"   Year: {item.year}")
        if hasattr(item, 'duration') and item.duration:
            duration_min = item.duration // (1000 * 60)  # Convert ms to minutes
            print(f"   Duration: {duration_min} minutes")
        print(f"   Rating Key: {item.ratingKey}")
        if hasattr(item, 'summary') and item.summary:
            print(f"   Summary: {item.summary[:100]}...")
        print()
    
    if len(items) > max_items:
        print(f"... and {len(items) - max_items} more items")

# Example usage functions
def main():
    """
    Main function - exports all libraries to CSV
    """
    print("=== Plex Library CSV Exporter ===\n")
    
    try:
        # List all libraries first
        print("Available libraries:")
        libraries = list_all_libraries()
        for lib in libraries:
            print(f"  Key: {lib['key']} - '{lib['title']}' ({lib['type']}) - {lib['total_items']} items")
        
        if not libraries:
            print("No libraries found. Check your connection and token.")
            return
        
        print("\n" + "="*60 + "\n")
        
        # Export all libraries to CSV
        csv_filename = export_all_libraries_to_csv()
        
        print(f"\nCSV export saved to: {csv_filename}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your PLEX_URL and PLEX_TOKEN environment variables are set correctly")

if __name__ == "__main__":
    main()