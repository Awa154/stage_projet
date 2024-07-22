from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse

from hrWeb.settings import EMAIL_HOST_USER
from .models import Clause, Client, Competence, Compte, Contrat, EmailSettings, Entreprise, FicheDePaie, Admin, Departement, Role, Salarie
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
import random
import string
from django.db.models import Q
from django.core.mail import get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.db.models import Count

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
    clients = Compte.objects.select_related('role').filter(role__nom_role="Client")
    
    # Statistiques
    total_comptes = comptes.count()
    total_salaries =salaries.count()
    total_partners = entreprises.count()
    total_clients=clients.count()
    context = {
        'total_comptes': total_comptes,
        'total_salaries': total_salaries,
        'total_partners':total_partners,
        'total_clients':total_clients,
    }
    return render(request,'pages/admin/pages/dashboard/home.html', context)

#Fonction pour retourner la vue vers la page d'accueil
def home_salarie(request):
    return render(request,'pages/salarie/dashboard/home.html')

#Fonction pour retourner la vue vers la page d'accueil
def home_entreprise(request):
    return render(request,'pages/entreprise/dashboard/home.html')

#Fonction pour retourner la vue vers la page d'accueil
def home_client(request):
    return render(request,'pages/client/dashboard/home.html')

#Fonction pour retourner la vue vers la page d'accueil
def home_test(request):
    return render(request,'pages/admin/pages/dashboard/test.html')

#Création de la vue pour créer un département
def creer_departement(request):
    if request.method == 'POST':
        nom_dep = request.POST['nom_dep']

        departement = Departement.objects.create(
            nom_dep=nom_dep,
        )
        messages.success(request, 'Le département a été ajouté avec succès.')
        return redirect('creer_departement')

    return render(request, 'pages/admin/pages/creer/creer_departement.html')

#Création de la vue pour créer un rôle
def creer_role(request):
    if request.method == 'POST':
        nom_role = request.POST['nom_role']
        niv_permission = request.POST['niv_permission']
        acce_page = request.POST['acce_page']

        role = Role.objects.create(
            nom_role=nom_role,
            niv_permission=niv_permission,
            acce_page=acce_page
        )
        messages.success(request, 'Le rôle a été créé avec succès.')
        return redirect('creer_role')

    return render(request, 'pages/admin/pages/creer/creer_role.html')

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

