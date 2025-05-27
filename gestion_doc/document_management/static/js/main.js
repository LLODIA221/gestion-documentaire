// Confirmation avant suppression
const deleteForms = document.querySelectorAll('form[action*="delete"], form[action*="supprimer"]');
deleteForms.forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            e.preventDefault();
        }
    });
});

// Focus automatique sur le premier champ de formulaire
window.addEventListener('DOMContentLoaded', function() {
    const firstInput = document.querySelector('form input, form select, form textarea');
    if (firstInput) {
        firstInput.focus();
    }
});

// Affichage/masquage mot de passe (si besoin, à compléter dans les templates)
function togglePassword(id) {
    const input = document.getElementById(id);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
} 