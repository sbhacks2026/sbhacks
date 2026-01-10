import sys
import json

# Get activities data from Node.js (NOT a token!)
if len(sys.argv) > 1:
    activities_json = sys.argv[1]
    try:
        activities = json.loads(activities_json)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid activities data"}))
        sys.exit(1)
else:
    print(json.dumps({"error": "No activities data provided"}))
    sys.exit(1)

# Filter to backpacking-related activities
target_sports = {"Run", "Hike", "TrailRun", "Walk"}

filtered_activities = []
for activity in activities:
    if isinstance(activity, dict) and activity.get("sport_type") in target_sports:
        filtered_activities.append({
            "name": activity.get("name"),
            "type": activity.get("sport_type"),
            "distance": activity.get("distance"),
            "elevation_gain": activity.get("total_elevation_gain"),
            "moving_time": activity.get("moving_time"),
            "start_date": activity.get("start_date")
        })

# Return result
result = {
    "status": "success",
    "message": "Analyzed backpacking activities",
    "total_activities": len(filtered_activities),
    "activities": filtered_activities
}

print(json.dumps(result))