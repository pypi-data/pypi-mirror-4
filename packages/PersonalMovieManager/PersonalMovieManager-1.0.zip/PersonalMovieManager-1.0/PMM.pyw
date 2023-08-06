#-------------------------------------------------------------------------------
# Name:        Personal Movie Manager
# Purpose:     To catalog movies
#
# Author:      Avirup Kundu
#
# Created:     16th January
# Copyright:   (c) Avirup Kundu
# Licence:     GPL
#-------------------------------------------------------------------------------
from PySide import QtCore, QtGui, QtWebKit
import mainWindow
from pyFiles import aboutWindow, unableWindow
import urllib.parse
import urllib.request
import json, sys, pickle, webbrowser,os, ast

class pmm(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(pmm, self).__init__(parent)
        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.data = {}
        self.retrievedData ={}
        self.directors = ''
        self.actors = ''
        self.language = ''
        self.genres = ''
        self.s=''
        with open('f.pkl', 'rb') as f:
            self.storedFilmData = pickle.load(f)

        self.connect(self.ui.imdb_search, QtCore.SIGNAL("clicked()"), self.getData)
        self.connect(self.ui.about, QtCore.SIGNAL("clicked()"), self.about)
        self.connect(self.ui.save, QtCore.SIGNAL("clicked()"), self.save)
        self.connect(self.ui.add_movie, QtCore.SIGNAL("clicked()"), self.addMovie)
        self.connect(self.ui.play_movie, QtCore.SIGNAL("clicked()"), self.playMovie)
        self.connect(self.ui.delete_movie, QtCore.SIGNAL("clicked()"), self.deleteMovie)
        self.connect(self.ui.listWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.updateDisplay)
        self.connect(self.ui.search, QtCore.SIGNAL("clicked()"), self.search)

        self.listSetup()

    def getData(self):
        self.data = {}
        self.receivedData = []
        self.temp_receivedData =[]
        url='http://imdbapi.org/'
        if self.ui.movie_name.displayText()[:2] != 'tt':
            self.data['q']=self.ui.movie_name.displayText()
            self.data['year']=self.ui.movie_release.displayText()
            self.data['type']='json'
        else:
            self.data['ids']=self.ui.movie_name.displayText()
            self.data['type']='json'
        try:
            url_values=urllib.parse.urlencode(self.data)
            full_url = url+'?'+url_values
            self.temp_receivedData.append((urllib.request.urlopen(full_url).read().decode()))
            self.receivedData.append(eval(self.temp_receivedData[0]))
            self.receivedData = json.dumps(self.receivedData)
            self.checkRetrievedData()
        except urllib.error.URLError:
            unableWindow.noInternet().exec_()

    def checkRetrievedData(self):
        try:
            self.retrievedData=json.loads(self.receivedData)[0][0]
            self.checkData()
            self.adjustData()
            self.displayData()
        except (KeyError):
            unWin = unableWindow.unable()
            if unWin.exec_():
                t_url = 'http://www.imdb.com/find'
                t_data = {}
                t_data['q'] = self.ui.movie_name.displayText()
                t_url_values = urllib.parse.urlencode(t_data)
                t_full_url = t_url+'?'+t_url_values

                webbrowser.open(t_full_url)
            else:
                pass
        except ValueError:
            unableWindow.noInternet().exec_()


    def checkData(self):
        try:
            self.retrievedData['rated']
        except KeyError:
            self.retrievedData['rated'] = 'N/A'
        try:
            self.retrievedData['plot_simple']
        except KeyError:
            self.retrievedData['plot_simple'] = 'N/A'
        try:
            self.retrievedData['runtime']
        except KeyError:
            self.retrievedData['runtime'] = list()
            self.retrievedData['runtime'].append('N/A')
        try:
            self.retrievedData['actors']
        except KeyError:
            self.retrievedData['actors'] = list()
            self.retrievedData['actors'].append('N/A')
        try:
            self.retrievedData['directors']
        except KeyError:
            self.retrievedData['directors'] = list()
            self.retrievedData['directors'].append('N/A')
        try:
            self.retrievedData['genres']
        except KeyError:
            self.retrievedData['genres'] = list()
            self.retrievedData['genres'].append('N/A')
        try:
            self.retrievedData['language']
        except KeyError:
            self.retrievedData['language'] = list()
            self.retrievedData['language'].append('N/A')
        try:
            self.retrievedData['poster']
        except KeyError:
            self.retrievedData['poster'] = QtCore.QUrl('poster_not_found.html')


    def adjustData(self):
        self.directors = ''
        self.actors = ''
        self.language = ''
        self.genres = ''
        for i in self.retrievedData['directors']:
            self.directors = self.directors+i+', '
        for i in self.retrievedData['actors']:
            self.actors = self.actors+i+', '
        for i in self.retrievedData['language']:
            self.language = self.language+i+', '
        for i in self.retrievedData['genres']:
            self.genres = self.genres+i+', '

        self.actors = self.actors[:-2]
        self.directors = self.directors[:-2]
        self.language = self.language[:-2]
        self.genres = self.genres[:-2]

    def displayData(self):
        self.ui.movie_name.setText(self.retrievedData['title'])
        self.ui.movie_director.setText(self.directors)
        self.ui.movie_release.setText(str(self.retrievedData['year']))
        self.ui.movie_genre.setText(self.genres)
        self.ui.movie_actor_list.setPlainText(self.actors)
        self.ui.movie_language.setText(self.language)
        self.ui.movie_plot.setPlainText(self.retrievedData['plot_simple'])
        self.ui.movie_imdb_url.setText(self.retrievedData['imdb_url'])
        self.ui.movie_imdb_id.setText(self.retrievedData['imdb_id'])
        self.ui.movie_rating.setText(self.retrievedData['rated'])
        self.ui.movie_length.setText(self.retrievedData['runtime'][0])
        self.ui.webView.load(self.retrievedData['poster'])

    def listSetup(self):
        self.list_data =[]
        for i in self.storedFilmData:
            self.list_data.append(i['title'])
        self.ui.listWidget.insertItems(0, self.list_data)

    def updateDisplay(self):
        try:
            self.n = self.ui.listWidget.currentRow()
            self.retrievedData = self.storedFilmData[self.n]
            self.adjustData()
            self.displayData()
        except IndexError:
            pass

    def getPoster(self):
        urllib.request.urlretrieve(self.retrievedData['poster'], os.path.join('posters', self.retrievedData['poster'].split('/')[-1]))
        s=os.path.join(os.getcwd(), 'posters', self.retrievedData['poster'].split('/')[-1])
        return(s)

    def save(self):
        self.checkRetrievedData()
        d = {}
        d['title']=self.retrievedData['title']
        d['year']=self.retrievedData['year']
        d['imdb_url']=self.retrievedData['imdb_url']
        d['imdb_id']=self.retrievedData['imdb_id']
        d['rated']=self.retrievedData['rated']
        d['runtime']=self.retrievedData['runtime']
        d['directors']=self.retrievedData['directors']
        d['actors']=self.retrievedData['actors']
        d['language']=self.retrievedData['language']
        d['genres']=self.retrievedData['genres']
        d['plot_simple']=self.retrievedData['plot_simple']
        d['poster']=self.getPoster()

        if d['title'] in self.list_data :
            row=self.list_data.index(d['title'])
            self.ui.listWidget.setCurrentRow(row)
        else:
            self.storedFilmData.append(d)
            with open('f.pkl', 'wb') as f:
                pickle.dump(self.storedFilmData, f, pickle.HIGHEST_PROTOCOL)
            self.ui.listWidget.clear()
            self.listSetup()

    def search(self):
        searchText=self.ui.search_text.text()
        if any(searchText.lower() in self.s.lower() for self.s in self.list_data):
            row=self.list_data.index(self.s)
            self.ui.listWidget.setCurrentRow(row)



    def addMovie(self):
        try:
            self.location = QtGui.QFileDialog.getOpenFileName(self)
            with open('f.pkl', 'rb') as f:
                self.temp_storedFilmData = pickle.load(f)
            self.temp_storedFilmData[self.n].update(local_file = self.location[0])
            with open('f.pkl', 'wb') as f:
                    pickle.dump(self.temp_storedFilmData, f, pickle.HIGHEST_PROTOCOL)
            with open('f.pkl', 'rb') as f:
                self.storedFilmData = pickle.load(f)
            self.retrievedData = self.storedFilmData[self.n]
        except AttributeError:
            unableWindow.noEntrySelected().exec_()


    def playMovie(self):
        try:
            os.startfile(self.retrievedData['local_file'])
        except KeyError:
            unableWindow.noMovie().exec_()

    def deleteMovie(self):
        try:
            try:
                os.remove(self.retrievedData['poster'])
            except (WindowsError, KeyError):
                pass
            try:
                self.storedFilmData.pop(self.n)
            except IndexError:
                pass
            with open('f.pkl', 'wb') as f:
                    pickle.dump(self.storedFilmData, f, pickle.HIGHEST_PROTOCOL)
            with open('f.pkl', 'rb') as f:
                self.storedFilmData = pickle.load(f)
            try:
                self.retrievedData = self.storedFilmData[self.n-1]
            except IndexError:
                pass
            self.ui.listWidget.clear()
            self.listSetup()
        except AttributeError:
            unableWindow.noEntrySelected().exec_()

    def about(self):
        abwin = aboutWindow.about()
        abwin.exec_()



app=QtGui.QApplication(sys.argv)
myapp = pmm()
myapp.show()
app.exec_()