# Fonction pour retourner la vue vers la page de création d'admin
def creer_admin(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = generer_nom_utilisateur()
        email = request.POST['email']
        sexe = request.POST['sexe']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
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
            return redirect('creer_admin')
        
        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=make_password(mot_de_passe),
            email=email,
            sexe=sexe,
            adresse=adresse,
            telephone=telephone,
            role=role,
        )
        
        # Envoyer l'email avec les identifiants de connexion
        if email:
            envoyer_email(
                subject="Bienvenue sur HrBridge",
                message=f'Bienvenue {nom_admin} {prenom_admin},\n\nVotre compte a été créé.\n\nVoici vos identifiants de connexion.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                recipient_list=[email]
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass
        
            nom_admin = request.POST['nom_admin']
            prenom_admin = request.POST['prenom_admin']

            Admin.objects.create(
                compte=compte,
                nom_admin=nom_admin,
                prenom_admin=prenom_admin,
            )
        messages.success(request, 'Le compte a été ajouté avec succès.')
        return redirect('creer_admin')
    
    roles = Role.objects.all()
    departements = Departement.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_admin.html', {'departements': departements, 'roles': roles})


# Fonction pour retourner la vue vers la page de création de salarié
def creer_salarie(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = generer_nom_utilisateur()
        email = request.POST['email']
        sexe = request.POST['sexe']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
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
            return redirect('creer_salarie')
        
        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=make_password(mot_de_passe),
            email=email,
            sexe=sexe,
            adresse=adresse,
            telephone=telephone,
            role=role,
        )
        
        # Envoyer l'email avec les identifiants de connexion
        if email:
            envoyer_email(
                subject="Bienvenue sur HrBridge",
                message=f'Bienvenue {nom_salarie} {prenom_salarie},\n\nVotre compte a été créé.\n\nVoici vos identifiants de connexion.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                recipient_list=[email]
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        # Créer le modèle associé basé sur le rôle de l'utilisateur
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
                return redirect('creer_salarie')
            
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
                
        messages.success(request, 'Le compte a été ajouté avec succès.')
        return redirect('creer_salarie')
    
    roles = Role.objects.all()
    departements = Departement.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_salarie.html', {'departements': departements, 'roles': roles})

# Fonction pour retourner la vue vers la page de création de compte
def creer_partenaire(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = generer_nom_utilisateur()
        email = request.POST['email']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
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
            return redirect('creer_partenaire')
        
        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=make_password(mot_de_passe),
            email=email,
            adresse=adresse,
            telephone=telephone,
            role=role,
        )
        
        # Envoyer l'email avec les identifiants de connexion
        if email:
            envoyer_email(
                subject="Bienvenue sur HrBridge",
                message=f'Nous souhaitons la bienvenue à {nom_entreprise} sur notre plateforme,\n\nVotre compte a été créé.\n\nVoici vos identifiants de connexion.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                recipient_list=[email]
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        # Créer le modèle associé basé sur le rôle de l'utilisateur
            nom_entreprise = request.POST.get('nom_entreprise')
            secteur_activite = request.POST.get('secteur_activite')
            site_web = request.POST.get('site_web')
            
            Entreprise.objects.create(
                compte=compte,
                nom_entreprise=nom_entreprise,
                secteurActivite=secteur_activite,
                site_web=site_web,
            )
        messages.success(request, 'Le compte a été ajouté avec succès.')
        return redirect('creer_partenaire')
    
    roles = Role.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_partenaire.html', {'roles': roles})

# Fonction pour retourner la vue vers la page de création de compte
def creer_client(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = generer_nom_utilisateur()
        email = request.POST['email']
        sexe = request.POST['sexe']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
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
            return redirect('creer_client')
        
        compte = Compte.objects.create(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=make_password(mot_de_passe),
            email=email,
            sexe=sexe,
            adresse=adresse,
            telephone=telephone,
            role=role,
        )
        
        # Envoyer l'email avec les identifiants de connexion
        if email:
            envoyer_email(
                subject="Bienvenue sur HrBridge",
                message=f'Nous souhaitons la bienvenue à {nom_client} {prenom_client} sur notre plateforme,\n\nVotre compte a été créé.\n\nVoici vos identifiants de connexion.\n\nNom d\'utilisateur: {nom_utilisateur}\nMot de passe: {mot_de_passe}\n\nCordialement,\nL\'équipe',
                recipient_list=[email]
            )
        else:
            # Logique d'envoi par WhatsApp (à implémenter)
            pass

        # Créer le modèle associé basé sur le rôle de l'utilisateur
            nom_client = request.POST.get('nom_client')
            prenom_client = request.POST.get('prenom_client')
            entreprise_id = request.POST('entreprise')
            
            entreprise_affilier = Entreprise.objects.get(id=entreprise_id)
            
            Client.objects.create(
                compte=compte,
                nom_client=nom_client,
                prenom_client=prenom_client,
                entreprise_affilier=entreprise_affilier
                
            )
        messages.success(request, 'Le compte a été ajouté avec succès.')
        return redirect('creer_client')
    
    roles = Role.objects.all()
    entreprises = Entreprise.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_client.html', {'entreprises': entreprises, 'roles': roles})

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

        if not compte.is_active:
            messages.error(request, "Votre compte est désactivé.")
            return render(request, "pages/auth/pages/login.html")

        # Vérifier le mot de passe
        if check_password(mot_de_passe, compte.mot_de_passe):
            # Définir la session
            request.session['user_id'] = compte.id
            request.session['user_nom_utilisateur'] = compte.nom_utilisateur

            # Redirection basée sur l'accès de l'utilisateur
            if compte.role.acce_page == 'AD':
                return redirect('home_admin')
            elif compte.role.acce_page == 'SA':
                return redirect('home_salarie')
            elif compte.role.acce_page == 'EN':
                return redirect('home_entreprise')
            elif compte.role.acce_page == 'CL':
                return redirect('home_client')
            else:
                messages.error(request, "Aucune page d'accès définie pour ce rôle.")
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

#Fonction pour changer le mot de passe en cas d'oublie
def oublier_mot_de_passe(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = Compte.objects.get(email=email)
            temp_password = generer_mot_de_passe()
            user.mot_de_passe = make_password(generer_mot_de_passe)
            user.save()
            
            # Envoyer l'email avec les identifiants de connexion
            subject = "HrBridge"
            message = 'Votre mot de passe temporaire',f'Votre nouveau mot de passe temporaire est : {temp_password}\nVeuillez le changer après vous être connecté.',
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

            messages.success(request, "Un mot de passe temporaire vous a été envoyé par email.")
            return redirect('connexion')
        except Compte.DoesNotExist:
            messages.error(request, "Aucun utilisateur trouvé avec cet email.")
            
    return render(request, "pages/auth/pages/forget_password.html")

#Fonction pour modifier son mot de passe
def changer_mot_de_passe(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')

    user = Compte.objects.get(id=user_id)

    if request.method == 'POST':
        ancien_mot_de_passe = request.POST.get('ancien_mot_de_passe')
        nouveau_mot_de_passe = request.POST.get('nouveau_mot_de_passe')
        confirmer_mot_de_passe = request.POST.get('confirmer_mot_de_passe')

        if not check_password(ancien_mot_de_passe, user.mot_de_passe):
            messages.error(request, "Le mot de passe actuel est incorrect.")
        elif nouveau_mot_de_passe != confirmer_mot_de_passe:
            messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
        else:
            user.mot_de_passe = make_password(nouveau_mot_de_passe)
            user.save()
            messages.success(request, "Mot de passe changé avec succès.")
            # Redirection basée sur l'accès de l'utilisateur
            if user.role.acce_page == "AD":
                return redirect('profile_admin')
            elif user.role.acce_page == "SA":
                return redirect('profile_salarie')
            elif user.role.acce_page == "EN":
                return redirect('profile_entreprise')
            elif user.role.acce_page == "CL":
                return redirect('profile_client')
            else:
                return redirect('connexion')

    return render(request, 'pages/auth/pages/change_password.html')

#Fonction pour la vue du profile
def profile_admin(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')

    user = get_object_or_404(Compte, id=user_id)

    if not hasattr(user, 'role') or user.role.acce_page != "AD":
        messages.error(request, "Vous n'avez pas les droits d'accès à cette page.")
        return redirect('home_admin')

    try:
        admin_info = Admin.objects.get(compte=user)
    except Admin.DoesNotExist:
        messages.error(request, "Les informations administratives n'ont pas été trouvées.")
        return redirect('home_admin')

    if request.method == 'POST':
        nom_utilisateur = request.POST.get('nom_utilisateur')
        nom_admin = request.POST.get('nom_admin')
        prenom_admin = request.POST.get('prenom_admin')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')

        if Compte.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà.")
        elif Compte.objects.filter(telephone=telephone).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec ce téléphone existe déjà.")
        else:
            user.nom_utilisateur = nom_utilisateur
            user.email = email
            user.adresse = adresse
            user.telephone = telephone
            user.save()

            admin_info.nom_admin = nom_admin
            admin_info.prenom_admin = prenom_admin
            admin_info.save()

            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_admin')
        
    return render(request, 'pages/admin/pages/dashboard/profile.html', {'user': user, 'admin_info': admin_info})

def profile_salarie(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')

    user = get_object_or_404(Compte, id=user_id)

    if not hasattr(user, 'role') or user.role.acce_page != "SA":
        messages.error(request, "Vous n'avez pas les droits d'accès à cette page.")
        return redirect('home_salarie')

    try:
        salarie_info = Salarie.objects.get(compte=user)
    except Salarie.DoesNotExist:
        messages.error(request, "Les informations du salarié n'ont pas été trouvées.")
        return redirect('home_salarie')

    if request.method == 'POST':
        nom_utilisateur = request.POST.get('nom_utilisateur')
        nom_salarie = request.POST.get('nom_salarie')
        prenom_salarie = request.POST.get('prenom_salarie')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')

        if Compte.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà.")
        elif Compte.objects.filter(telephone=telephone).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec ce téléphone existe déjà.")
        else:
            user.nom_utilisateur = nom_utilisateur
            user.email = email
            user.adresse = adresse
            user.telephone = telephone
            user.save()

            salarie_info.nom_salarie = nom_salarie
            salarie_info.prenom_salarie = prenom_salarie
            salarie_info.save()

            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_salarie')

    return render(request, 'pages/salarie/dashboard/profile.html', {'user': user, 'salarie_info': salarie_info})

def profile_entreprise(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')

    user = get_object_or_404(Compte, id=user_id)

    if not hasattr(user, 'role') or user.role.acce_page != "EN":
        messages.error(request, "Vous n'avez pas les droits d'accès à cette page.")
        return redirect('home_entreprise')

    try:
        entreprise_info = Entreprise.objects.get(compte=user)
    except Entreprise.DoesNotExist:
        messages.error(request, "Les informations de l'entreprise n'ont pas été trouvées.")
        return redirect('home_entreprise')

    if request.method == 'POST':
        nom_utilisateur = request.POST.get('nom_utilisateur')
        nom_entreprise = request.POST.get('nom_entreprise')
        secteur_activite = request.POST.get('secteur_activite')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        site_web = request.POST.get('site_web')

        if Compte.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà.")
        elif Compte.objects.filter(telephone=telephone).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec ce téléphone existe déjà.")
        else:
            user.nom_utilisateur = nom_utilisateur
            user.email = email
            user.adresse = adresse
            user.telephone = telephone
            
            user.save()

            entreprise_info.nom_entreprise = nom_entreprise
            entreprise_info.secteurActivite = secteur_activite
            entreprise_info.site_web = site_web
            entreprise_info.save()

            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_entreprise')

    return render(request, 'pages/entreprise/dashboard/profile.html', {'user': user, 'entreprise_info': entreprise_info})

def profile_client(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')

    user = get_object_or_404(Compte, id=user_id)

    if not hasattr(user, 'role') or user.role.acce_page != "CL":
        messages.error(request, "Vous n'avez pas les droits d'accès à cette page.")
        return redirect('home_client')

    try:
        client_info = Client.objects.get(compte=user)
    except Client.DoesNotExist:
        messages.error(request, "Les informations du client n'ont pas été trouvées.")
        return redirect('home_client')

    if request.method == 'POST':
        nom_utilisateur = request.POST.get('nom_utilisateur')
        nom_client = request.POST.get('nom_client')
        prenom_client = request.POST.get('prenom_client')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        entreprise_affilier = request.POST.get('entreprise_affilier')

        if Compte.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà.")
        elif Compte.objects.filter(telephone=telephone).exclude(id=user.id).exists():
            messages.error(request, "Un utilisateur avec ce téléphone existe déjà.")
        else:
            user.nom_utilisateur = nom_utilisateur
            user.email = email
            user.adresse = adresse
            user.telephone = telephone
            user.save()

            client_info.nom_client = nom_client
            client_info.prenom_client = prenom_client
            client_info.entreprise_affilier = entreprise_affilier
            client_info.save()

            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile_client')

    return render(request, 'client/profile.html', {'user': user, 'client_info': client_info})

#Fonction pour activé ou désactivé un compte
def statut(request, user_id):
    compte = Compte.objects.get(id=user_id)
    compte.is_active = not compte.is_active
    compte.save()
    messages.success(request, f"Le statut de {compte.nom_utilisateur} a été mis à jour.")
    # Redirection basée sur l'accès de l'utilisateur
    if compte.role.acce_page == "AD":
        return redirect('liste_admin')
    elif compte.role.acce_page == "SA":
        return redirect('liste_salarie')
    elif compte.role.acce_page == "EN":
        return redirect('liste_partenaire')
    elif compte.role.acce_page == "CL":
        return redirect('liste_client')
    else:
        return redirect('home_admin')

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
        
        clauses = request.POST.getlist('clauses')
        for clause in clauses:
            Clause.objects.create(contrat=contrat, clause=clause)

        messages.success(request, 'Le contrat a été établie avec succès.')
        return redirect('creer_contrat')
    salaries = Salarie.objects.all()
    entreprises = Entreprise.objects.all()
    return render(request, 'pages/admin/pages/creer/creer_contrat.html', {'salaries': salaries, 'entreprises': entreprises})

#Création de la vue pour affecter un salarié 
def affecter_salarie(request, salarie_id):
    salarie = get_object_or_404(Salarie, id=salarie_id)
    if request.method == 'POST':
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
        return redirect('affecter_salare')
    entreprises = Entreprise.objects.all()
    return render(request, 'pages/admin/pages/liste/liste_salarie.html', {'salarie': salarie, 'entreprises': entreprises})


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


#Fonction pour retourner la vue vers la page de la liste des administrateurs
def liste_admin(request):
    admins = Admin.objects.select_related('compte').all()
    
    # Recherche
    query = request.GET.get('q')
    if query:
        admins = admins.filter(
            Q(nom_admin__icontains=query)|
            Q(prenom_admin__icontains=query)
        )

    context = {
        'admins': admins,
    }
    return render(request,'pages/admin/pages/liste/liste_admin.html', context)

#Fonction pour retourner la vue vers la page de la liste des salariés
def liste_salarie(request):
    salaries = Salarie.objects.select_related('compte').prefetch_related('competence_set').all()
    entreprises = Entreprise.objects.all()
    # Recherche
    query = request.GET.get('q')
    if query:
        salaries = salaries.filter(
            Q(nom_salarie__icontains=query)|
            Q(prenom_salarie__icontains=query)|
            Q(dateEmbauche__icontains=query)|
            Q(competence_set__competence__icontains=query)
        )

    context = {
        'salaries': salaries,
        'entreprises':entreprises
    }
    return render(request,'pages/admin/pages/liste/liste_salarie.html', context)

#Fonction pour retourner la vue vers la page de la liste des entreprises
def liste_partenaire(request):
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
    return render(request,'pages/admin/pages/liste/liste_partenaire.html',context)

#Fonction pour retourner la vue vers la page de la liste des entreprises
def liste_client(request):
    clients = Client.objects.select_related('compte').all()
    entreprises = Entreprise.objects.select_related('compte').all()

    # Recherche
    query = request.GET.get('q')
    if query:
        clients = clients.filter(
            Q(nom__icontains=query)
        )

    context = {
    'clients': clients,
    'entreprises': entreprises,
    }
    return render(request,'pages/admin/pages/liste/liste_client.html',context)

#Fonction pour retourner la vue vers la page de la liste des contrats
def liste_contrat(request):
    contrats = Contrat.objects.all()

    # Recherche
    query = request.GET.get('q')
    if query:
        contrats = contrats.filter(
            Q(date_debut__icontains=query)|
            Q(date_fin__icontains=query)
        )

    context = {
    'contrats': contrats
    }
    return render(request,'pages/admin/pages/liste/liste_contrat.html',context)

#Fonction pour retourner la vue vers la page de la liste des fiches de paies
def liste_fichePaie(request):
    departements = Departement.objects.annotate(total_employes=Count('salarie'))
    return render(request, 'pages/admin/pages/liste/liste_fichepaie.html', {'departements': departements})

#Fonction pour retourner la vue vers la page de la liste des contrats
def liste_departements(request):
    departements = Departement.objects.annotate(total_employes=Count('salarie'))
    return render(request, 'pages/admin/pages/liste/liste_departement.html', {'departements': departements})

#Fonction pour retourner la vue vers la page de la liste des salariés
def liste_role(request):
    roles = Role.objects.all()
    
    # Recherche
    query = request.GET.get('q')
    if query:
        roles = roles.filter(
            Q(nom_role__icontains=query)
        )

    context = {
        'roles': roles,
    }
    return render(request,'pages/admin/pages/liste/liste_role.html', context)

# Modifier un département
def modifier_departement(request, departement_id):
    departement = get_object_or_404(Departement, id=departement_id)

    if request.method == 'POST':
        nom_dep = request.POST.get('nom_dep')
        departement.nom_dep = nom_dep
        departement.save()
        messages.success(request, 'Le département a été mis à jour avec succès.')
        return redirect('liste_departements')   # Rediriger vers la liste des départements après modification

    return render(request, 'pages/admin/pages/liste/liste_departement.html', {'departement': departement})

# Modifier un rôle
def modifier_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)

    if request.method == 'POST':
        nom_role = request.POST.get('nom_role')
        niv_permission = request.POST.get('niv_permission')
        acce_page = request.POST.get('acce_page')
        role.nom_role = nom_role
        role.niv_permission = niv_permission
        role.acce_page = acce_page
        role.save()
        
        messages.success(request, 'Le rôle a été mis à jour avec succès.')
        return redirect('liste_role') # Rediriger vers la liste des rôles après modification

    return render(request, 'pages/admin/pages/liste/liste_role.html', {'role': role})

# Modifier un contrat
def modifier_contrat(request, contrat_id):
    contrat = get_object_or_404(Contrat, id=contrat_id)

    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        type_contrat = request.POST.get('type_contrat')
        mode_paiement = request.POST.get('mode_paiement')
        taux_horaire = request.POST.get('taux_horaire')
        heures_travail = request.POST.get('heures_travail')
        jours_travail = request.POST.get('jours_travail')
        salaire_mensuel = request.POST.get('salaire_mensuel')
        statut = request.POST.get('statut')
        salarie_id = request.POST.get('salarie')
        entreprise_id = request.POST.get('entreprise')
        
        # Convertir les champs numériques ou définir None si vide
        taux_horaire = float(taux_horaire) if taux_horaire else None
        heures_travail = int(heures_travail) if heures_travail else None
        jours_travail = int(jours_travail) if jours_travail else None
        salaire_mensuel = float(salaire_mensuel) if salaire_mensuel else None
        
        contrat.date_debut = date_debut
        contrat.date_fin = date_fin
        contrat.type_contrat = type_contrat
        contrat.mode_paiement = mode_paiement
        contrat.taux_horaire = taux_horaire
        contrat.heures_travail = heures_travail
        contrat.jours_travail = jours_travail
        contrat.salaire_mensuel = salaire_mensuel
        contrat.statut = statut
        contrat.salarie_id = salarie_id
        contrat.entreprise_id = entreprise_id
        contrat.save()
        
        messages.success(request, 'Le contrat a été mis à jour avec succès.')
        return redirect('liste_contrat') # Rediriger vers la liste des contrats après modification

    return render(request, 'pages/admin/pages/liste/liste_contrat.html', {'contrat': contrat})

#Fonction me permettant d'avoir tout les contrat en relations en avec un salarié
def contrats_en_cours(request, salarie_id):
    salarie = get_object_or_404(Salarie, id=salarie_id)
    contrats = Contrat.objects.filter(salarie=salarie, statut='actif')
    return render(request, 'pages/admin/pages/liste/liste_contrat_en_cours.html', {'contrats': contrats, 'salarie': salarie})

def contrats_termines(request, salarie_id):
    salarie = get_object_or_404(Salarie, id=salarie_id)
    contrats = Contrat.objects.filter(salarie=salarie, statut='terminer')
    return render(request, 'pages/admin/pages/liste/liste_contrat_terminer.html', {'contrats': contrats, 'salarie': salarie})

def fiche_paie_payer(request, salarie_id):
    salarie = get_object_or_404(Salarie, id=salarie_id)
    fiches_de_paie = FicheDePaie.objects.filter(salarie=salarie, montant__gt=0)
    return render(request, 'pages/admin/pages/liste/liste_fiche_paie_payer.html', {'fiches_de_paie': fiches_de_paie, 'salarie': salarie})

def fiche_paie_impayer(request, salarie_id):
    salarie = get_object_or_404(Salarie, id=salarie_id)
    fiches_de_paie = FicheDePaie.objects.filter(salarie=salarie, montant=0)
    return render(request, 'pages/admin/pages/liste/liste_fiche_paie_impayer.html', {'fiches_de_paie': fiches_de_paie, 'salarie': salarie})


#Fonction me permettant d'avoir tout les contrat en relations en avec un  partenaire
def contrats_en_cours_partenaire(request, entreprise_id):
    entreprise = get_object_or_404(Entreprise, id=entreprise_id)
    contrats = Contrat.objects.filter(entreprise=entreprise, statut='actif')
    return render(request, 'pages/admin/pages/liste/liste_contrat_en_cours_partenaire.html', {'contrats': contrats, 'entreprise': entreprise})

def contrats_termines_partenaire(request, entreprise_id):
    entreprise = get_object_or_404(Entreprise, id=entreprise_id)
    contrats = Contrat.objects.filter(entreprise=entreprise, statut='terminer')
    return render(request, 'pages/admin/pages/liste/liste_contrat_terminer_partenaire.html', {'contrats': contrats, 'entreprise': entreprise})

def fiche_paie_payer_partenaire(request, entreprise_id):
    entreprise = get_object_or_404(Entreprise, id=entreprise_id)
    fiches_de_paie = FicheDePaie.objects.filter(entreprise=entreprise, montant__gt=0)
    return render(request, 'pages/admin/pages/liste/liste_fiche_paie_payer_partenaire.html', {'fiches_de_paie': fiches_de_paie, 'entreprise': entreprise})

def fiche_paie_impayer_partenaire(request, entreprise_id):
    entreprise = get_object_or_404(Entreprise, id=entreprise_id)
    fiches_de_paie = FicheDePaie.objects.filter(entreprise=entreprise, montant=0)
    return render(request, 'pages/admin/pages/liste/liste_fiche_paie_impayer_partenaire.html', {'fiches_de_paie': fiches_de_paie, 'entreprise': entreprise})

#Fonction pour configurer les éméteurs d'envoie d'email
def configurer_email(request):
    email_settings, created = EmailSettings.objects.get_or_create(id=request.POST.get('id', 1))  # Adjust to fetch by id

    if request.method == 'POST':
        email_settings.host = request.POST.get('host')
        email_settings.port = request.POST.get('port')
        email_settings.host_user = request.POST.get('host_user')
        email_settings.host_password = request.POST.get('host_password')
        email_settings.use_tls = 'use_tls' in request.POST
        email_settings.use_ssl = 'use_ssl' in request.POST
        email_settings.save()

        messages.success(request, 'Email mis à jour avec success')
        return redirect('configurer_email')

    return render(request, 'pages/admin/setting/email.html', {'email_settings': email_settings})

#Fonction pour choisir l'email principale qui envoie les messages
def general_configuration(request):
    email_settings_list = EmailSettings.objects.all()
    if request.method == 'POST':
        selected_emetteur = request.POST.get('email_settings')
        return redirect('envoyer_email', emetteur_id=selected_emetteur)

    return render(request, 'pages/admin/setting/general.html', {'email_settings_list': email_settings_list})

# Fonction générale d'envoi des emails
def envoyer_email(subject, message, recipient_list, emetteur_id):
    try:
        # Récupération des paramètres de l'émetteur
        email_settings = EmailSettings.objects.get(id=emetteur_id)
        
        # Configuration de la connexion email
        email_backend = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=email_settings.host,
            port=email_settings.port,
            username=email_settings.host_user,
            password=email_settings.host_password,
            use_tls=email_settings.use_tls,
            use_ssl=email_settings.use_ssl,
            fail_silently=False,
        )

        # Envoi de l'email
        send_mail(
            subject,
            message,
            email_settings.host_user,
            recipient_list,
            connection=email_backend,
        )
        return True
    except EmailSettings.DoesNotExist:
        print("Email settings not configured.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False