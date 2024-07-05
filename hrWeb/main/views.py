from django.shortcuts import render, redirect
from django.http import HttpResponse

from hrWeb.settings import EMAIL_HOST_USER
from .models import Competence, Compte, Contrat, Entreprise, FicheDePaie, Admin, Departement, Role, Salarie
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
import random
import string
from django.db.models import Q
# Create your views here.

# Ajouter une vue de succès simple
def success(request):
    return HttpResponse("L'action a été mener avec succès!")

#Fonction pour retourner la vue vers la page d'accueil de l'admin
def home(request):
    return render(request,'pages/home/home.html')

#Fonction pour retourner la vue vers la page d'accueil de l'admin
def home_admin(request):
    return render(request,'pages/admin/pages/dashboard/home.html')

#Fonction pour retourner la vue vers la page d'accueil
def home_salarie(request):
    return render(request,'pages/salarie/dashboard/home.html')

#Fonction pour retourner la vue vers la page d'accueil
def home_entreprise(request):
    return render(request,'pages/entreprise/dashboard/home.html')

#Fonction de connexion
def login(request):
    if request.method == "POST":
        nom_utilisateur = request.POST.get('nom_utilisateur')
        mot_de_passe = request.POST.get('mot_de_passe')
        # Récupérer l'utilisateur avec le nom d'utilisateur donné
        try:
            user = Compte.objects.get(nom_utilisateur=nom_utilisateur)
            
            if user.statut == 'inactif':
                messages.error(request, "Votre compte est désactivé.")
                return render(request, "pages/auth/pages/login.html")
            
            if check_password(mot_de_passe, user.mot_de_passe):
                # Créer une session pour l'utilisateur
                request.session['user_id'] = user.id
                # Redirection basée sur le type d'utilisateur
                if user.role == "Admin":
                    return redirect('home_admin')  # Rediriger vers la page d'administration
                elif user.role == "Salarié":
                    return redirect('home_salarie')  # Rediriger vers la page salarié
                elif user.role == "Entreprise partenaire":
                    return redirect('home_entreprise')  # Rediriger vers la page entreprise
                messages.success(request, "Vous êtes maintenant connecté!")
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        except Compte.DoesNotExist:
            messages.error(request, "Nom d'utilisateur ou mot de passe inexistent.")

    return render(request, "pages/auth/pages/login.html")

#Fonction de déconnexion
def logout(request):
    # Supprimez la session de l'utilisateur
    if 'user_id' in request.session:
        del request.session['user_id']
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')


#Vue permettant de générer automatiquement les mots de passes
def generer_mot_de_passe():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(8))

#Création de la vue pour créer un rôle
def creer_role(request):
    if request.method == 'POST':
        nom_role = request.POST['nom_role']
        niv_permission = request.POST['niv_permission']
        departement_id = request.POST['departement']
        departement = Departement.objects.get(id=departement_id)

        role = Role.objects.create(
            nom_role=nom_role,
            niv_permission=niv_permission,
            departement=departement
        )
        return redirect('success')
    departements = Departement.objects.all()

    return render(request, 'pages/admin/pages/creer/creer_role.html', {'departements': departements})

