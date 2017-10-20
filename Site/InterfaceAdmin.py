import json
from urllib.request import urlopen

from kivy.app import App
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

def loaddata():
    data = urlopen('http://localhost:8080/getmovies').read()
    data = json.loads(data.decode('utf-8'))
    titre_films = []

    for i in range(len(data['films'])):
        titre_films.append(data['films'][i]['titre'])
    return data['films'],titre_films


class AlCine(GridLayout):
    movies, title_movies = loaddata()
    output_info = ObjectProperty()
    movies_supp = ObjectProperty()
    position = ''

    def Details_films(self, text):
        recette = ''

        if text != '':
            self.position = str(self.title_movies.index(text))
            film = self.movies[self.title_movies.index(text)]

            for i in range(len(film['recette'])):
                recette += '\n         ' + str(film['recette'][i])

            self.output_info.text = '''- Titre: {}
- Genre: {}
- Boisson: {}
- Jeu: {}
- Recette: {}'''.format(film['titre'], film['genre'],
                        film['boisson'], film['jeu'], recette)

    def Supprimer(self):
        data = urlopen('http://localhost:8080/delmovies?mov=' + self.position)
        data = data.read().decode('utf-8')

        if (data == 'OK'):
            self.output_info.text = ''
            self.movies_supp.text = ''
            self.movies, self.movies_supp.values = loaddata()


class AlCineApp(App):
    title = 'AlCiné'


Config.set('graphics','width','700')
Config.set('graphics','height','500')

AlCineApp().run()
