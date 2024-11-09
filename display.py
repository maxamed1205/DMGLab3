from neo4j import GraphDatabase
import folium

# Fonction pour afficher une ville sur la carte
def display_city_on_map(m, popup, latitude, longitude, radius=1000, color="#3186cc"):
    folium.Circle(
        location=(latitude, longitude),
        radius=radius,
        popup=popup,
        color=color,
        fill=True,
        fill_opacity=0.8,
    ).add_to(m)

# Fonction pour afficher une ligne entre deux villes
def display_polyline_on_map(m, locations, popup=None, color="#3186cc", weight=2.0):
    folium.PolyLine(
        locations,
        popup=popup,
        color=color,
        weight=weight,
        opacity=1
    ).add_to(m)

class DisplayTrainNetwork:
    def __init__(self, uri):
        self.driver = GraphDatabase.driver(uri)

    def close(self):
        self.driver.close()

    def fetch_cities_and_routes(self):
        cities = []
        routes = []

        with self.driver.session() as session:
            # Récupérer les villes
            result_cities = session.run("MATCH (c:City) RETURN c.name AS name, c.latitude AS latitude, c.longitude AS longitude")
            for record in result_cities:
                cities.append({
                    "name": record["name"],
                    "latitude": record["latitude"],
                    "longitude": record["longitude"]
                })

            # Récupérer les routes entre villes
            result_routes = session.run("MATCH (c1:City)-[r:LINE]->(c2:City) RETURN c1, c2, r")
            for record in result_routes:
                c1, c2, rel = record["c1"], record["c2"], record["r"]
                routes.append({
                    "city1": c1["name"],
                    "city2": c2["name"],
                    "distance": rel["km"],
                    "locations": [(c1["latitude"], c1["longitude"]), (c2["latitude"], c2["longitude"])]
                })
        return cities, routes

    def display_network(self):
        # Centrer la carte sur la Suisse
        map_object = folium.Map(location=[46.800663464, 8.222665776], zoom_start=8)

        # Récupérer les villes et routes
        cities, routes = self.fetch_cities_and_routes()

        # Afficher les villes
        for city in cities:
            display_city_on_map(
                m=map_object,
                popup=city["name"],
                latitude=city["latitude"],
                longitude=city["longitude"],
                color="#3186cc"
            )

        # Afficher les routes
        for route in routes:
            display_polyline_on_map(
                m=map_object,
                locations=route["locations"],
                popup=f"{route['city1']} - {route['city2']}, Distance: {route['distance']} km",
                color="#3186cc"
            )

        # Sauvegarder la carte
        map_object.save("out/network_map.html")
        print("Carte du réseau enregistrée sous 'out/network_map.html'")

if __name__ == "__main__":
    display_train_network = DisplayTrainNetwork("neo4j://localhost:7687")

    # Afficher le réseau de trains
    display_train_network.display_network()
