from django.urls import path
from .views import *

urlpatterns = [
    #Route vers la page d'accueil
    path('', home, name="home"),
    
    #Route vers la page d'accueil du chacun des personnelles de l'entreprises
    path('home_admin', home_admin, name="home_admin"),
    path('home_salarie', home_salarie, name="home_salarie"),
    path('home_entreprise', home_entreprise, name="home_entreprise"),
    path('home_test', home_test, name="home_test"),
    
    #Route vers les pages concernant l'authentification
    path('connexion', connexion, name="connexion"),
    path('deconnexion', deconnexion, name="deconnexion"),
    
    #Route vers les méthodes de création gérer par l'admin et ses représentants
    path('success', success, name="success"),
    path('creer_departement', creer_departement, name="creer_departement"),
    path('creer_role', creer_role, name="creer_role"),
    path('creer_compte', creer_compte, name="creer_compte"),
    path('creer_contrat', creer_contrat, name="creer_contrat"),
    path('creer_fichepaie', creer_fichepaie, name="creer_fichepaie"),
    
    #Route vers les méthodes pour gérer les affichages par l'admin et ses représentants
    path('liste_salarie', liste_salarie, name="liste_salarie"),
    path('liste_entreprise', liste_entreprise, name="liste_entreprise"), 
]

