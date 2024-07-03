from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Compte, Contrat, Entreprise, FicheDePaie, Admin, Departement, Salarie
from django.core.mail import send_mail
from django.conf import settings
import random
import string
# Create your views here.

# Ajouter une vue de succès simple
def success(request):
    return HttpResponse("L'action a été mener avec succès!")

#Fonction pour retourner la vue vers la page d'accueil
def home(request):
    return render(request,'pages/admin/pages/dashboard/home.html')

#Vue permettant de générer automatiquement les mots de passes
def generer_mot_de_passe():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(8))

#Création de la vue permettant de créer un admin
def creer_admin(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST['nom_utilisateur']
        email = request.POST['email']
        sexe = request.POST['sexe']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()

        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            sexe=sexe,
            adresse=adresse,
            telephone=telephone,
            type_utilisateur='GES',
            statut=statut
        )

        nom = request.POST['nom']
        prenom = request.POST['prenom']

        admin = admin.objects.create(
            nom=nom,
            prenom=prenom,
            compte=compte,
        )

        # Envoyer les identifiants par email
        if email:
            send_mail(
                'Votre compte admin a été créé',
                f'Bonjour {prenom},\n\nVotre compte admin a été créé.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        return redirect('success')
    return render(request, 'pages/admin/pages/creer/creer_admin.html')

#Création de la vue pour créer un département
def creer_departement(request):
    if request.method == 'POST':
        nom_dep = request.POST['nom_dep']

        departement = Departement.objects.create(
            nom_dep=nom_dep,
        )
        return redirect('success')

    return render(request, 'pages/admin/pages/creer/creer_departement.html')

#Création de la vue permettant de créer le compte d'un salirié
def ajouter_salarie(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST['nom_utilisateur']
        email = request.POST['email']
        adresse = request.POST['adresse']
        sexe = request.POST['sexe']
        telephone = request.POST['telephone']
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()

        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            adresse=adresse,
            sexe=sexe,
            telephone=telephone,
            type_utilisateur='EM',
            statut=statut
        )
        
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        date_naissance = request.POST['date_naissance']
        annee_exp = request.POST['annee_exp']
        departement_id = request.POST['departement']
        admin_id = request.POST['admin']
        departement = Departement.objects.get(id=departement_id)
        admin = admin.objects.get(id=admin_id)

        salarie = Salarie.objects.create(
            nom=nom,
            prenom=prenom,
            dateNaissance=date_naissance,
            annee_exp=annee_exp,
            compte=compte,
            admin=admin,
            departement=departement
        )

        # Envoyer les identifiants par email
        if email:
            send_mail(
                'Votre compte salarié a été créé',
                f'Bonjour {prenom},\n\nVotre compte salarié a été créé.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        return redirect('success')
    departements = Departement.objects.all()
    admins = admin.objects.all()
    return render(request, 'pages/admin/pages/creer/ajouter_salarie.html', {'departements': departements, 'admins': admins})

#Création de la vue permettant de créer le compte des entreprises
def ajouter_entreprise(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST['nom_utilisateur']
        email = request.POST['email']
        adresse = request.POST['adresse']
        sexe = request.POST['sexe']
        telephone = request.POST['telephone']
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()

        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            adresse=adresse,
            sexe=sexe,
            telephone=telephone,
            type_utilisateur='EN',
            statut=statut
        )

        nom = request.POST['nom']
        secteur_activite = request.POST['secteur_activite']
        admin_id = request.POST['admin']
        admin = admin.objects.get(id=admin_id)

        entreprise = Entreprise.objects.create(
            nom=nom,
            secteurActivite=secteur_activite,
            compte=compte,
            admin=admin
        )

        # Envoyer les identifiants par email
        if email:
            send_mail(
                'Votre compte entreprise a été créé',
                f'Bonjour,\n\nVotre compte entreprise a été créé.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        return redirect('success')

    admins = admin.objects.all()
    return render(request, 'pages/admin/pages/creer/ajouter_entreprise.html', {'admins': admins})

#Création de la vue pour créer les contrats 
def creer_contrat(request):
    if request.method == 'POST':
        salarie_id = request.POST['salarie']
        entreprise_id = request.POST['entreprise']
        date_debut = request.POST['date_debut']
        date_fin = request.POST['date_fin']
        type_contrat = request.POST['type_contrat']
        mode_paiement = request.POST['mode_paiement']
        taux_horaire = request.POST.get('taux_horaire', None)
        heures_travail = request.POST.get('heures_travail', None)
        jours_travail = request.POST.get('jours_travail', None)
        salaire_mensuel = request.POST.get('salaire_mensuel', None)
        statut = 'actif'

        salarie = Salarie.objects.get(id=salarie_id)
        entreprise = Entreprise.objects.get(id=entreprise_id)

        contrat = Contrat.objects.create(
            salarie=salarie,
            entreprise=entreprise,
            date_debut=date_debut,
            date_fin=date_fin,
            type_contrat=type_contrat,
            mode_paiement=mode_paiement,
            taux_horaire=taux_horaire,
            heures_travail=heures_travail,
            jours_travail=jours_travail,
            salaire_mensuel=salaire_mensuel,
            statut=statut
        )
        contrat.save()

        return redirect('success')

    salaries = Salarie.objects.all()
    entreprises = Entreprise.objects.all()
    return render(request, 'creer_contrat.html', {'salaries': salaries, 'entreprises': entreprises})


def creer_fichepaie(request):
    if request.method == 'POST':
        salarie_id = request.POST['salarie']
        date_paiement = request.POST['date_paiement']
        salarie = Salarie.objects.get(id=salarie_id)

        fiche_de_paie = FicheDePaie.objects.create(
            salarie=salarie,
            datePaiement=date_paiement,
            montant=0  # Initialement à 0, sera calculé plus tard
        )

        montant_final = fiche_de_paie.calculer_montant_final()
        fiche_de_paie.montant = montant_final
        fiche_de_paie.save()

        return redirect('success')

    salaries = Salarie.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_fichepaie.html', {'salaries': salaries})