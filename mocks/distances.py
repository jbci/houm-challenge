from geopy.distance import distance
from django.contrib.gis.geos import Point

origin_dict = {"lng": -70.5446686230096, "lat": -33.38480466907792}
origin_point = Point(origin_dict['lng'], origin_dict['lat'])
for i in range(0, 10, 1):
    dest_dict = {"lng": -70.5446686230096 + (0.01 * i), "lat": -33.38480466907792+ (0.01 * i)}
    current_point = Point((dest_dict["lng"], dest_dict["lat"]))
    print(f"i: {i} lat: {dest_dict['lat']} lng: {dest_dict['lng']}")
    print(f"distance: {distance(origin_point, current_point).km} km")