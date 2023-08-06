#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Cltwit is a command line twitter utility
Author : Jérôme Launay
Date : 2013
"""

from sqlite2csv import sqlite2csv
from cltwitdb import cltwitdb
from utils import LocalTimezone
from cltwitreport import TweetsReport 
import ConfigParser
import webbrowser
import os, sys
import getopt
import gettext
import sqlite3

APP_NAME = 'cltwit'
LOC_PATH = os.path.dirname(__file__) + '/locale'
gettext.find(APP_NAME, LOC_PATH)
gettext.install(APP_NAME, LOC_PATH, True)

try:
    import tweepy
except ImportError:
    print(_("Veuillez installer tweetpy https://github.com/tweepy/tweepy"))
    sys.exit()


# Répertoire pour conf et bdd
__cltwitdir__ = os.path.expanduser("~/.config/cltwit")
# Fichier de configuration
__configfile__ = __cltwitdir__ + "/cltwit.conf"
# base de données et table sqlite
__dblocation__ = __cltwitdir__ + '/data.db'
__tablename__ = 'twitter'


__Local__ = LocalTimezone()

# gestion des couleurs sur le terminal
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def has_colours(stream):
    """Vérifier la prise en charge des couleurs par le terminal"""
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # couleurs auto sur un TTY
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # Si erreur on suppose false
        return False

__has_colours__ = has_colours(sys.stdout)


def printout(text, colour=WHITE):
    """Print en couleur"""
    if __has_colours__:
        seq = "\x1b[1;%dm" % (30+colour) + text + "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)


def checkdb():
    """ Vérifier la présence de la bdd sqlite et la créer si absente """
    if (not os.path.exists(__dblocation__)):
        printout(_(u"Vous devez d'abord lancer la commande --database create \
pour créer une base de données de vos tweets."), RED)
        sys.exit()

def checkconfig():
    """Récupérer la configuration ou la créer"""
    # On ouvre le fichier de conf
    config = ConfigParser.RawConfigParser()
    try:
        config.read(__configfile__)
        if config.has_option('twitterapi','access_token'):
            access_token = config.get('twitterapi','access_token')
        if config.has_option('twitterapi','access_password'):
            access_password = config.get('twitterapi','access_password')
    except:
        pass

    auth = tweepy.OAuthHandler("Jus1rnqM6S0WojJfOH1kQ",
                               "AHQ5sTC8YYArHilXmqnsstOivY6ygQ2N27L1zBwk")

    # Si aucune conf , autorisation de connexion à twitter via OAuth
    if not(config.has_option('twitterapi','access_token') and
           config.has_option('twitterapi','access_password')):
        # On ouvre le navigateur web pour récupếrer le numéro d'autorisation
        while True:
            try:
                webbrowser.open(auth.get_authorization_url())
                var  = raw_input(_("Entrez le token !\n"))
                auth.get_access_token(var)
            except Exception,e:
                print(str(e))
                continue
            break
        var = auth.access_token
        # On récupère le token et le password
        access_password = str(var).split("&")[0].split("=")[1]
        access_token = str(var).split("&")[1].split("=")[1]
        # écrire le fichier de conf avec les informations récupérées
        try:
            cfgfile = open(__configfile__,'w')
            if not(config.has_section('twitterapi')):
                config.add_section('twitterapi')
            config.set('twitterapi', 'access_token', access_token)
            config.set('twitterapi', 'access_password', access_password)
            config.write(cfgfile)
        except IOError:
            pass
        finally:
            cfgfile.close()
    else: # Si un fichier de conf existait déjà
        auth.set_access_token(access_token, access_password)
    return auth

def login():
    """ Se connecter à l'api twitter via tweepy """
    auth = checkconfig()
    api = tweepy.API(auth)
    # On vérifie la connexion à l'api en récupérant le user name
    try:
        twittername = api.me().screen_name
    except Exception,e:
        if 'Unable to get username' in (str(e)):
            printout(_(u"Impossible de s'authentifier avec l'api Twitter.\
Fonctionne en mode déconnecté"), RED)
            print("\n")
            twittername = "offline_mode"
    printout(_(u"Authentifié avec le user twitter {0}").format(twittername.decode('utf-8')), GREEN)
    print("\n")
    return api, auth, twittername

def get_friends_followers(api):
    """Renvoie la liste des id des friends et followers"""
    friend_id = []
    follower_id = []
    printout(_(u"Récupération des Followers..."), YELLOW)
    print("\n")
    for follower in tweepy.Cursor(api.followers).items():
        follower_id.append(follower.id)
    printout((u"Récupération des Friends..."), YELLOW)
    print("\n")
    for friend in tweepy.Cursor(api.friends).items():
        friend_id.append(friend.id)

    return friend_id, follower_id

