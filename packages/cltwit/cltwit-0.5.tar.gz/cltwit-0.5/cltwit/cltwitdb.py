#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

"""
import sqlite3
import os, sys
import gettext
import types
import tweepy
APP_NAME = 'cltwit'
LOC_PATH = os.path.dirname(__file__) + '/locale'
gettext.find(APP_NAME, LOC_PATH)
gettext.install(APP_NAME, LOC_PATH, True)

class cltwitdb:

    def __init__(self, loc, name):
        self.dblocation = loc
        self.table_name = name

    def smart_unicode(self,s, encoding='utf-8', errors='strict'):
        if type(s) in (unicode, int, long, float, types.NoneType):
            return unicode(s)
        elif type(s) is str or hasattr(s, '__unicode__'):
            return unicode(s, encoding, errors)
        else:
            return unicode(str(s), encoding, errors)

    def create(self, api, twittername):
        """ Créer une base de données """
        if (not os.path.exists(self.dblocation)):
            conn = sqlite3.connect(self.dblocation)
            c = conn.cursor()
            sql = 'create table if not exists ' + self.table_name + \
            '(id integer PRIMARY KEY, date text, tweet text, id_str text, url text )'
            c.execute(sql)
        conn = sqlite3.connect(self.dblocation)
        c = conn.cursor()
        #~ print(_(self.smart_unicode("Création de la liste des tweets de ")) + twittername)
        conn.text_factory = str
        page_list = []
        try:
            for page in tweepy.Cursor(api.user_timeline,
                    count=200,include_rts=True).pages(16):
                page_list.append(page)

            for page in page_list:
                for status in page:
                    self.insert(status.text, status.created_at, status.id_str, twittername,conn,c)
        except Exception,e :
            print(str(e) + "\n")
        # On ferme la connexion et le curseur
        conn.commit()
        c.close()
        conn.close()

    def update(self, api, twittername):
        """ Mettre à jour une base de données """
        if (not os.path.exists(self.dblocation)):
            print(_(self.smart_unicode("La base de données n'existe pas, utilisez --database create")))
            sys.exit()
        # Récupérer l'id_str from du tweet le plus récent
        conn = sqlite3.connect(self.dblocation)
        c = conn.cursor()
        c.execute('select id_str from twitter order by date desc limit 1')
        # fetchone() retourne un tuple
        since = c.fetchone()[0]

        print(_(self.smart_unicode("Mise à jour de la base de données de {0}\n")).format(twittername ))
        nb = 0
        try:
            for status in tweepy.api.user_timeline(twittername, since_id=since):
                nb +=1
                self.insert(status.text, status.created_at, status.id_str, twittername,conn,c)
        except Exception,e :
            print(str(e) + "\n")

        print(_(self.smart_unicode("Ajout de {0} tweet(s) dans la base de données.").format(nb)))

        conn.commit()
        c.close()
        conn.close()

    def insert(self, statustext, statuscreated_at, statusid_str, twittername, conn, c):
        """ Insérer dans la base """
        statusurl = "https://twitter.com/{0}/status/{1}".format\
        (twittername, statusid_str)
        #'insert_query = ''INSERT INTO testTable ({0}) VALUES ({1})'''.format(
        #(','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        #cur.execute(insert_query, tuple)
        insert_query = '''INSERT INTO {0} VALUES (null,{1})'''.format(self.table_name, ','.join('?'*4))
        try:
            c.execute(insert_query, [(str(statuscreated_at)), \
            (self.smart_unicode(statustext)), (str(statusid_str)), (str(statusurl))])
        except Exception, e:
            print e

    def search(self, search, champ_recherche):
        """Rechercher un motif dans une table sqlite (retourne un tuple)"""
        # Récupérer l'id_str from du tweet le plus récent
        conn = sqlite3.connect(self.dblocation)
        conn.text_factory = str
        c = conn.cursor()
        c.execute("select * from {0} where {1} like ? order by date desc".format(self.table_name, champ_recherche), [('%'+search+'%'),])
        # fetchall() retourne un tuple
        return c.fetchall()
        c.close()
        conn.close()
