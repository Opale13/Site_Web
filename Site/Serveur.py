import json
import os.path

import cherrypy
from cherrypy.lib.static import serve_file
import jinja2

import jinja2plugin
import jinja2tool

ROOT = os.path.abspath(os.getcwd())

class AlCine():

    def __init__(self):
        self.films = self.loadfilms()
        self.titre = []
        for i in range(len(self.films)):
            self.titre.append(self.films[i]['titre'])

    @cherrypy.expose
    def index(self):
        """Permet d'afficher les image-lien dans la page index"""
        if len(self.films) == 0:
            films = '<p>No movies in the database.</p>'
        else:
            films = ''
            nbr_image = 0

            for i in range(len(self.films)):
                movie = self.films[i]

                if nbr_image == 4:
                    films += '<br>'
                    nbr_image = 0

                films += '''<a href="fiche?numero={}"><img src={} width="250" height="370"></a>'''.format(i,
                                                                                                          movie['affiche'])
                nbr_image += 1
        return {'film': films}

    @cherrypy.expose
    def fiche(self, numero):
        """Renvoie des variables dans les balises situées dans la page fiche"""
        num = int(numero)

        recette_cocktail = '<br>'
        for j in range(len(self.films[num]["recette"])):
            recette_cocktail += self.films[num]["recette"][j]
            recette_cocktail += '<br>'

        movie = self.films[int(numero)]

        return {"title": movie['titre'], "genre": movie['genre'], "boisson": movie['boisson'],
                "recipe": recette_cocktail, "picture": movie['affiche'], "game": movie['jeu']}

    @cherrypy.expose
    def formulaire(self):
        return None

    @cherrypy.expose
    def getmovies(self):
        """Permet d'obtenir via l'interface administrateur la base de donnée"""
        return json.dumps({
            'films': self.films
        }, ensure_ascii=False).encode('utf-8')

    @cherrypy.expose
    def delmovies(self, mov):
        """Supprime un film via l'interface administrateur"""
        resultat = 'KO'
        num_mov = int(mov)

        if 0 <= num_mov < len(self.films):
            del(self.films[num_mov])
            resultat = 'OK'

        self.savefilms()

        return resultat.encode('utf-8')

    @cherrypy.expose
    def addmovies(self, titre, genre, boisson, recette, jeu=""):
        """Permet de rajouter des films à la base de donnée via le formulaire"""

        if titre in self.titre:
            return '''Votre film existe déjà dans notre base de données<br>
                        <a href="index"><input type="button" value="Acceuil"></a>
                        <a href="formulaire"><input type="button" value="formulaire"></a>'''.encode("UTF-8")

        elif titre == "" or genre == "" or boisson == "" or recette == "":
            return '''Champs non remplis <form method="post" action="formulaire">
                                         <input type="submit" value="Return" >
                                         </form>'''.encode("UTF-8")

        else:
            recipe = recette.split(";")
            dico_db ={"titre": titre, "genre": genre, "boisson": boisson, "recette": recipe,
                      "jeu": jeu, "affiche": ""}

            self.films.append(dico_db)
            self.savefilms()
            return '''Votre film à bien été rajouté, redirigez-vous vers notre page d\'acceuil
                                            <form method="post" action="index">
                                            <input type="submit" value="Acceuil" >
                                            </form>'''.encode("UTF-8")

    @cherrypy.expose
    def search(self, recherche):
        try:
            if recherche == '':
                return {"resultat":"<h2>Aucune recherche effectuée</h2>"}
            position = []
            for i in range(len(self.films)):
                if recherche in self.films[i]['titre']:
                    position.append(i)

            result = ''
            for i in position:
                result += '''<a href="fiche?numero={}"><img src={} width="250"height="370"></a>'''.format(str(i),
                                                                                                          self.films[i]['affiche'])
            return {"resultat": result, "recherche": recherche}

        except:
            return None

    def loadfilms(self):
        """Permet de charger la base de donnée dans une variable"""
        try:
            with open('DataBase.json', 'r') as file:
                content = json.loads(file.read())
                print(content)
                return content['films']
        except:
            cherrypy.log('Loading database failed.')
            return []

    def savefilms(self):
        """Permet de sauvegarder la base de donnée apres modification"""
        try:
            with open("DataBase.json", "w") as file:
                file.write(json.dumps({
                    'films':self.films}, ensure_ascii=False, indent=4))
        except:
            cherrypy.log('Saving database failed.')

if __name__ == '__main__':
    ENV = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    jinja2plugin.Jinja2TemplatePlugin(cherrypy.engine, env=ENV).subscribe()
    cherrypy.tools.template = jinja2tool.Jinja2Tool()

    cherrypy.quickstart(AlCine(),'','serveur.conf')