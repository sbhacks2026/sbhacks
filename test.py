from serpapi import GoogleSearch

params = {
  "engine": "google",
  "q": "Seven Falls Hike All Trails Santa Barbara",
  "location": "Los Angeles, California, United States",
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
        print(first_result['link'])
    else:
        print("No link found in first result")
else:
    print("No organic results found")


