#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Cltwit is a command line twitter utility
Author : Jérôme Launay
Date : 2013
"""

from sqlite2csv import sqlite2csv
from cltwitdb import cltwitdb
import ConfigParser
import webbrowser
import os, sys
import getopt
import types
import gettext
import sqlite3
import csv, codecs

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

def smart_str(s, encoding='utf-8', errors='strict', from_encoding='utf-8'):
    if type(s) in (int, long, float, types.NoneType):
        return str(s)
    elif type(s) is str:
        if encoding != from_encoding:
            return s.decode(from_encoding, errors).encode(encoding, errors)
        else:
            return s
    elif type(s) is unicode:
        return s.encode(encoding, errors)
    elif hasattr(s, '__str__'):
        return smart_str(str(s), encoding, errors, from_encoding)
    elif hasattr(s, '__unicode__'):
        return smart_str(unicode(s), encoding, errors, from_encoding)
    else:
        return smart_str(str(s), encoding, errors, from_encoding)

def smart_unicode(s, encoding='utf-8', errors='strict'):
    if type(s) in (unicode, int, long, float, types.NoneType):
        return unicode(s)
    elif type(s) is str or hasattr(s, '__unicode__'):
        return unicode(s, encoding, errors)
    else:
        return unicode(str(s), encoding, errors)

def checkdb():
    """ Vérifier la présence de la bdd sqlite et la créer si absente """
    if (not os.path.exists(__dblocation__)):
        print(_(smart_unicode("Vous devez d'abord lancer la commande --database create \
pour créer une base de données de vos tweets.")))
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
                #~ var  = raw_input(_(smart_unicode("Entrez le numéro d'autorisation !\n")))
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
            print(_(smart_unicode("Impossible de s'authentifier avec l'api Twitter.\n \
Fonctionne en mode déconnecté")))
            twittername = "offline_mode"
    print(_(smart_unicode("Authentifié avec le user twitter {0}\n")).format(twittername))
    return api, auth, twittername

def get_friends_followers(api):
    """Renvoie la liste des id des friends et followers"""
    friend_id = []
    follower_id = []

    print(_(smart_unicode("Récupération des Followers...")))
    for follower in tweepy.Cursor(api.followers).items():
        follower_id.append(follower.id)

    print(_(smart_unicode("Récupération des Friends...\n")))
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
        print(_("Vous suivez maintenant {0}").format(api.get_user(user).screen_name))
    except Exception,e:
        print(e)

def unfollow_user(api, user):
    """Cesser de suivre une personne"""
    try:
        api.destroy_friendship(user)
        print(_("Vous ne suivez plus {0}").format(api.get_user(user).screen_name))
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
        opts, args = getopt.getopt(sys.argv[1:], "hfut:o:s:d:",\
                                       ["help","follow","unfollow","tweet=","output=","search=","database="])
    except getopt.GetoptError, err:
        print(err)
        help()
        sys.exit()
    # traitement des options
    for option, value in opts:
        if option in ('-d','--database'):
            if value in ('u','update'):
                # Se connecter à l'api twitter
                api, auth, twittername = login()
                # Mettre à jour la base de données
                db = cltwitdb(__dblocation__, __tablename__)
                db.update(api, twittername)
            if value in ('c','create'):
                # Se connecter à l'api twitter
                api, auth, twittername = login()
                # Créer la base de données
                db = cltwitdb(__dblocation__, __tablename__)
                print(_(smart_unicode("Création de la liste des tweets de ")) + twittername)
                db.create(api, twittername)
                print(_(smart_unicode("Base de données crée")))
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
            print(_(smart_unicode("Fichier csv {0} créé.").format(value)))
            sys.exit()
        if option in ("-s", "--search"):
            # Rechercher un motif dans la base des tweets
            checkdb()
            print(_(smart_str("Recherche de {0} dans vos anciens tweets...\n"))\
                      .format(smart_unicode(value)))
            # la méthode search retourne un tuple avec les champs
            # qui contiennent le motif
            db = cltwitdb(__dblocation__, __tablename__)
            results = db.search(value,"tweet")
            for result in results:
                print(smart_str("{0} -> {1}\n{2}\n\n").format(result[1],result[4], result[2]))

        if option in ("-u", "--unfollow"):
            # Se connecter à l'api twitter
            api, auth, twittername = login()
            # Créer les liste friend et followers (par id)
            friend_id,follower_id = get_friends_followers(api)
            # Création des listes follow et unfollow
            follow_liste = get_diff(follower_id, friend_id)
            unfollow_liste = get_diff(friend_id, follower_id)
            # Un-follow
            print(_("Vous suivez {0} personnes qui ne vous suivent pas.\n")\
                      .format(len(unfollow_liste)))
            print(_("Voulez changer cela ? (o/N)"))
            reponse = raw_input("> ")
            if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                for user in unfollow_liste:
                    print(_("Voulez-vous cesser de suivre {0} ? (o/N)")\
                              .format(api.get_user(user).screen_name))
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
            print(_("{0} personnes vous suivent alors que vous ne les suivez pas.\n")\
                      .format(len(follow_liste)))
            print(_("Voulez changer cela ? (o/N)"))
            reponse = raw_input("> ")
            if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                for user in follow_liste:
                    print(_("Voulez-vous suivre {0} ? (o/N)"\
                                .format(api.get_user(user).screen_name)))
                    reponse = raw_input("> ")
                    if (reponse.lower() == 'o' or reponse.lower() == 'y'):
                        follow_users(api, user)

        if option in ("-t","--tweet"):
            # Se connecter à l'api twitter
            api, auth, twittername = login()
            # Envoyer un tweet
            if len(value) < 141:
                api.update_status(value)
                print(_(smart_unicode("\nTweet envoyé !")))
            else:
                print(_(smart_unicode("La limite pour un tweet est de 140 caractères, votre message \
fait {0} caractères de trop").format(str(len(value) - 140))))
            sys.exit()

        if option in ("-h", "--help"):
            help()

def help():
    print(_(smart_unicode("""
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
-o (--output) FILENAME
    *Exporter l'intégralité de vos tweets dans \
le fichier FILENAME

-d (--database) c|u
    c (create)
            *Créer ou récréer la base de données des tweets
    u (update)
            *Mettre à jour la base de données des tweets
""")
            )
          )

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(_(smart_unicode("\nMerci d'avoir utilisé clitwit !")))
