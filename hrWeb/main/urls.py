from django.urls import path
from .views import *

urlpatterns = [
    #Route vers la page d'accueil
    path('', home, name="home"),
    
    #Route vers la page d'accueil du chacun des personnelles de l'entreprises
    path('home_admin', home_admin, name="home_admin"),
    path('home_salarie', home_salarie, name="home_salarie"),
    path('home_entreprise', home_entreprise, name="home_entreprise"),
    path('home_client', home_client, name="home_client"),
    
    #Route vers les pages concernant l'authentification
    path('connexion', connexion, name="connexion"),
    path('deconnexion', deconnexion, name="deconnexion"),
    path('oublier_mot_de_passe', oublier_mot_de_passe, name="oublier_mot_de_passe"),
    path('changer_mot_de_passe', changer_mot_de_passe, name="changer_mot_de_passe"),
    path('statut/<int:user_id>/', statut, name='statut'),
    
    #Route vers les méthodes de création gérer par l'admin et ses représentants
    path('success', success, name="success"),
    path('creer_departement', creer_departement, name="creer_departement"),
    path('creer_role', creer_role, name="creer_role"),
    path('creer_admin', creer_admin, name="creer_admin"),
    path('creer_salarie', creer_salarie, name="creer_salarie"),
    path('creer_partenaire', creer_partenaire, name="creer_partenaire"),
    path('creer_client', creer_client, name="creer_client"),
    path('creer_contrat', creer_contrat, name="creer_contrat"),
    path('creer_fichepaie', creer_fichepaie, name="creer_fichepaie"),
    
    #Route vers les pages de profile
    path('profile_admin', profile_admin, name="profile_admin"),
    path('profile_salarie', profile_salarie, name="profile_salarie"),
    path('profile_entreprise', profile_entreprise, name="profile_entreprise"),
    path('profile_client', profile_client, name="profile_client"),
    
    #Route vers les méthodes pour gérer les affichages par l'admin et ses représentants
    path('liste_admin', liste_admin, name="liste_admin"),
    path('liste_salarie', liste_salarie, name="liste_salarie"),
    path('liste_partenaire', liste_partenaire, name="liste_partenaire"),
    path('liste_client', liste_client, name="liste_client"), 
    path('liste_role', liste_role, name="liste_role"), 
    path('contrats_en_cours/<int:salarie_id>/', contrats_en_cours, name="contrats_en_cours"),
    path('contrats_termines/<int:salarie_id>/', contrats_termines, name="contrats_termines"),
    path('fiche_paie_payer/<int:salarie_id>/', fiche_paie_payer, name="fiche_paie_payer"),
    path('fiche_paie_impayer/<int:salarie_id>/', fiche_paie_impayer, name="fiche_paie_impayer"),
]

