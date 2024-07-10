from django.shortcuts import render, redirect
from django.http import HttpResponse

from hrWeb.settings import EMAIL_HOST_USER
from .models import Competence, Compte, Contrat, Entreprise, FicheDePaie, Admin, Departement, Role, Salarie
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
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
    comptes = Compte.objects.select_related('role').all()
    salaries = Compte.objects.select_related('role').filter(role__nom_role="Salarié")
    entreprises = Compte.objects.select_related('role').filter(role__nom_role="Entreprise partenaire")
    
    # Statistiques
    total_comptes = comptes.count()
    total_salaries =salaries.count()
    total_partners = entreprises.count()
    context = {
        'total_comptes': total_comptes,
        'total_salaries': total_salaries,
        'total_partners':total_partners
    }
    return render(request,'pages/admin/pages/dashboard/home.html', context)

#Fonction pour retourner la vue vers la page d'accueil
def home_salarie(request):
    return render(request,'pages/salarie/dashboard/home.html')

#Fonction pour retourner la vue vers la page d'accueil
def home_entreprise(request):
    return render(request,'pages/entreprise/dashboard/home.html')

#Création de la vue pour créer un département
def creer_departement(request):
    if request.method == 'POST':
        nom_dep = request.POST['nom_dep']

        departement = Departement.objects.create(
            nom_dep=nom_dep,
        )
        return redirect('success')

    return render(request, 'pages/admin/pages/creer/creer_departement.html')

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

def generer_nom_utilisateur(length=12):
    characters = string.ascii_letters
    while True:
        nom_utilisateur = ''.join(random.choice(characters) for i in range(length))
        if not Compte.objects.filter(nom_utilisateur=nom_utilisateur).exists():
            return nom_utilisateur


