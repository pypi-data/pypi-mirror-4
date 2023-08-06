#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Exporte le contenu d'une base sqlite en csv (encodage utf-8)

import sqlite3
# Requête des données à exporter
c.execute('select champ1, champ2, champ3 from table')
# On appelle la classe sqlite2csv qui se charge de l'export
export = sqlite2csv(open(FICHIER.csv, "wb"))
# Entête du fichier csv
export.writerow(["Champ1", "Champ2", "Champ3"])
# Lignes du fichier csv
export.writerows(c)
# On ferme la connexion sqlite et le curseur
c.close
conn.close
"""
import csv, codecs, cStringIO

class sqlite2csv:

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Rediriger la sortie vers une file d'attente
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Récupếrer les données dans la file d'attente encodées en utf-8
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # Les encoder vers l'encodage de sortie
        data = self.encoder.encode(data)
        # Ecrire dans le flux de sortie
        self.stream.write(data)
        # Vider la file d'attente
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
