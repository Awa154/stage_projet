from datetime import date, datetime
from django.db import models
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save

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
    nom_agent_entreprise= models.CharField(max_length=100, default="Aucun")
    prenom_agent_entreprise=models.CharField(max_length=200, default="Aucun")
    poste_agent= models.CharField(max_length=200, default="Agent")
    secteurActivite = models.CharField(max_length=100)
    site_web = models.URLField(max_length=255, blank=True)
    
class Client(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE, null=True, blank=True)
    entreprise_affilier = models.ForeignKey(Entreprise, on_delete=models.CASCADE,null=True, blank=True)
    nom_client = models.CharField(max_length=100)
    prenom_client = models.CharField(max_length=200)
    poste_occupe = models.CharField(max_length=100)
    
class Salarie(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    nom_salarie = models.CharField(max_length=100)
    prenom_salarie = models.CharField(max_length=200)
    dateNaissance = models.DateField(null=True, blank=True)
    annee_exp = models.PositiveIntegerField(null=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.dateNaissance.year - ((today.month, today.day) < (self.dateNaissance.month, self.dateNaissance.day))

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
    fonction_salarie= models.CharField(max_length=100, null=True, blank=True)
    mode_paiement = models.CharField(max_length=50, choices=PAIE_CHOICES)
    taux_horaire = models.FloatField(null=True, blank=True)
    heures_travail = models.IntegerField(null=True, blank=True)
    jours_travail = models.IntegerField(null=True, blank=True)
    taux_journalier = models.FloatField(null=True, blank=True)
    salaire_mensuel = models.FloatField(null=True, blank=True)
    est_terminer = models.BooleanField(default=False)
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Ensure date_fin is a date object
        if isinstance(self.date_fin, str):
            self.date_fin = datetime.strptime(self.date_fin, '%Y-%m-%d').date()

        if self.date_fin < date.today():
            self.est_terminer = True
            self.salarie.compte.is_active = False
            self.salarie.compte.save()
        super().save(*args, **kwargs)

@receiver(post_save, sender= Contrat)
def desactiver_compte_salarie(sender, instance, **kwargs):
    if instance.est_terminer:
        salarie = instance.salarie
        salarie.compte.is_active = False
        salarie.compte.save()
    
class Clause(models.Model):
    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE)
    clause = models.TextField(null=True, blank=True)

class FicheDePaie(models.Model):
    dateEmission = models.DateField(null=True, blank=True)
    echeance = models.DateField(null=True, blank=True)
    periode_de= models.DateField(null=True, blank=True)
    a_periode= models.DateField(null=True, blank=True)
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    nbre_jour_travail= models.IntegerField(null=True, blank=True)
    travail_supp= models.IntegerField(null=True, blank=True)
    travail_nuit= models.IntegerField(null=True, blank=True)
    nbre_jour_conger= models.IntegerField(null=True, blank=True)
    detail=models.TextField(blank=True)
    total_prime= models.FloatField(null=True, blank=True)
    total_indemnite= models.FloatField(null=True, blank=True)
    total_retenue= models.FloatField(null=True, blank=True)
    salaire_net = models.FloatField(null=True, blank=True)
    est_payer = models.BooleanField(default=False) 
    
    
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

class Rapport(models.Model):
    datePaiement = models.DateField()
    echeance = models.DateField()
    detail= models.TextField()
    montant = models.FloatField()
    statut = models.CharField(max_length=10, default='Impayer')
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

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
    
class EmailSettings(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    host_user = models.CharField(max_length=255)
    host_password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    def __str__(self):
        return f"Email Settings: {self.host}"

