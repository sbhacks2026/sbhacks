import sys
try:
    from ddgs import DDGS
except ImportError:
    print("Error: ddgs not installed. Run: pip install ddgs", file=sys.stderr)
    #sys.exit(1)

if len(sys.argv) > 1:
    trail_name = sys.argv[1]
    query = f"site:alltrails.com {trail_name}"

    # The usage remains mostly the same, just the import changed
    with DDGS() as ddgs:
        # max_results controls how many links you get back
        results = ddgs.text(query, max_results=1)
        
        for result in results:
            print(result['href'])