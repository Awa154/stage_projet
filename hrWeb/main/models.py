from django.db import models

class Compte(models.Model):
    SEXE_CHOICES = (
        ('H', 'Homme'),
        ('F', 'Femme'),
    )
    TYPE_CHOICES = (
        ('AD', 'Admin'),
        ('EM', 'Employe'),
        ('EN', 'Entreprise'),
    )
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    )
    nom_utilisateur = models.CharField(max_length=50)
    mot_de_passe = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    email = models.EmailField(null=True, blank=True)
    adresse = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    type_utilisateur = models.CharField(max_length=2, choices=TYPE_CHOICES)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)

    def __str__(self):
        return self.nom_utilisateur

    def envoyerIdentifiants(self):
        if self.email:
            # envoyer identifiants par email
            pass
        else:
            # envoyer identifiants par WhatsApp
            pass

class Departement(models.Model):
    nom_dep = models.CharField(max_length=100)

    def __str__(self):
        return self.nom_dep

class Admin(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=100)
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Entreprise(models.Model):
    nom = models.CharField(max_length=100)
    secteurActivite = models.CharField(max_length=100)
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nom

class Salarie(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=100)
    dateNaissance = models.DateField()
    dateEmbauche = models.DateTimeField(auto_now_add=True)
    annee_exp = models.IntegerField()
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Competence(models.Model):
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    competence = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.competence} ({self.salarie.nom} {self.salarie.prenom})"

class Contrat(models.Model):
    PAIE_CHOICES = (
        ('H', 'Heure'),
        ('J', 'Jour'),
        ('M', 'Mois'),
    )
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('terminer', 'Terminer'),
    )
    date_debut = models.DateField()
    date_fin = models.DateField()
    type_contrat = models.CharField(max_length=100)
    mode_paiement = models.CharField(max_length=50, choices=PAIE_CHOICES)
    taux_horaire = models.FloatField(null=True, blank=True)
    heures_travail = models.IntegerField(null=True, blank=True)
    jours_travail = models.IntegerField(null=True, blank=True)
    salaire_mensuel = models.FloatField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

    def __str__(self):
        return f"Contrat {self.id} - {self.salarie.nom} {self.salarie.prenom}"

class FicheDePaie(models.Model):
    salarie = models.ForeignKey(Salarie, on_delete=models.CASCADE)
    datePaiement = models.DateField()
    montant = models.FloatField()

    def __str__(self):
        return f"FicheDePaie {self.id} - {self.salarie.nom} {self.salarie.prenom}"
    
#Méthode pour calculer le salaire en fonction du mode payement d'un employé
def calculer_montant_final(self):
    contrat = Contrat.objects.filter(salarie=self.salarie, statut='actif').first()
    if not contrat:
        return 0
    if contrat.mode_paiement == 'H':
        return contrat.taux_horaire * contrat.heures_travail
    elif contrat.mode_paiement == 'J':
        return contrat.taux_horaire * 8 * contrat.jours_travail
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

    def __str__(self):
        return f"Demande {self.id} - {self.titre}"
