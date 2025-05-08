// JavaScript für Modal und Zeitsteuerung
document.addEventListener('DOMContentLoaded', function() {
    // Event-Listener für das Modal
    const modal = document.getElementById('changeEndDateModal_{{ project.id }}');
    if (modal) {
        modal.addEventListener('shown.bs.modal', function() {
            console.log('Modal opened for project {{ project.id }}');
        });
    }
    
    // Event-Listener für die Schnellauswahl-Buttons
    const quickSelectButtons = document.querySelectorAll('#changeEndDateModal_{{ project.id }} .quick-select-btn');
    
    quickSelectButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Werte aus dem Button abrufen
            const value = parseInt(this.getAttribute('data-value'));
            const unit = this.getAttribute('data-unit');
            
            console.log(`Quick select: +${value} ${unit}`);
            
            // Formular für die Schnellauswahl vorbereiten und absenden
            const adjustForm = document.getElementById('adjustForm_{{ project.id }}');
            
            // Versteckte Felder erstellen oder aktualisieren
            let valueInput = adjustForm.querySelector('input[name="value"]');
            if (!valueInput) {
                valueInput = document.createElement('input');
                valueInput.type = 'hidden';
                valueInput.name = 'value';
                adjustForm.appendChild(valueInput);
            }
            valueInput.value = value;
            
            let unitInput = adjustForm.querySelector('input[name="unit"]');
            if (!unitInput) {
                unitInput = document.createElement('input');
                unitInput.type = 'hidden';
                unitInput.name = 'unit';
                adjustForm.appendChild(unitInput);
            }
            unitInput.value = unit;
            
            // Formular absenden
            adjustForm.submit();
        });
    });
    
    // Formular-Validierung und Übermittlung
    const endDateForm = document.getElementById('endDateForm_{{ project.id }}');
    if (endDateForm) {
        endDateForm.addEventListener('submit', function(event) {
            const dateInput = this.querySelector('input[name="end_date"]');
            
            if (!dateInput.value) {
                event.preventDefault();
                alert('Bitte ein gültiges Datum eingeben.');
                return false;
            }
            
            console.log('Submitting form with end date:', dateInput.value);
        });
    }
    
    // Funktion zum Aktualisieren des Countdowns
    updateRemainingTime();
    // Alle 30 Sekunden aktualisieren
    setInterval(updateRemainingTime, 30000);
});

// Funktion zum Aktualisieren der verbleibenden Zeit via API
function updateRemainingTime() {
    const countdownTimer = document.getElementById('countdown-timer');
    const projectId = {{ project.id }};
    
    if (!countdownTimer) return;
    
    fetch(`/api/project/${projectId}/remaining-time`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Netzwerkantwort war nicht ok');
            }
            return response.json();
        })
        .then(data => {
            // Countdown-Badge aktualisieren
            countdownTimer.textContent = data.remaining_detailed;
            countdownTimer.className = `badge bg-${data.status}`;
            
            // Fortschrittsbalken aktualisieren, falls vorhanden
            const progressBar = document.getElementById('project-progress-bar');
            if (progressBar) {
                progressBar.className = `progress-bar bg-${data.status}`;
            }
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der verbleibenden Zeit:', error);
            countdownTimer.textContent = 'Fehler';
            countdownTimer.className = 'badge bg-danger';
        });

 // Mache das Kalendersymbol klickbar
    $(document).ready(function(){
        // Initialisiere den Datepicker
        $('.datepicker').datepicker({
            format: 'dd.mm.yy',
            autoclose: true,
            todayHighlight: true,
            language: 'de'
        });
        
        
        $('.date-icon-trigger').click(function(){
            $(this).parent().find('input').focus();
        });
    });