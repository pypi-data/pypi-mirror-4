# #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class utilisée par Cltwit pour générer un reporting pdf de la répartition des tweets
"""
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor

pdf_chart_colors = [
    HexColor("#0000e5"),
    HexColor("#1f1feb"),
    HexColor("#5757f0"),
    HexColor("#8f8ff5"),
    HexColor("#c7c7fa"),
    HexColor("#f5c2c2"),
    HexColor("#eb8585"),
    HexColor("#e04747"),
    HexColor("#d60a0a"),
    HexColor("#ff0000"),
    HexColor("#cc0000"),
    HexColor("#B20000"),
    ]

def setItems(n, obj, attr, values):
    """définir la couleur des slices"""
    m = len(values)
    i = m // n
    for j in xrange(n):
        setattr(obj[j],attr,values[j*i % m])

class TweetsReport():
    """ Ecrit sur un canvas """
    def __init__(self,pdfPath):
        self.canvas = Canvas(pdfPath)

    def ecrireLegende(self, decalage, year, donnes):
        """ Ecrire la légenge """
        self.canvas.setFont('Times-Bold', 18)
        self.canvas.drawString(70,610 - decalage ,"Année {0}".format(year))
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(420,680 - decalage ,"Janvier : {0}".format(donnes[0]) )
        self.canvas.drawString(420,668 - decalage ,"Février : {0}".format(donnes[1]) )
        self.canvas.drawString(420,656 - decalage ,"Mars : {0}".format(donnes[2]) )
        self.canvas.drawString(420,644 - decalage ,"Avril : {0}".format(donnes[3]) )
        self.canvas.drawString(420,632 - decalage ,"Mai : {0}".format(donnes[4]) )
        self.canvas.drawString(420,620 - decalage ,"Juin : {0}".format(donnes[5]) )
        self.canvas.drawString(420,608 - decalage ,"Juillet : {0}".format(donnes[6]) )
        self.canvas.drawString(420,596 - decalage ,"Août : {0}".format(donnes[7]) )
        self.canvas.drawString(420,584 - decalage ,"Septembre : {0}".format(donnes[8]) )
        self.canvas.drawString(420,572 - decalage ,"Octobre : {0}".format(donnes[9]) )
        self.canvas.drawString(420,560 - decalage ,"Novembre : {0}".format(donnes[10]) )
        self.canvas.drawString(420,548 - decalage ,"Décembre : {0}".format(donnes[11]) )


    def ecrireTitre(self,user):
        """ Ecrire le titre """
        self.canvas.setFont('Times-Bold', 18)
        self.canvas.drawString(50,790,"Cltwit")
        self.canvas.setFont("Helvetica", 14)
        self.canvas.drawString(50,750,"Nombre de tweets envoyés par année et par mois par {0}".format(user))

    def addPie(self,decalage,donnes):
        self.d = Drawing(300, 200)
        self.pc = Pie()
        self.pc.data = donnes
        self.pc.checkLabelOverlap = 1
        self.pc.labels = ['Jan.','Fev.','Mar.','Avr.','Mai.','Juin','Jui.','Aou.','Sept','Oct.','Nov.','Dec.']
        self.pc.x = 20
        self.pc.y = 90
        self.pc.width = 140
        self.pc.height = 140
        n = len(self.pc.data)
        setItems(n,self.pc.slices,'fillColor',pdf_chart_colors)
        self.d.add(self.pc)
        self.d.drawOn(self.canvas, 200, 450 - decalage)

    def NextPage(self):
        """ Créer une nouvelle page """
        self.canvas.showPage()

    def save(self):
        """ Enregistrer """
        self.canvas.save()
