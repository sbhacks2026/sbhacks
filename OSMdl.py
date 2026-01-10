# Open Street Map (OSM) trail data download
## Includes geographic coordinated to preserve visual interface
## Calculates trail distance with the provided coordinates

import osmium
import json
from geopy.distance import geodesic
from collections import defaultdict

class HikingTrailHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.trails = []
        self.ways = {}  # Store ways for later lookup
        
    def way(self, w):
        # Store all ways that might be part of hiking trails
        tags = {tag.k: tag.v for tag in w.tags}
        if 'highway' in tags or 'route' in tags:
            coords = [(node.lat, node.lon) for node in w.nodes]
            self.ways[w.id] = {
                'coords': coords,
                'tags': tags
            }
    
    def relation(self, r):
        # Only process hiking route relations
        tags = {tag.k: tag.v for tag in r.tags}
        
        if tags.get('type') == 'route' and tags.get('route') in ['hiking', 'foot']:
            trail = {
                'id': r.id,
                'name': tags.get('name', 'Unnamed Trail'),
                'distance': tags.get('distance', ''),
                'operator': tags.get('operator', ''),
                'description': tags.get('description', ''),
                'sac_scale': tags.get('sac_scale', 'unknown'),
                'surface': tags.get('surface', 'unknown'),
                'coordinates': [],
                'member_ways': []
            }
            
            # Collect member ways
            for member in r.members:
                if member.type == 'w':  # way
                    trail['member_ways'].append(member.ref)
            
            self.trails.append(trail)

def process_trails_efficient(pbf_file='california-latest.osm.pbf'):
    """More efficient processing focusing on hiking route relations"""
    
    print("Pass 1: Reading ways and relations...")
    handler = HikingTrailHandler()
    handler.apply_file(pbf_file, locations=True)
    
    print(f"Found {len(handler.trails)} hiking route relations")
    print(f"Loaded {len(handler.ways)} ways")
    
    # Build complete trails from member ways
    print("\nPass 2: Building trail geometries...")
    complete_trails = []
    
    for trail in handler.trails:
        all_coords = []
        
        # Collect coordinates from all member ways
        for way_id in trail['member_ways']:
            if way_id in handler.ways:
                way_coords = handler.ways[way_id]['coords']
                all_coords.extend(way_coords)
        
        if all_coords:
            trail['coordinates'] = all_coords
            
            # Calculate distance
            distance_km = 0
            for i in range(len(all_coords) - 1):
                distance_km += geodesic(all_coords[i], all_coords[i+1]).kilometers
            
            trail['distance_km'] = distance_km
            trail['distance_miles'] = distance_km * 0.621371
            
            # Remove member_ways from final output
            del trail['member_ways']
            
            complete_trails.append(trail)
    
    return complete_trails

def save_geojson(trails, filename='california_hiking_trails.geojson'):
    """Save to GeoJSON"""
    features = []
    
    for trail in trails:
        if trail['coordinates']:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[lon, lat] for lat, lon in trail['coordinates']]
                },
                'properties': {
                    'name': trail['name'],
                    'distance_km': round(trail['distance_km'], 2),
                    'distance_miles': round(trail['distance_miles'], 2),
                    'difficulty': trail['sac_scale'],
                    'surface': trail['surface'],
                    'operator': trail['operator'],
                    'description': trail['description'],
                    'osm_id': trail['id']
                }
            }
            features.append(feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"\nSaved {len(features)} trails to {filename}")
    return len(features)

def main():
    print("Processing California OSM data for hiking trails...")
    print("This will take 2-5 minutes...\n")
    
    # Process the file
    trails = process_trails_efficient('california-latest.osm.pbf')
    
    print(f"\nFound {len(trails)} complete hiking trails")
    
    # Save to GeoJSON
    count = save_geojson(trails)
    
    # Statistics
    if trails:
        total_miles = sum(t['distance_miles'] for t in trails)
        avg_miles = total_miles / len(trails)
        
        print(f"\n=== Statistics ===")
        print(f"Total trails: {len(trails)}")
        print(f"Total distance: {total_miles:.1f} miles")
        print(f"Average trail: {avg_miles:.1f} miles")
        
        # Show longest trails
        print("\nTop 10 longest trails:")
        sorted_trails = sorted(trails, key=lambda x: x['distance_miles'], reverse=True)
        for trail in sorted_trails[:10]:
            print(f"  {trail['name']}: {trail['distance_miles']:.1f} miles")

if __name__ == "__main__":
    main()