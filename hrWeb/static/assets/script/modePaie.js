// Gestion des champs de rôles
document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('mode_paiement');
    const heureFields = document.getElementById('heure-fields');
    const jourFields = document.getElementById('jour-fields');
    const moisFields = document.getElementById('mois-fields');

    roleSelect.addEventListener('change', function() {
        const selectedMode = this.value;
        heureFields.classList.add('hidden');
        jourFields.classList.add('hidden');
        moisFields.classList.add('hidden');

        if (selectedMode === 'H') {
            heureFields.classList.remove('hidden');
        } else if (selectedMode === 'J') {
            jourFields.classList.remove('hidden');
        } else if (selectedMode === 'M') {
            moisFields.classList.remove('hidden');
        }
    });
});