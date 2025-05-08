document.addEventListener('DOMContentLoaded', function() {
    // Automatische Textfeld-Erweiterung für die Projektbeschreibung
    const textarea = document.getElementById('{{ form.description.id }}');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
    
    // Form Validation
    const form = document.querySelector('form');
    const nameInput = document.getElementById('{{ form.name.id }}');
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        
        // Einfache Validierung für den Projektnamen
        if (!nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            if (!nameInput.nextElementSibling || !nameInput.nextElementSibling.classList.contains('invalid-feedback')) {
                const feedback = document.createElement('div');
                feedback.classList.add('invalid-feedback');
                feedback.textContent = 'Bitte geben Sie einen Projektnamen ein';
                nameInput.parentNode.insertBefore(feedback, nameInput.nextElementSibling);
            }
            isValid = false;
        } else {
            nameInput.classList.remove('is-invalid');
            nameInput.classList.add('is-valid');
        }
        
        if (!isValid) {
            event.preventDefault();
        }
    });
    
    // Entfernen der Fehlermeldung beim Tippen
    nameInput.addEventListener('input', function() {
        if (this.value.trim()) {
            this.classList.remove('is-invalid');
        }
    });
});