from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    
    #Route vers les méthodes gérer par l'admin et ses représentants
    path('success', success, name="success"),
    path('creer_admin', creer_admin, name="creer_admin"),
    path('creer_departement', creer_departement, name="creer_departement"),
    path('creer_fichepaie', creer_fichepaie, name="creer_fichepaie"),
    path('creer_contrat', creer_contrat, name="creer_contrat"),
    path('ajouter_salarie', ajouter_salarie, name="ajouter_salarie"),
    path('ajouter_entreprise', ajouter_entreprise, name="ajouter_entreprise"),
    
]

