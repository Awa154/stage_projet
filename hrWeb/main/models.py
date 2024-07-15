from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Departement(models.Model):
    nom_dep = models.CharField(max_length=100)

    def __str__(self):
        return self.nom_dep
    
class Role(models.Model):
    ACCE_PAGE = (
        ('AD', 'Page administrateur'),
        ('SA', 'Page salarié'),
        ('EN', 'Page des partenaires'),
        ('CL', 'Page des clients'),
    )
    nom_role = models.CharField(max_length=50)
    niv_permission=models.IntegerField()
    acce_page=models.CharField(max_length=60,choices=ACCE_PAGE, null=True, blank=True)


class Compte(models.Model):
    SEXE_CHOICES = (
        ('H', 'Homme'),
        ('F', 'Femme'),
    )
    nom_utilisateur = models.CharField(max_length=100)
    mot_de_passe = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, null=True, blank=True)
    email = models.EmailField(max_length=200, unique=True, null=True, blank=True)
    adresse = models.CharField(max_length=100, null=True, blank=True)
    telephone = PhoneNumberField(unique=True,null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    photo_profile = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Champ pour indiquer si le compte est actif

    def __str__(self):
        return self.email

    def envoyerIdentifiants(self):
        if self.email:
            # envoyer identifiants par email
            pass
        else:
            # envoyer identifiants par WhatsApp
            pass

class Admin(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    nom_admin = models.CharField(max_length=100)
    prenom_admin = models.CharField(max_length=150)

class Entreprise(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    nom_entreprise = models.CharField(max_length=100)
    secteurActivite = models.CharField(max_length=100)
    site_web = models.URLField(max_length=255, blank=True)
    
class Client(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE, null=True, blank=True)
    entreprise_affilier = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nom_client = models.CharField(max_length=100)
    prenom_client = models.CharField(max_length=150)
    poste_occupe = models.CharField(max_length=100)
    
class Salarie(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    nom_salarie = models.CharField(max_length=100)
    prenom_salarie = models.CharField(max_length=150)
    dateNaissance = models.DateField(null=True, blank=True)
    dateEmbauche = models.DateTimeField(null=True, blank=True)
    annee_exp = models.PositiveIntegerField(null=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)

class Competence(models.Model):
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    competence = models.CharField(max_length=100,null=True, blank=True)

class Contrat(models.Model):
    PAIE_CHOICES = (
        ('H', 'Heure'),
        ('J', 'Jour'),
        ('M', 'Mois'),
    )
    date_debut = models.DateField()
    date_fin = models.DateField()
    type_contrat = models.CharField(max_length=100)
    mode_paiement = models.CharField(max_length=50, choices=PAIE_CHOICES)
    taux_horaire = models.FloatField(null=True, blank=True)
    heures_travail = models.IntegerField(null=True, blank=True)
    jours_travail = models.IntegerField(null=True, blank=True)
    salaire_mensuel = models.FloatField(null=True, blank=True)
    statut = models.CharField(max_length=10, default='En cours')
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

class FicheDePaie(models.Model):
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    datePaiement = models.DateField()
    montant = models.FloatField()
    
#Méthode pour calculer le salaire en fonction du mode payement d'un employé
def calculer_montant_final(self):
    contrat = Contrat.objects.filter(salarie=self.salarie, statut='actif').first()
    if not contrat:
        return 0
    if contrat.mode_paiement == 'H':
        return contrat.taux_horaire * contrat.heures_travail
    elif contrat.mode_paiement == 'J':
        return contrat.taux_horaire * contrat.heures_travail * contrat.jours_travail
    elif contrat.mode_paiement == 'M':
        return contrat.salaire_mensuel
    return 0


class DemandeEmploye(models.Model):
    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('VALIDÉ', 'Validé'),
        ('REFUSÉ', 'Refusé'),
    )
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    details = models.TextField()
    competences_recherchees = models.CharField(max_length=255)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='EN_ATTENTE')

