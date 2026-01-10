import osmium
import json

class SimpleTrailHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.trails = []
        self.ways = {}
        
    def way(self, w):
        # Store ways with coordinates
        tags = {tag.k: tag.v for tag in w.tags}
        coords = [(node.lon, node.lat) for node in w.nodes]  # GeoJSON uses lon, lat
        self.ways[w.id] = {
            'coords': coords,
            'tags': tags
        }
    
    def relation(self, r):
        tags = {tag.k: tag.v for tag in r.tags}
        
        # Only hiking routes
        if tags.get('type') == 'route' and tags.get('route') in ['hiking', 'foot']:
            trail = {
                'name': tags.get('name', 'Unnamed Trail'),
                'member_ways': [m.ref for m in r.members if m.type == 'w']
            }
            self.trails.append(trail)

def extract_trails(pbf_file='socal-latest.osm.pbf'):
    print("Reading Southern California OSM data...")
    handler = SimpleTrailHandler()
    handler.apply_file(pbf_file, locations=True)
    
    print(f"Found {len(handler.trails)} hiking trails")
    
    # Build trail geometries
    features = []
    for trail in handler.trails:
        all_coords = []
        
        # Collect coordinates from member ways
        for way_id in trail['member_ways']:
            if way_id in handler.ways:
                all_coords.extend(handler.ways[way_id]['coords'])
        
        if len(all_coords) > 1:  # Need at least 2 points for a line
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': all_coords
                },
                'properties': {
                    'name': trail['name']
                }
            })
    
    return features

def save_geojson(features, filename='socal_trails.geojson'):
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"Saved {len(features)} trails to {filename}")
    print(f"\nView it at: http://geojson.io")

if __name__ == "__main__":
    features = extract_trails('socal-latest.osm.pbf')
    save_geojson(features)
    
    # Show sample trail names
    print("\nSample trails found:")
    for feature in features[:10]:
        print(f"  - {feature['properties']['name']}")