def get_diff(liste1, liste2):
    """Renvoie les objets de liste1 qui ne sont pas dans liste2"""
    return list(set(liste1).difference(set(liste2)))

def follow_users(api, user):
    """Suivre une personne"""
    try:
        api.create_friendship(user)
        printout(_(u"Vous suivez maintenant {0}").format(api.get_user(user).screen_name.decode('utf-8')), GREEN)
    except Exception,e:
        print(e)

def unfollow_user(api, user):
    """Cesser de suivre une personne"""
    try:
        api.destroy_friendship(user)
        printout(_(u"Vous ne suivez plus {0}").format(api.get_user(user).screen_name.decode('utf-8')), GREEN)
    except Exception,e:
        print(e)

def main(argv=None):
    """ Point d'entrée """
    # Si le répertoire pour la conf et la base de données n'existe pas le créer
    if not os.path.exists(__cltwitdir__):
        os.makedirs(__cltwitdir__)
    #~ twittername = "offline_mode"
    # Traitement des arguments
    if argv is None:
        argv = sys.argv
    if len(argv)  == 1:
        help()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:ahfut:o:s:d:", \
       ["report", "api", "help", "follow", "unfollow", "tweet=", "output=", "search=", "database="])
    except getopt.GetoptError, err:
        print(err)
        help()
        sys.exit()
    # traitement des options
    for option, value in opts:
        if option in ('-a','--api'):
            api, auth, twittername = login()
            res = api.rate_limit_status()
            rtime = res['reset_time']
            rhits = res['remaining_hits']
            hlimit = res['hourly_limit']
            

            from dateutil.parser import parse
            drtime = parse(rtime)
            
            printout(_("Informations sur l'utilisation de l'api Twitter"), YELLOW)
            print("\n")
            # Définir l'heure locale qui correspond à l'heure renvoyée
            # par l'api Twitter
            rlocaltime = drtime.astimezone(__Local__)
            printout(_("Maximum d'appels par heure: "), BLUE)
            print hlimit
            printout(_("Nombre d'appels restants: "), BLUE)
            print rhits
            printout(_("Heure du prochain reset: "), BLUE)
            print rlocaltime.strftime("%H:%M %Y-%m-%d")

        if option in ('-r','--report'):
            api, auth, twittername = login()

            checkdb()

            conn = sqlite3.connect(__dblocation__)
            c = conn.cursor()
            c.execute("select substr(date, 1,4)  from twitter order by date asc limit 1")
            dmois = c.fetchone()[0] 
            c.execute("select substr(date, 1,4)  from twitter order by date desc limit 1")
            fmois = c.fetchone()[0]
            # Requête des données à exporter
            dd = dict()
            for a in range (int(dmois), int(fmois) + 1):
                result = []
                for m in range (1, 13):
                    mois = ('{num:02d}'.format(num=m))
                    c.execute("select count(*) from twitter where substr(date, 1,4)  = '{0}' and substr(date, 6,2) = '{1}'".format(a, mois))
                    result.append(c.fetchone()[0])
                dd[a] = result
            c.close()
            conn.close()
            treport = TweetsReport(value)
            # twittername = "offline"
            treport.ecrireTitre(twittername)
            nb = 0
            for annee, donnees in dd.items():
                nb += 1
                if nb == 4:
                    treport.NextPage()
                    nb = 1
                    saut = 0
                if nb == 1:
                    saut = 0
                if nb == 2:
                    saut = 200
                if nb == 3:
                    saut = 400
                treport.ecrireLegende(saut,annee,donnees)
                treport.addPie(saut,donnees)
            treport.save()
            printout(_(u"Report {0} créé !").format(value), GREEN)
            print("\n")
            sys.exit(0)

        if option in ('-d','--database'):
            if value in ('u','update'):
                # Se connecter à l'api twitter
                api, auth, twittername = login()
                # Mettre à jour la base de données
                db = cltwitdb(__dblocation__, __tablename__)
                printout(_(u"Mise à jour de la base de données de {0}").format(twittername.decode('utf-8')), YELLOW)
                print("\n")
                nb = db.update(api, twittername)
                printout(_(u"Ajout de {0} tweet(s) dans la base de données.").format(nb), GREEN)
            if value in ('c','create'):
                # Se connecter à l'api twitter
                api, auth, twittername = login()
                # Créer la base de données
                db = cltwitdb(__dblocation__, __tablename__)
                printout(_(u"Création de la liste des tweets de ") + twittername.decode('utf-8'), YELLOW)
                db.create(api, twittername)
                printout(_(u"Base de données crée"), GREEN)
                sys.exit()

                #~ database_create(api,twittername)
        if option in ("-o", "--output"):
            # Exporter en csv
            checkdb()
            conn = sqlite3.connect(__dblocation__)
            c = conn.cursor()
            # Requête des données à exporter
            c.execute('select date, tweet, url from {0} order by date desc'.format(__tablename__))
            # On appelle la classe sqlite2csv qui se charge de l'export
            export = sqlite2csv(open(value, "wb"))
            # Entête du fichier csv
            export.writerow(["Date", "Tweet", "URL"])
            # Lignes du fichier csv
            export.writerows(c)
            # On ferme la connexion sqlite et le curseur
            c.close()
            conn.close()
            printout(_(u"Fichier csv {0} créé.").format(value.decode('utf-8')), GREEN)
            sys.exit()
        if option in ("-s", "--search"):
            # Rechercher un motif dans la base des tweets
            checkdb()
            printout(_(u"Recherche de {0} dans vos anciens tweets...")\
                      .format(value.decode('utf-8')), YELLOW)
            print("\n")
            # la méthode search retourne un tuple avec les champs
            # qui contiennent le motif
            db = cltwitdb(__dblocation__, __tablename__)
            results = db.search(value,"tweet")
            for result in results:
                print((u"{0} -> {1}\n{2}\n\n").format(result[1].decode('utf-8'),result[4].decode('utf-8'), result[2].decode('utf-8')))

        if option in ("-u", "--unfollow"):
            # Se connecter à l'api twitter
            api, auth, twittername = login()
            # Créer les liste friend et followers (par id)
            friend_id,follower_id = get_friends_followers(api)
            # Création des listes follow et unfollow
            follow_liste = get_diff(follower_id, friend_id)
            unfollow_liste = get_diff(friend_id, follower_id)
            # Un-follow
            printout(_("Vous suivez {0} personnes qui ne vous suivent pas.")\
                      .format(len(unfollow_liste)), YELLOW)
            print("\n")
            printout(_("Voulez changer cela ? (o/N)"), BLUE)
            print("\n")
            reponse = raw_input("> ")
            if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                for user in unfollow_liste:
                    printout(_("Voulez-vous cesser de suivre {0} ? (o/N)")\
                              .format(api.get_user(user).screen_name), BLUE)
                    print("\n")
                    reponse = raw_input("> ")
                    if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                        unfollow_user(api, user)

        if option in ("-f", "--follow"):
            # Se connecter à l'api twitter
            api, auth, twittername = login()
            # Créer les liste friend et followers (par id)
            friend_id, follower_id = get_friends_followers(api)
            # Création des listes follow et unfollow
            follow_liste = get_diff(follower_id, friend_id)
            unfollow_liste = get_diff(friend_id, follower_id)

            # follow
            printout(_("{0} personnes vous suivent alors que vous ne les suivez pas.")\
                      .format(len(follow_liste)), YELLOW)
            print("\n")
            printout(_("Voulez changer cela ? (o/N)"), BLUE)
            print("\n")
            reponse = raw_input("> ")
            if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                for user in follow_liste:
                    printout(_("Voulez-vous suivre {0} ? (o/N)"\
                                .format(api.get_user(user).screen_name)), BLUE)
                    print("\n")
                    reponse = raw_input("> ")
                    if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                        follow_users(api, user)

        if option in ("-t","--tweet"):
            # Se connecter à l'api twitter
            api, auth, twittername = login()
            # Envoyer un tweet
            if len(value) < 141:
                api.update_status(value)
                print("\n")
                printout(_(u"Tweet envoyé !"), GREEN)
            else:
                printout(_(u"La limite pour un tweet est de 140 caractères, votre message \
fait {0} caractères de trop").format(str(len(value) - 140).decode('utf-8')), RED)
            sys.exit()

        if option in ("-h", "--help"):
            help()

def help():
    printout(_(u"""
Usage :
cltwit [OPTIONS]
Options :
-f (--follow)
    *Ajouter des personnes qui vous suivent et que vous ne suivez pas
-u (--unfollow)
    *Cesser de suivre les personnes que vous suivez et qui \
vous ne suivent pas
-s (--search) MOTIF
    *Search ( rechercher MOTIF dans vos anciens tweets)
-t  (--tweet)
    *Envoyer un tweet (message de 140 caractères maximum)
-o (--output) FILENAME.csv
    *Exporter l'intégralité de vos tweets dans \
le fichier FILENAME.csv
-a (--api)
    * Obtenir des informations sur l'utilisation de l'api twitter
-r (--report) FILENAME.pdf
    * Générer un reporting format pdf avec la repartition des tweets par année et par mois
-d (--database) c|u
    c (create)
            *Créer ou récréer la base de données des tweets
    u (update)
            *Mettre à jour la base de données des tweets
"""), BLUE
)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n")
        print(_(u"Merci d'avoir utilisé clitwit !"))