#Création de la vue permettant de créer un admin
def creer_admin(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST['nom_utilisateur']
        email = request.POST['email']
        sexe = request.POST['sexe']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()

        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            sexe=sexe,
            adresse=adresse,
            telephone=telephone,
            role=role,
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
        
        roles = Role.objects.all()
        return redirect('success')
    return render(request, 'pages/admin/pages/creer/creer_admin.html', {'roles': roles})

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
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()

        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            adresse=adresse,
            sexe=sexe,
            telephone=telephone,
            role=role,
            statut=statut
        )
        
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        date_naissance = request.POST['date_naissance']
        annee_exp = request.POST['annee_exp']
        departement_id = request.POST['departement']
        departement = Departement.objects.get(id=departement_id)

        salarie = Salarie.objects.create(
            nom=nom,
            prenom=prenom,
            dateNaissance=date_naissance,
            annee_exp=annee_exp,
            compte=compte,
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
    roles = Role.objects.all()
    departements = Departement.objects.all()
    return render(request, 'pages/admin/pages/creer/ajouter_salarie.html', {'departements': departements, 'roles': roles})

#Création de la vue permettant de créer le compte des entreprises
def ajouter_entreprise(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST['nom_utilisateur']
        email = request.POST['email']
        adresse = request.POST['adresse']
        sexe = request.POST['sexe']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()

        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            adresse=adresse,
            sexe=sexe,
            telephone=telephone,
            role=role,
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

    roles = Role.objects.all()
    return render(request, 'pages/admin/pages/creer/ajouter_entreprise.html', {'roles': roles})

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



#Fonction pour retourner la vue vers la page de la liste des salariés
def liste_salarie(request):
    salaries = Salarie.objects.select_related('compte').prefetch_related('competence_set').all()
    
    # Recherche
    query = request.GET.get('q')
    if query:
        salaries = salaries.filter(
            Q(nom__icontains=query)|
            Q(prenom__icontains=query)|
            Q(domaine__icontains=query)|
            Q(competence_set__competence__icontains=query)
        )

    context = {
        'salaries': salaries,
    }
    return render(request,'pages/admin/pages/liste/listeSalarie.html', context)

#Fonction pour retourner la vue vers la page de la liste des entreprises
def liste_entreprise(request):
    entreprises = Entreprise.objects.select_related('compte').all()

    # Recherche
    query = request.GET.get('q')
    if query:
        entreprises = entreprises.filter(
            Q(nom__icontains=query)
        )

    context = {
    'entreprises': entreprises,
    }
    return render(request,'pages/admin/pages/liste/listeEntreprise.html',context)

#Fonction pour retourner la vue vers la page de création de compte
def creer_compte(request):
    if request.method == "POST":
        error = []
        # Récupérer les données du formulaire
        nom_utilisateur = request.POST.get('nom_utilisateur')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        sexe = request.POST.get('sexe')
        telephone = request.POST.get('telephone')
        nom_role = request.POST.get('nom_role') 
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()
        
        # Vérifier l'unicité de l'email et du contact
        if Compte.objects.filter(email=email).exists():
            error.append("Un utilisateur avec cet email existe déjà.")
        if Compte.objects.filter(telephone=telephone).exists():
            error.append("Un utilisateur avec ce contact existe déjà.")
        
        # Afficher les erreurs
        if error:
            for err in error:
                messages.error(request, err)
            return redirect('creer_compte')
        
        try:
            nom_role = Role.objects.get(id=nom_role)
        except Role.DoesNotExist:
            messages.error(request, "Le rôle sélectionné n'existe pas.")
            return redirect('creer_compte')

        # Créer l'utilisateur
        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            email=email,
            adresse=adresse,
            sexe=sexe,
            telephone=telephone,
            nom_role=nom_role,
            statut=statut
        )
        
        # Envoyer l'email avec les identifiants de connexion
        subject = "Votre compte entreprise a été créé"
        message = f'Bonjour,\n\nVotre compte entreprise a été créé.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        if email:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        # Créer le modèle associé basé sur le rôle de l'utilisateur
        if nom_role.nom_role == "Salarié":
            nom_salarie = request.POST.get('nom_salarie')
            prenom_salarie = request.POST.get('prenom_salarie')
            date_naissance = request.POST.get('date_naissance')
            annee_exp = request.POST.get('annee_exp')
            departement_id = request.POST.get('departement')

            try:
                departement = Departement.objects.get(id=departement_id)
            except Departement.DoesNotExist:
                messages.error(request, "Le département sélectionné n'existe pas.")
                return redirect('creer_compte')

            salarie = Salarie.objects.create(
                nom_salarie= nom_salarie,
                prenom_salarie=prenom_salarie,
                dateNaissance=date_naissance,
                annee_exp=annee_exp,
                compte=compte,
                departement=departement
            )

            competences = request.POST.getlist('competences')
            for competence in competences:
                Competence.objects.create(salarie=salarie, competence=competence)
                    
        elif nom_role.nom_role == "Entreprise partenaire":
            nom_entreprise = request.POST.get('nom_entreprise')
            secteur_activite = request.POST.get('secteur_activite')
            site_web=request.POST.get('site_web')
            
            Entreprise.objects.create(
                nom_entreprise=nom_entreprise,
                secteurActivite=secteur_activite,
                site_web=site_web,
                compte=compte,
            )
        elif nom_role.nom_role == "Admin":
            nom_admin = request.POST.get('nom_admin')
            prenom_admin = request.POST.get('prenom_admin')

            Admin.objects.create(
                nom_admin=nom_admin,
                prenom_admin=prenom_admin,
                compte=compte,
            )

        return redirect('success')

    roles = Role.objects.all()
    departements = Departement.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_compte.html', {'departements': departements, 'roles': roles})