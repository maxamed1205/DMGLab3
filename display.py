from neo4j import GraphDatabase
import folium


# display city on the folium map
def display_city_on_map(m, popup, latitude, longitude, radius=1000, color="#3186cc"):
    folium.Circle(
        location=(latitude, longitude),
        radius=radius,
        popup=popup,
        color=color,
        fill=True,
        fill_opacity=0.8,
    ).add_to(m)


# display polyline on the folium map
# locations: (list of points (latitude, longitude)) – Latitude and Longitude of line
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

            # Récupérer les relations entre villes (routes)
            result_routes = session.run("""
                MATCH (c1:City)-[r:LINE]->(c2:City)
                RETURN c1.name AS city1, c2.name AS city2, r.km AS distance
            """)
            for record in result_routes:
                routes.append({
                    "city1": record["city1"],
                    "city2": record["city2"],
                    "distance": record["distance"]
                })

        return cities, routes


    def display_cities(self):
        map_1 = folium.Map(location=center_switzerland, zoom_start=8)
        with self.driver.session() as session:
            session.read_transaction(self._display_cities, map_1)
        map_1.save('out/1.html')

    @staticmethod
    def _display_cities(tx, m):
        query = (
            """
            MATCH (c:City)
            RETURN c
            """
        )
        result = tx.run(query)
        for record in result:
            display_city_on_map(
                m=m,
                popup=record['c']['name'],
                latitude=record['c']['latitude'],
                longitude=record['c']['longitude']
            )
    def display_routes(self, routes, cities):
        # Initialiser la carte centrée sur la Suisse
        map_object = folium.Map(location=[46.800663464, 8.222665776], zoom_start=8)

        for route in routes:
            # Trouver les coordonnées des villes
            city1 = next((city for city in cities if city["name"] == route["city1"]), None)
            city2 = next((city for city in cities if city["name"] == route["city2"]), None)

            if city1 and city2:  # Vérifier que les deux villes existent
                # Ajouter une ligne entre les deux villes
                folium.PolyLine(
                    locations=[(city1["latitude"], city1["longitude"]), (city2["latitude"], city2["longitude"])],
                    color="blue",
                    weight=2.5,
                    opacity=0.8
                ).add_to(map_object)

        # Enregistrer la carte dans un fichier HTML pour visualisation
        map_object.save("out/routes_map.html")
        print("Carte avec routes enregistrée sous 'out/routes_map.html'")


if __name__ == "__main__":
    display_train_network = DisplayTrainNetwork("neo4j://localhost:7687")

    center_switzerland = [46.800663464, 8.222665776]

    # Récupère les villes et routes depuis Neo4j
    cities, routes = display_train_network.fetch_cities_and_routes()
    print("Cities:", len(cities))
    print("Routes:", len(routes))

    # display cities on the map
    display_train_network.display_cities()

    display_train_network.display_routes(routes, cities)
