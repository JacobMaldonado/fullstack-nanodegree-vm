#Para la coneeccion http
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
#para la coneccion a la base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#para importar nuestra base de datos
from database_setup import Restaurant, Base, MenuItem

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.header_restaurants()
                return
            elif self.path.endswith("/restaurants/new"):
                self.header_create_restaurants()
                return
            elif self.path.endswith("/update"):
                self.header_update_restaurant()
                return
        except IOError:
            self.send_error(404, 'File Not Found: ' + str(self.path))

    def do_POST(self):
        try:
            if(self.path.endswith("/restaurants/new")):
                self.post_new_restaurant()
            elif self.path.endswith("/update"):
                self.post_update_restaurant()
        except:
            pass

    #opcion para el header restaurants
    def header_restaurants(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        output = ""
        output += "<html><body>"
        output += "<h1>Restaurants</h1>"
        output += "<h2>"
        output += self.get_restaurants_from_db(self.session_from_db())
        output += "</h2></br>"
        output += "<p><a href = '/restaurants/new'>New Restaurant</a></p>"
        output += "</body></html>"
        self.wfile.write(output)
        print output
        return

    def header_create_restaurants(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        output = ""
        output += "<html><body>"
        output += "<h1>Restaurants</h1>"
        output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                        <h2>Create a Restaurant</h2>
                        <input name="restaurant" type="text" >
                        <input type="submit" value="Submit">
                    </form>'''
        output += "<a href = '/restaurants'> go Back </a>"
        output += "</body></html>"
        self.wfile.write(output)
        print output
        return

    #proceso GET para el update de un restaurant
    def header_update_restaurant(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        id_res = self.path.split("/")[2]
        session = self.session_from_db()
        name = session.query(Restaurant).filter_by(id = id_res).one()
        output = ""
        output += "<html><body>"
        output += "<h1>" + str(name) + "</h1>"
        output += "<form method='POST' enctype='multipart/form-data' action='restaurants/" + str(id_res) + "/update'>" 
        output +=                '<h2>Update a Restaurant</h2>'
        output +=                '<input name="restaurant" type="text" >'
        output +=                '<input type="submit" value="Submit">'
        output +=            '</form>'
        output += "<a href = '/restaurants'> go Back </a>"
        output += "</body></html>"
        self.wfile.write(output)
        print output
        return

    def post_update_restaurant(self):
        ctype, pdict = cgi.parse_header(
            self.headers.getheader('content-type'))
        id_res = self.path.split("/")[2]
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            restaurant_content = fields.get('restaurant')
            self.update_restaurant_from_db(self.session_from_db(), id_res, restaurant_content[0])
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

    #proceso POST para un nuevo restaurante
    def post_new_restaurant(self):
        ctype, pdict = cgi.parse_header(
            self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            restaurant_content = fields.get('restaurant')
            self.insert_restaurant_to_db(self.session_from_db(), restaurant_content[0])
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

    #crea la sesion de la base de datos
    def session_from_db(self):
        #Conectando con la base de datos y creando la sesion
        engine = create_engine('sqlite:///restaurantmenu.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind = engine)
        session = DBSession()
        return session

    #consigue los restaurantes de la bd
    def get_restaurants_from_db(self, session):

        #creando las consultas
        items = session.query(Restaurant).all()
        result = ""
        for item in items:
            result += item.name + "</br>"
            result += "<a href = '/restaurants/" + str(item.id) + "/update' > Update</a> </br>"
            result += "<a href = '' > Delete</a> </br></br>"
        return result

    #inserta el restaurante a la base de datos
    def insert_restaurant_to_db(self, session, restaurant_name):
        newRestaurant = Restaurant(name = restaurant_name)
        session.add(newRestaurant)
        session.commit()

    def update_restaurant_from_db(self, session, restaurant_id, restaurant_name):
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        restaurant.name = restaurant_name
        session.add(restaurant)
        session.commit()

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print("Web Server running on port " + str(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
