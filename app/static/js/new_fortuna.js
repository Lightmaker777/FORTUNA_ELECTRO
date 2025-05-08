
document.addEventListener('DOMContentLoaded', function() {
    // Hilfsfunktion zur Zeitberechnung
    function calculateHours(timeFrom, timeTo) {
        if (!timeFrom || !timeTo) return 0;
        
        const [fromHours, fromMinutes] = timeFrom.split(':').map(Number);
        const [toHours, toMinutes] = timeTo.split(':').map(Number);
        
        let hours = toHours - fromHours;
        let minutes = toMinutes - fromMinutes;
        
        if (minutes < 0) {
            hours--;
            minutes += 60;
        }
        
        return hours + (minutes / 60);
    }
    
    // Funktionen für die Arbeitseinsatz-Tabelle
    function updateAllHours() {
        let totalHours = 0;
        
        document.querySelectorAll('#arbeitseinsatz-table tbody tr').forEach(row => {
            const timeFrom = row.querySelector('.time-from').value;
            const timeTo = row.querySelector('.time-to').value;
            const hours = calculateHours(timeFrom, timeTo);
            
            row.querySelector('.time-hours').value = hours.toFixed(1);
            totalHours += hours;
        });
        
        document.querySelector('.total-hours').value = totalHours.toFixed(1);
        updateJsonData();
    }
    
    function addTimeRow() {
        const tbody = document.querySelector('#arbeitseinsatz-table tbody');
        const newRow = document.createElement('tr');
        
        // Klone die Options aus dem ursprünglichen Select
        const originalSelect = document.querySelector('.activity-select');
        const optionsHTML = Array.from(originalSelect.options)
            .map(opt => `<option value="${opt.value}">${opt.text}</option>`)
            .join('');
        
        newRow.innerHTML = `
            <td>
                <select class="form-select activity-select">
                    ${optionsHTML}
                </select>
            </td>
            <td>
                <input type="time" class="form-control time-from" value="00:00">
            </td>
            <td>
                <input type="time" class="form-control time-to" value="00:00">
            </td>
            <td>
                <input type="text" class="form-control time-hours" value="0.0" readonly>
            </td>
            <td class="text-center">
                <button type="button" class="btn btn-sm btn-outline-danger remove-row-btn">
                    <i class="fas fa-times"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(newRow);

        
        
        // Event-Listener hinzufügen
        const timeFromInput = newRow.querySelector('.time-from');
        const timeToInput = newRow.querySelector('.time-to');
        const activitySelect = newRow.querySelector('.activity-select');
        const removeBtn = newRow.querySelector('.remove-row-btn');
        
        timeFromInput.addEventListener('change', updateAllHours);
        timeToInput.addEventListener('change', updateAllHours);
        activitySelect.addEventListener('change', checkForOtherActivity);
        removeBtn.addEventListener('click', function() {
            tbody.removeChild(newRow);
            updateAllHours();
            updateRemoveButtons();
        });
        
        updateAllHours();
        updateRemoveButtons();
    }
    
    function updateRemoveButtons() {
        const rows = document.querySelectorAll('#arbeitseinsatz-table tbody tr');
        rows.forEach((row, index) => {
            const btn = row.querySelector('.remove-row-btn');
            if (rows.length > 1) {
                btn.style.display = 'block';
            } else {
                btn.style.display = 'none';
            }
        });
    }
    
    
// Modify the addMaterialRow function to avoid duplicating "Andere Materialien"
// Modify the addMaterialRow function to handle events properly
function addMaterialRow() {
    const tbody = document.querySelector('#material-table tbody');
    const newRow = document.createElement('tr');
    
    newRow.innerHTML = `
        <td style="background-color: #14304d !important; color: var(--accent) !important;">
            <select class="form-select material-name" style="background-color: #14304d !important; color: var(--accent) !important;">
                <option value="">Bitte auswählen</option>
                {% for value, label in material_choices %}
                <option value="{{ value }}">{{ label }}</option>
                {% endfor %}
                <option value="other">Andere Materialien</option>
            </select>
        </td>
        <td style="background-color: #14304d !important; color: var(--accent) !important;">
            <input type="text" class="form-control material-quantity" placeholder="z.B. 25m" style="background-color: #14304d !important; color: var(--accent) !important;">
        </td>
        <td class="text-center" style="background-color: #14304d !important; color: var(--accent) !important;">
            <button type="button" class="btn btn-sm btn-outline-danger remove-material-btn">
                <i class="fas fa-times"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(newRow);
    
    // Apply the dark styles to the new row
    const newSelects = newRow.querySelectorAll('.form-select');
    const newInputs = newRow.querySelectorAll('.form-control');
    
    newSelects.forEach(select => {
        select.style.setProperty('background-color', '#14304d', 'important');
        select.style.setProperty('color', 'var(--accent)', 'important');
    });
    
    newInputs.forEach(input => {
        input.style.setProperty('background-color', '#14304d', 'important');
        input.style.setProperty('color', 'var(--accent)', 'important');
    });
    
    // Event-Listener hinzufügen
    const removeBtn = newRow.querySelector('.remove-material-btn');
    removeBtn.addEventListener('click', function() {
        if (tbody.children.length > 1) {
            tbody.removeChild(newRow);
        } else {
            newRow.querySelector('.material-name').value = "";
            newRow.querySelector('.material-quantity').value = "";
        }
        checkForOtherMaterial();
        updateJsonData();
    });
    
    const materialSelect = newRow.querySelector('.material-name');
    materialSelect.addEventListener('change', function() {
        checkForOtherMaterial();
        updateJsonData();
    });
    
    newRow.querySelector('.material-quantity').addEventListener('input', updateJsonData);
    
    updateMaterialRemoveButtons();
    checkForOtherMaterial();
    updateJsonData();
}


function updateMaterialRemoveButtons() {
    const rows = document.querySelectorAll('#material-table tbody tr');
    rows.forEach((row, index) => {
        const btn = row.querySelector('.remove-material-btn');
        if (rows.length > 1) {
            btn.style.display = 'block';
        } else {
            btn.style.display = 'none';
        }
    });
}

// Fix the collectMaterialData function for form submission
function collectMaterialData() {
    const materialData = [];
    const rows = document.querySelectorAll('#material-table tbody tr');
    
    rows.forEach(row => {
        const materialSelect = row.querySelector('.material-name');
        const quantityInput = row.querySelector('.material-quantity');
        
        // Skip empty selections
        if (materialSelect.value === "") {
            return;
        }
        
        // Get the displayed text
        let materialText;
        if (materialSelect.value === 'other') {
            materialText = document.getElementById('{{ form.other_material.id }}').value.trim() || "Andere Materialien";
        } else {
            const selectedOption = materialSelect.options[materialSelect.selectedIndex];
            materialText = selectedOption ? selectedOption.text : "";
        }
        
        const quantity = quantityInput.value.trim();
        
        // Only add if it's not "Bitte auswählen" and at least one field is filled
        if ((materialText && materialText !== "Bitte auswählen") || quantity) {
            materialData.push({
                material: materialSelect.value,
                materialText: materialText,
                menge: quantity
            });
        }
    });
    
    return materialData;
}

// Fix the loadMaterialData function to handle other materials
function loadMaterialData() {
    const tbody = document.querySelector('#material-table tbody');
    tbody.innerHTML = ''; // Tabelle leeren
    
    let materialData = [];
    try {
        const materialDataJson = document.getElementById('material_data').value;
        if (materialDataJson) {
            materialData = JSON.parse(materialDataJson);
        }
    } catch (e) {
        console.error('Fehler beim Parsen der Material-Daten:', e);
        materialData = [];
    }
    
    // Wenn keine Daten vorhanden sind, eine leere Zeile hinzufügen
    if (materialData.length === 0) {
        addMaterialRow();
        return;
    }
    
    // Bestehende Daten laden
    materialData.forEach(item => {
        addMaterialRow();
        const lastRow = tbody.lastElementChild;
        const materialSelect = lastRow.querySelector('.material-name');
        const quantityInput = lastRow.querySelector('.material-quantity');
        
        // Set the value from the saved data
        materialSelect.value = item.material || '';
        quantityInput.value = item.menge || '';
        
        // If this is an "other" material, make sure to also populate the other_material field
        if (item.material === 'other' && item.materialText) {
            document.getElementById('{{ form.other_material.id }}').value = item.materialText;
        }
    });
    
    // Make sure to update the other material field visibility
    checkForOtherMaterial();
}

// Vor dem Absenden des Formulars ausführen
document.getElementById('timesheet-form').addEventListener('submit', function() {
    const materialData = collectMaterialData();
    document.getElementById('material_data').value = JSON.stringify(materialData);
});
    
    // Arbeitskraft-Feld bearbeitbar machen
    const arbeitskraftField = document.getElementById('arbeitskraft');
    
    // 1. readonly-Attribut entfernen
    arbeitskraftField.removeAttribute('readonly');
    
    // 2. Aussehen anpassen, damit es wie ein normales Eingabefeld aussieht
    arbeitskraftField.style.backgroundColor = "#fff";
    arbeitskraftField.style.cursor = "text";
    
    // 3. Optionalen Platzhalter hinzufügen
    arbeitskraftField.placeholder = "Name(n) der Arbeitskraft(e) eingeben";
    
    // 4. Hilfetext unter dem Feld hinzufügen
    const helpText = document.createElement('div');
    helpText.className = 'form-text';
    helpText.innerHTML = '<small>Mehrere Namen können mit Komma getrennt werden.</small>';
    arbeitskraftField.parentNode.appendChild(helpText);
    
    // 5. Feld in die Tab-Reihenfolge einfügen
    arbeitskraftField.tabIndex = 0;
    
    // JSON-Daten für das Formular sammeln
    function updateJsonData() {
        // Arbeitseinsatz-Daten sammeln
        const arbeitseinsatzData = [];
        document.querySelectorAll('#arbeitseinsatz-table tbody tr').forEach(row => {
            const activitySelect = row.querySelector('.activity-select');
            const activity = activitySelect.value;
            
            // Get the correct activity text - handle "andere" specially
            let activityText;
            if (activity === 'andere') {
                activityText = document.getElementById('{{ form.other_activity.id }}').value.trim() || "Andere Tätigkeit";
            } else {
                activityText = activitySelect.options[activitySelect.selectedIndex].text;
            }
            
            const von = row.querySelector('.time-from').value;
            const bis = row.querySelector('.time-to').value;
            const std = row.querySelector('.time-hours').value;
            
            arbeitseinsatzData.push({
                activity: activity,
                activityText: activityText,
                von: von,
                bis: bis,
                std: std
            });
        });
        
        // Material-Daten sammeln
    const materialData = [];
    document.querySelectorAll('#material-table tbody tr').forEach(row => {
        const materialSelect = row.querySelector('.material-name');
        const quantity = row.querySelector('.material-quantity').value.trim();
        
        // Skip empty selections
        if (materialSelect.value === "") {
            return;
        }
        
        let materialText;
        if (materialSelect.value === 'other') {
            // Wenn "Andere Materialien" ausgewählt ist, den Wert aus dem anderen Feld nehmen
            materialText = document.getElementById('{{ form.other_material.id }}').value.trim() || "Andere Materialien";
        } else {
            // Ansonsten den ausgewählten Text nehmen
            const selectedOption = materialSelect.options[materialSelect.selectedIndex];
            materialText = selectedOption ? selectedOption.text : "";
        }
        
        if ((materialText && materialText !== "Bitte auswählen") || quantity) {
            materialData.push({
                material: materialSelect.value,
                materialText: materialText,
                menge: quantity
            });
        }
    });
        

        // JSON-Daten in die versteckten Felder eintragen
        document.getElementById('arbeitseinsatz_data').value = JSON.stringify(arbeitseinsatzData);
        document.getElementById('material_data').value = JSON.stringify(materialData);
        
        // Haupt-Aktivität setzen (erste Zeile)
        if (arbeitseinsatzData.length > 0) {
            document.getElementById('activity-hidden').value = arbeitseinsatzData[0].activity;
        }
        
        // Vorschau aktualisieren
        updatePreview();
    }
    
    // Aktivität "Andere" Logik
    // Update the checkForOtherActivity function to handle input changes
function checkForOtherActivity() {
    let hasOtherActivity = false;
    document.querySelectorAll('.activity-select').forEach(select => {
        if (select.value === 'andere') {
            hasOtherActivity = true;
        }
    });
    
    const otherActivityDiv = document.getElementById('other-activity-div');
    if (hasOtherActivity) {
        otherActivityDiv.style.display = 'block';
        
        // Add event listener to update JSON data when the other activity field changes
        const otherActivityInput = document.getElementById('{{ form.other_activity.id }}');
        otherActivityInput.addEventListener('input', updateJsonData);
    } else {
        otherActivityDiv.style.display = 'none';
    }
}
   
// Modify the updatePreview function to handle empty material rows better
function updatePreview() {
    // Kopfdaten
    document.getElementById('preview-datum').textContent = document.getElementById('datum').value;
    document.getElementById('preview-bv').textContent = document.getElementById('bauvorhaben').value;
    document.getElementById('preview-arbeitskraft').textContent = document.getElementById('arbeitskraft').value;
    document.getElementById('preview-an-abreise').textContent = document.getElementById('an_abreise').value;

    // Arbeitseinsatz
    const arbeitseinsatzPreview = document.getElementById('preview-arbeitseinsatz');
    arbeitseinsatzPreview.innerHTML = '';
    let totalHours = 0;
    
    // Parse the JSON data to ensure we're using the correct activity text
    let arbeitseinsatzData = [];
    try {
        arbeitseinsatzData = JSON.parse(document.getElementById('arbeitseinsatz_data').value || '[]');
    } catch (e) {
        console.error('Fehler beim Parsen der Arbeitseinsatz-Daten:', e);
    }
    
    arbeitseinsatzData.forEach(item => {
        const activityText = item.activityText;
        const von = item.von;
        const bis = item.bis;
        const std = parseFloat(item.std) || 0;
        totalHours += std;
        
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${activityText}</td>
            <td>${von}</td>
            <td>${bis}</td>
            <td>${std.toFixed(1)}</td>
        `;
        arbeitseinsatzPreview.appendChild(newRow);
    });
    
    document.getElementById('preview-stunden-summe').textContent = totalHours.toFixed(1);

    // Material
    const materialPreview = document.getElementById('preview-material');
    materialPreview.innerHTML = '';
    
    // Get material data from JSON
    let materialData = [];
    try {
        materialData = JSON.parse(document.getElementById('material_data').value || '[]');
    } catch (e) {
        console.error('Fehler beim Parsen der Material-Daten:', e);
    }
    
    // If we have material data, display it
    if (materialData.length > 0) {
        materialData.forEach(item => {
            const materialText = item.materialText;
            const quantity = item.menge;
            
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${materialText}</td>
                <td>${quantity}</td>
            `;
            materialPreview.appendChild(newRow);
        });
    } else {
        // No materials entered
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="2" class="text-center text-muted">Keine Materialien eingetragen</td>
        `;
        materialPreview.appendChild(emptyRow);
    }

    // Notizen
    const notes = document.getElementById('{{ form.notes.id }}').value.trim();
    if (notes) {
        document.getElementById('preview-notes-section').style.display = 'block';
        document.getElementById('preview-notes').textContent = notes;
    } else {
        document.getElementById('preview-notes-section').style.display = 'none';
    }
}
    
    // Event-Listener für alle Inputs
    function setupEventListeners() {
        // Inputs im Formular
        const formInputs = document.querySelectorAll('#timesheet-form input, #timesheet-form select, #timesheet-form textarea');
        formInputs.forEach(input => {
            input.addEventListener('input', updateJsonData);
        });
        
        // Arbeitseinsatz-Tabelle
        document.querySelectorAll('.time-from, .time-to').forEach(input => {
            input.addEventListener('change', updateAllHours);
        });
        
        document.querySelectorAll('.activity-select').forEach(select => {
            select.addEventListener('change', checkForOtherActivity);
        });
        
        document.getElementById('add-row-btn').addEventListener('click', addTimeRow);
        document.getElementById('add-material-btn').addEventListener('click', addMaterialRow);
        
        // Material-Eingaben
        const materialInputs = document.querySelectorAll('.material-name, .material-quantity');
        materialInputs.forEach(input => {
            input.addEventListener('input', updateJsonData);
        });
        
    }
    
    // Zeichenzähler für Notizen
    function setupCharCounter() {
        const notesField = document.getElementById('{{ form.notes.id }}');
        const charCounter = document.getElementById('char-count');
        
        notesField.addEventListener('input', function() {
            const length = this.value.length;
            charCounter.textContent = length;
            
            if (length > 500) {
                charCounter.classList.add('text-danger');
                charCounter.classList.remove('text-muted');
            } else {
                charCounter.classList.remove('text-danger');
                charCounter.classList.add('text-muted');
            }
        });
    }
    
    // Keyboard-Shortcuts
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(event) {
            // Strg+S zum Speichern
            if (event.ctrlKey && event.key === 's') {
                event.preventDefault();
                document.getElementById('save-btn').click();
            }
            
            // Strg+P für Vorschau
            if (event.ctrlKey && event.key === 'p') {
                event.preventDefault();
                const previewBtn = document.querySelector('[data-bs-target="#previewModal"]');
                previewBtn.click();
            }
        });
    }
    
    // Form-Validierung
    function setupFormValidation() {
        const form = document.getElementById('timesheet-form');
        
        form.addEventListener('submit', function(event) {
            // Validiere Datum
            const datumInput = document.getElementById('datum');
            if (!datumInput.value) {
                event.preventDefault();
                datumInput.classList.add('is-invalid');
                datumInput.focus();
                return;
            }
            
            // Validiere Arbeitskraft
            const arbeitskraftInput = document.getElementById('arbeitskraft');
            if (!arbeitskraftInput.value.trim()) {
                event.preventDefault();
                arbeitskraftInput.classList.add('is-invalid');
                arbeitskraftInput.focus();
                return;
            }
            
            // Validiere Stunden
            const totalHours = parseFloat(document.querySelector('.total-hours').value);
            if (totalHours <= 0) {
                event.preventDefault();
                alert('Bitte tragen Sie mindestens eine Tätigkeit mit gültiger Zeiterfassung ein.');
                return;
            }
            
            // Validiere 'Andere Tätigkeit', falls ausgewählt
            const hasOtherActivity = Array.from(document.querySelectorAll('.activity-select')).some(select => select.value === 'andere');
            if (hasOtherActivity) {
                const otherActivityInput = document.getElementById('{{ form.other_activity.id }}');
                if (!otherActivityInput.value.trim()) {
                    event.preventDefault();
                    otherActivityInput.classList.add('is-invalid');
                    otherActivityInput.focus();
                    return;
                }
            }

             // Validiere 'Andere Materialien', falls ausgewählt
            const hasOtherMaterial = Array.from(document.querySelectorAll('.material-name')).some(select => select.value === 'other');
            if (hasOtherMaterial) {
                const otherMaterialInput = document.getElementById('{{ form.other_material.id }}');
                if (!otherMaterialInput.value.trim()) {
                    event.preventDefault();
                    otherMaterialInput.classList.add('is-invalid');
                    otherMaterialInput.focus();
                    return;
                }
            }
        });
    }
    
    // Bestätigungsdialog vor dem Verlassen der Seite
    function setupLeaveConfirmation() {
        let formChanged = false;
        
        // Überwachen aller Eingaben
        const formInputs = document.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            input.addEventListener('change', function() {
                formChanged = true;
            });
        });
        
        // Bestätigungsdialog anzeigen
        window.addEventListener('beforeunload', function(event) {
            if (formChanged) {
                event.preventDefault();
                event.returnValue = 'Sie haben ungespeicherte Änderungen. Möchten Sie die Seite wirklich verlassen?';
                return event.returnValue;
            }
        });
        
        // Bestätigung beim Abbrechen-Button deaktivieren
        document.querySelector('a.btn-outline-secondary').addEventListener('click', function() {
            formChanged = false;
        });
        
        // Bestätigung beim Speichern-Button deaktivieren
        document.getElementById('save-btn').addEventListener('click', function() {
            formChanged = false;
        });
    }
    
    // Datum automatisch auf heute setzen
    function setDateToday() {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        
        const datumInput = document.getElementById('datum');
        if (!datumInput.value) {
            datumInput.value = `${year}-${month}-${day}`;
        }
    }
    
    // Funktion für automatische Zeit-Vorschläge
    function setupTimeAutocomplete() {
        // Vorschläge für gängige Arbeitszeiten
        const commonStartTimes = ['07:00', '07:30', '08:00', '08:30', '09:00'];
        const commonEndTimes = ['16:00', '16:30', '17:00', '17:30', '18:00'];
        
        // Datalist für Von-Zeit
        const fromDatalistId = 'time-from-options';
        let fromDatalist = document.getElementById(fromDatalistId);
        
        if (!fromDatalist) {
            fromDatalist = document.createElement('datalist');
            fromDatalist.id = fromDatalistId;
            document.body.appendChild(fromDatalist);
            
            commonStartTimes.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                fromDatalist.appendChild(option);
            });
        }
        
        // Datalist für Bis-Zeit
        const toDatalistId = 'time-to-options';
        let toDatalist = document.getElementById(toDatalistId);
        
        if (!toDatalist) {
            toDatalist = document.createElement('datalist');
            toDatalist.id = toDatalistId;
            document.body.appendChild(toDatalist);
            
            commonEndTimes.forEach(time => {
                const option = document.createElement('option');
                option.value = time;
                toDatalist.appendChild(option);
            });
        }
        
        // Datalist den Eingabefeldern zuweisen
        document.querySelectorAll('.time-from').forEach(input => {
            input.setAttribute('list', fromDatalistId);
        });
        
        document.querySelectorAll('.time-to').forEach(input => {
            input.setAttribute('list', toDatalistId);
        });
    }
    
    // Autosave-Funktion
    function setupAutosave() {
        const AUTOSAVE_KEY = 'timesheet_autosave_' + window.location.pathname;
        const AUTOSAVE_INTERVAL = 30000; // 30 Sekunden
        
        // Wiederherstellen von Autosave-Daten
        try {
            const savedData = localStorage.getItem(AUTOSAVE_KEY);
            if (savedData) {
                const data = JSON.parse(savedData);
                
                // Datum und Kopfdaten wiederherstellen
                if (data.date) document.getElementById('datum').value = data.date;
                if (data.arbeitskraft) document.getElementById('arbeitskraft').value = data.arbeitskraft;
                if (data.an_abreise) document.getElementById('an_abreise').value = data.an_abreise;
                
                // Arbeitseinsatz wiederherstellen
                if (data.arbeitseinsatz && data.arbeitseinsatz.length > 0) {
                    // Erste Zeile füllen
                    const firstRow = document.querySelector('#arbeitseinsatz-table tbody tr');
                    firstRow.querySelector('.activity-select').value = data.arbeitseinsatz[0].activity;
                    firstRow.querySelector('.time-from').value = data.arbeitseinsatz[0].von;
                    firstRow.querySelector('.time-to').value = data.arbeitseinsatz[0].bis;
                    
                    // Weitere Zeilen hinzufügen
                    for (let i = 1; i < data.arbeitseinsatz.length; i++) {
                        addTimeRow();
                        const row = document.querySelectorAll('#arbeitseinsatz-table tbody tr')[i];
                        row.querySelector('.activity-select').value = data.arbeitseinsatz[i].activity;
                        row.querySelector('.time-from').value = data.arbeitseinsatz[i].von;
                        row.querySelector('.time-to').value = data.arbeitseinsatz[i].bis;
                    }
                }
                
                // Material wiederherstellen
                if (data.material && data.material.length > 0) {
                    // Erste Zeile füllen
                    const firstRow = document.querySelector('#material-table tbody tr');
                    firstRow.querySelector('.material-name').value = data.material[0].material;
                    firstRow.querySelector('.material-quantity').value = data.material[0].menge;
                    
                    // Weitere Zeilen hinzufügen
                    for (let i = 1; i < data.material.length; i++) {
                        addMaterialRow();
                        const row = document.querySelectorAll('#material-table tbody tr')[i];
                        row.querySelector('.material-name').value = data.material[i].material;
                        row.querySelector('.material-quantity').value = data.material[i].menge;
                    }
                }
                
                // Notizen wiederherstellen
                if (data.notes) document.getElementById('{{ form.notes.id }}').value = data.notes;
                
                // Interface aktualisieren
                updateAllHours();
                checkForOtherActivity();
                checkForOtherMaterial();
                
                // Autosave-Info anzeigen
                const autosaveInfo = document.createElement('div');
                autosaveInfo.className = 'alert alert-info animate__animated animate__fadeIn';
                autosaveInfo.innerHTML = `
                    <i class="fas fa-history me-2"></i>
                    <strong>Automatisch gespeicherte Daten wiederhergestellt.</strong>
                    <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Schließen"></button>
                `;
                document.querySelector('.card-body').insertBefore(autosaveInfo, document.querySelector('form'));
                
                // Alert nach 5 Sekunden ausblenden
                setTimeout(() => {
                    autosaveInfo.classList.add('animate__fadeOut');
                    setTimeout(() => autosaveInfo.remove(), 500);
                }, 5000);
            }
        } catch (error) {
            console.error('Fehler beim Wiederherstellen der Autosave-Daten:', error);
        }
        
        // Regelmäßiges Speichern
        setInterval(() => {
            try {
                // Daten sammeln
                const data = {
                    date: document.getElementById('datum').value,
                    arbeitskraft: document.getElementById('arbeitskraft').value,
                    an_abreise: document.getElementById('an_abreise').value,
                    arbeitseinsatz: JSON.parse(document.getElementById('arbeitseinsatz_data').value || '[]'),
                    material: JSON.parse(document.getElementById('material_data').value || '[]'),
                    notes: document.getElementById('{{ form.notes.id }}').value
                };
                
                // Im LocalStorage speichern
                localStorage.setItem(AUTOSAVE_KEY, JSON.stringify(data));
            } catch (error) {
                console.error('Fehler beim Autosave:', error);
            }
        }, AUTOSAVE_INTERVAL);
        
        // Beim erfolgreichen Absenden des Formulars Autosave löschen
        document.getElementById('timesheet-form').addEventListener('submit', function() {
            localStorage.removeItem(AUTOSAVE_KEY);
        });
    }
    
    // Alle Initialisierungen starten
    setupEventListeners();
    setupCharCounter();
    setupKeyboardShortcuts();
    setupFormValidation();
    setupLeaveConfirmation();
    setDateToday();
    setupTimeAutocomplete();
    setupAutosave();
    
    // Initialen Zustand aktualisieren
    updateAllHours();
    updateJsonData();
    updateRemoveButtons();
    updateMaterialRemoveButtons();
    checkForOtherActivity();
    checkForOtherMaterial()
    
    // Modal-Events für die Vorschau
    const previewModal = document.getElementById('previewModal');
    previewModal.addEventListener('show.bs.modal', updatePreview);
});
document.addEventListener('DOMContentLoaded', function() {
    // Alle Formularelemente auswählen
    const inputs = document.querySelectorAll('.form-control, .form-select');
    
    // Stile anwenden
    inputs.forEach(input => {
        input.style.setProperty('background-color', '#14304d', 'important');
        input.style.setProperty('color', 'var(--accent)', 'important');
    });
    
    // Auch auf neue Elemente anwenden, die später hinzugefügt werden
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes) {
                mutation.addedNodes.forEach(node => {
                    if (node.querySelectorAll) {
                        const newInputs = node.querySelectorAll('.form-control, .form-select');
                        newInputs.forEach(input => {
                            input.style.setProperty('background-color', '#14304d', 'important');
                            input.style.setProperty('color', 'var(--accent)', 'important');
                        });
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});

    // Funktion um zu prüfen, ob "Andere Materialien" ausgewählt wurde
// Funktion um zu prüfen, ob "Andere Materialien" ausgewählt wurde
function checkForOtherMaterial() {
    let hasOtherMaterial = false;
    document.querySelectorAll('.material-name').forEach(select => {
        if (select.value === 'other') {
            hasOtherMaterial = true;
        }
    });
    
    const otherMaterialDiv = document.getElementById('other-material-div');
    if (hasOtherMaterial) {
        otherMaterialDiv.style.display = 'block';
        
        // Add event listener to update JSON data when the other material field changes
        const otherMaterialInput = document.getElementById('{{ form.other_material.id }}');
        otherMaterialInput.addEventListener('input', updateJsonData);
    } else {
        otherMaterialDiv.style.display = 'none';
    }
}
    // Event-Listener nach dem Laden der Seite hinzufügen
    document.addEventListener('DOMContentLoaded', function() {
        // Initial-Check durchführen
        checkForOtherMaterial();
        
        // Event-Delegation für Material-Selects
    document.getElementById('material-table').addEventListener('change', function(event) {
        if (event.target.classList.contains('material-name')) {
            checkForOtherMaterial();
        }
    });
        
        // Event-Listener für "Material hinzufügen"-Button
        document.getElementById('add-material-btn').addEventListener('click', function() {
            // Zeitverzögerung, um dem DOM Zeit zu geben, die neuen Elemente zu rendern
            setTimeout(checkForOtherMaterial, 10);
        });
    });
    // Add this JavaScript to your page (in a <script> tag or external JS file)
document.addEventListener('DOMContentLoaded', function() {
    // Ensure hidden fields stay hidden (in case CSS is overriding them)
    const hiddenFields = [
        'arbeitseinsatz_data',
        'material_data',
        'activity-hidden',
        'material-hidden'
    ];
    
    hiddenFields.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            // Force hide with inline style
            element.style.display = 'none';
            element.style.position = 'absolute';
            element.style.left = '-9999px';
        }
    });
});