# Vue permettant de générer automatiquement les mots de passe
def generer_mot_de_passe(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Fonction pour retourner la vue vers la page de création de compte
def creer_compte(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = generer_nom_utilisateur()
        email = request.POST['email']
        sexe = request.POST['sexe']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
        statut = 'actif'
        mot_de_passe = generer_mot_de_passe()
        
        # Valider les données
        errors = []
        # Vérifier l'unicité de l'email et du contact
        if Compte.objects.filter(email=email).exists():
            errors.append("Un utilisateur avec cet email existe déjà.")
        if Compte.objects.filter(telephone=telephone).exists():
            errors.append("Un utilisateur avec ce contact existe déjà.")
        
        if errors:
            for err in errors:
                messages.error(request, err)
            return redirect('creer_compte')
        
        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=make_password(mot_de_passe),
            email=email,
            sexe=sexe,
            adresse=adresse,
            telephone=telephone,
            role=role,
            statut=statut
        )
        
        # Envoyer l'email avec les identifiants de connexion
        subject = "Bienvenue sur HrBridge"
        message = f'Salutations,\n\nVotre compte a été créé.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe'
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
        if role.nom_role == "Admin":
            nom_admin = request.POST['nom_admin']
            prenom_admin = request.POST['prenom_admin']

            Admin.objects.create(
                compte=compte,
                nom_admin=nom_admin,
                prenom_admin=prenom_admin,
            )
            
        elif role.nom_role == "Salarié":
            nom_salarie = request.POST.get('nom_salarie')
            prenom_salarie = request.POST.get('prenom_salarie')
            dateNaissance = request.POST.get('dateNaissance')
            dateEmbauche = request.POST.get('dateEmbauche')
            annee_exp = request.POST.get('annee_exp')
            departement_id = request.POST.get('departement')
            
            try:
                departement = Departement.objects.get(id=departement_id)
            except Departement.DoesNotExist:
                messages.error(request, "Le département sélectionné n'existe pas.")
                return redirect('creer_compte')
            
            salarie = Salarie.objects.create(
                compte=compte,
                nom_salarie=nom_salarie,
                prenom_salarie=prenom_salarie,
                dateNaissance=dateNaissance,
                dateEmbauche=dateEmbauche,
                annee_exp=annee_exp,
                departement=departement
            )

            competences = request.POST.getlist('competences')
            for competence in competences:
                Competence.objects.create(salarie=salarie, competence=competence)
                    
        elif role.nom_role == "Entreprise partenaire":
            nom_entreprise = request.POST.get('nom_entreprise')
            secteur_activite = request.POST.get('secteur_activite')
            site_web = request.POST.get('site_web')
            
            Entreprise.objects.create(
                compte=compte,
                nom_entreprise=nom_entreprise,
                secteurActivite=secteur_activite,
                site_web=site_web,
            )
        messages.success(request, 'Le compte a été créé avec succès.')
        return redirect('creer_compte')
    
    roles = Role.objects.all()
    departements = Departement.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_compte.html', {'departements': departements, 'roles': roles})

#Fonction de connexion
def connexion(request):
    if request.method == 'POST':
        nom_utilisateur = request.POST.get('nom_utilisateur')
        mot_de_passe = request.POST.get('mot_de_passe')

        # Rechercher l'utilisateur par son nom d'utilisateur
        try:
            compte = Compte.objects.get(nom_utilisateur=nom_utilisateur)
        except Compte.DoesNotExist:
            messages.error(request, "Nom d'utilisateur incorrect.")
            return redirect('connexion')
        
        if compte.statut == 'inactif':
                messages.error(request, "Votre compte est désactivé.")
                return render(request, "pages/auth/pages/login.html")

        # Vérifier le mot de passe
        if check_password(mot_de_passe, compte.mot_de_passe):
            # Définir la session
            request.session['user_id'] = compte.id
            request.session['username'] = compte.nom_utilisateur 
            request.session['role_id'] = compte.role.id
            
            print("Role Name:", compte.id)
            print("Role Name id:", compte.role.id)
            # Redirection basée sur le rôle de l'utilisateur
            if compte.role.id == 1 :
                return redirect('home_admin')
            elif compte.role.id == 2 :
                return redirect('home_salarie')
            elif compte.role.id == 3 :
                return redirect('home_entreprise')
            else:
                messages.error(request, "Ce rôle d'utilisateur n'est pas pris en charge.")
                return redirect('connexion')
        else:
            messages.error(request, "Mot de passe incorrect.")
            return redirect('connexion')
    else:
        return render(request, "pages/auth/pages/login.html")

#Fonction de déconnexion
def deconnexion(request):
    # Supprimez la session de l'utilisateur
    if 'user_id' in request.session:
        del request.session['user_id']
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('connexion')


#Création de la vue pour créer les contrats 
def creer_contrat(request):
    if request.method == 'POST':
        salarie_id = request.POST['salarie']
        entreprise_id = request.POST['entreprise']
        date_debut = request.POST['date_debut']
        date_fin = request.POST['date_fin']
        type_contrat = request.POST['type_contrat']
        mode_paiement = request.POST['mode_paiement']
        taux_horaire = request.POST.get('taux_horaire')
        heures_travail = request.POST.get('heures_travail')
        jours_travail = request.POST.get('jours_travail')
        salaire_mensuel = request.POST.get('salaire_mensuel')
        statut = 'actif'
        
        # Convertir les champs numériques ou définir None si vide
        taux_horaire = float(taux_horaire) if taux_horaire else None
        heures_travail = int(heures_travail) if heures_travail else None
        jours_travail = int(jours_travail) if jours_travail else None
        salaire_mensuel = float(salaire_mensuel) if salaire_mensuel else None
        
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

        messages.success(request, 'Le contrat a été établie avec succès.')
        return redirect('creer_contrat')

    salaries = Salarie.objects.all()
    entreprises = Entreprise.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_contrat.html', {'salaries': salaries, 'entreprises': entreprises})


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

