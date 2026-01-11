from serpapi import GoogleSearch
import sys
import json

def search_trail(trail_name, location=""):
    """
    Search for a trail on Google and return the first AllTrails link.

    Args:
        trail_name: The name of the trail to search for
        location: Optional location context

    Returns:
        JSON string with the first organic result link
    """
    # Build search query
    search_query = f"{trail_name} AllTrails"
    if location:
        search_query += f" {location}"

    params = {
        "engine": "google",
        "q": search_query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": "975824a675b71dc0d0aeda8a04d37166df2d746599a3cd2fd96b767002400435"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Get the first link from organic search results
    if 'organic_results' in results and len(results['organic_results']) > 0:
        first_result = results['organic_results'][0]
        if 'link' in first_result:
            return json.dumps({
                "success": True,
                "link": first_result['link'],
                "title": first_result.get('title', ''),
                "snippet": first_result.get('snippet', '')
            })

    return json.dumps({
        "success": False,
        "error": "No results found"
    })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Trail name required"}))
        sys.exit(1)

    trail_name = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else ""

    print(search_trail(trail_name, location))
