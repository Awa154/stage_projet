var el = document.getElementById("wrapper");
    var toggleButton = document.getElementById("menu-toggle");

    toggleButton.onclick = function () {
        el.classList.toggle("toggled");
    };

    document.addEventListener('DOMContentLoaded', function() {
        var dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="collapse"]'))
        var dropdownList = dropdownTriggerList.map(function (dropdownTriggerEl) {
            return new bootstrap.Collapse(dropdownTriggerEl, {
                toggle: false
            })
        })
    });


    document.addEventListener("DOMContentLoaded", function() {
        // Sélectionne tous les liens de la barre latérale
        const navLinks = document.querySelectorAll('.nav-link');
    
        // Fonction pour gérer l'ajout de la classe 'active'
        function setActiveLink(link) {
            // Supprime la classe 'active' de tous les liens
            navLinks.forEach(link => link.classList.remove('active'));
            // Ajoute la classe 'active' au lien cliqué
            link.classList.add('active');
        }
    
        // Ajoute un événement de clic à chaque lien
        navLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                // Empêche le comportement par défaut pour les liens qui ne naviguent pas
                if (this.getAttribute('href') === '#') {
                    event.preventDefault();
                }
                // Gère la mise à jour de la classe 'active'
                setActiveLink(this);
            });
        });
    
        // Vérifie si un lien doit rester actif après le rechargement
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            if (link.getAttribute('href') !== '#' && link.getAttribute('href').includes(currentPath)) {
                setActiveLink(link);
            }
        });
    });

