// form-handlers.js
// Formularvalidierung, JSON-Daten
let updateJsonData, setupEventListeners, setupFormValidation, setupLeaveConfirmation, setDateToday, setupAutosave;

// form-module.js - Form handling, validation, and data functions

function updateJsonData() {
    // Collect work data
    const arbeitseinsatzData = [];
    document.querySelectorAll('#arbeitseinsatz-table tbody tr').forEach(row => {
        const activitySelect = row.querySelector('.activity-select');
        const activity = activitySelect.value;
        
        // Get the correct activity text - handle "andere" specially
        let activityText;
        if (activity === 'andere') {
            activityText = document.getElementById('otherActivityId').value.trim() || "Andere Tätigkeit";
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
    
    // Collect material data
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
            // If "Andere Materialien" is selected, use the value from the other field
            materialText = document.getElementById('otherMaterialId').value.trim() || "Andere Materialien";
        } else {
            // Otherwise use the selected text
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
    
    // Write JSON data to hidden fields
    document.getElementById('arbeitseinsatz_data').value = JSON.stringify(arbeitseinsatzData);
    document.getElementById('material_data').value = JSON.stringify(materialData);
    
    // Set main activity (first row)
    if (arbeitseinsatzData.length > 0) {
        document.getElementById('activity-hidden').value = arbeitseinsatzData[0].activity;
    }
    
    // Update preview
    updatePreview();
}

function updatePreview() {
    // Header data
    document.getElementById('preview-datum').textContent = document.getElementById('datum').value;
    document.getElementById('preview-bv').textContent = document.getElementById('bauvorhaben').value;
    document.getElementById('preview-arbeitskraft').textContent = document.getElementById('arbeitskraft').value;
    document.getElementById('preview-an-abreise').textContent = document.getElementById('an_abreise').value;

    // Work time
    const arbeitseinsatzPreview = document.getElementById('preview-arbeitseinsatz');
    arbeitseinsatzPreview.innerHTML = '';
    let totalHours = 0;
    
    // Parse the JSON data to ensure we're using the correct activity text
    let arbeitseinsatzData = [];
    try {
        arbeitseinsatzData = JSON.parse(document.getElementById('arbeitseinsatz_data').value || '[]');
    } catch (e) {
        console.error('Error parsing work data:', e);
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
        console.error('Error parsing material data:', e);
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

    // Notes
    const notes = document.getElementById('notesId').value.trim();
    if (notes) {
        document.getElementById('preview-notes-section').style.display = 'block';
        document.getElementById('preview-notes').textContent = notes;
    } else {
        document.getElementById('preview-notes-section').style.display = 'none';
    }
}

function setupCharCounter() {
    const notesField = document.getElementById('notesId');
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

function setupFormValidation() {
    const form = document.getElementById('timesheet-form');
    
    form.addEventListener('submit', function(event) {
        // Validate date
        const datumInput = document.getElementById('datum');
        if (!datumInput.value) {
            event.preventDefault();
            datumInput.classList.add('is-invalid');
            datumInput.focus();
            return;
        }
        
        // Validate work force
        const arbeitskraftInput = document.getElementById('arbeitskraft');
        if (!arbeitskraftInput.value.trim()) {
            event.preventDefault();
            arbeitskraftInput.classList.add('is-invalid');
            arbeitskraftInput.focus();
            return;
        }
        
        // Validate hours
        const totalHours = parseFloat(document.querySelector('.total-hours').value);
        if (totalHours <= 0) {
            event.preventDefault();
            alert('Bitte tragen Sie mindestens eine Tätigkeit mit gültiger Zeiterfassung ein.');
            return;
        }
        
        // Validate 'Andere Tätigkeit', if selected
        const hasOtherActivity = Array.from(document.querySelectorAll('.activity-select')).some(select => select.value === 'andere');
        if (hasOtherActivity) {
            const otherActivityInput = document.getElementById('otherActivityId');
            if (!otherActivityInput.value.trim()) {
                event.preventDefault();
                otherActivityInput.classList.add('is-invalid');
                otherActivityInput.focus();
                return;
            }
        }

        // Validate 'Andere Materialien', if selected
        const hasOtherMaterial = Array.from(document.querySelectorAll('.material-name')).some(select => select.value === 'other');
        if (hasOtherMaterial) {
            const otherMaterialInput = document.getElementById('otherMaterialId');
            if (!otherMaterialInput.value.trim()) {
                event.preventDefault();
                otherMaterialInput.classList.add('is-invalid');
                otherMaterialInput.focus();
                return;
            }
        }
        
        // Collect material data before form submission
        const materialData = collectMaterialData();
        document.getElementById('material_data').value = JSON.stringify(materialData);
    });
}

function setupLeaveConfirmation() {
    let formChanged = false;
    
    // Monitor all inputs
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('change', function() {
            formChanged = true;
        });
    });
    
    // Show confirmation dialog
    window.addEventListener('beforeunload', function(event) {
        if (formChanged) {
            event.preventDefault();
            event.returnValue = 'Sie haben ungespeicherte Änderungen. Möchten Sie die Seite wirklich verlassen?';
            return event.returnValue;
        }
    });
    
    // Disable confirmation on cancel button
    document.querySelector('a.btn-outline-secondary').addEventListener('click', function() {
        formChanged = false;
    });
    
    // Disable confirmation on save button
    document.getElementById('save-btn').addEventListener('click', function() {
        formChanged = false;
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl+S to save
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            document.getElementById('save-btn').click();
        }
        
        // Ctrl+P for preview
        if (event.ctrlKey && event.key === 'p') {
            event.preventDefault();
            const previewBtn = document.querySelector('[data-bs-target="#previewModal"]');
            previewBtn.click();
        }
    });
}

function setupFormModule() {
    // Make work force field editable
    setupWorkForceField();
    
    // Set up form-related event listeners
    const formInputs = document.querySelectorAll('#timesheet-form input, #timesheet-form select, #timesheet-form textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', updateJsonData);
    });
    
    // Set up character counter for notes
    setupCharCounter();
    
    // Set up form validation
    setupFormValidation();
    
    // Set up leave confirmation
    setupLeaveConfirmation();
    
    // Set up keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Set up autosave
    setupAutosave();
    
    // Ensure hidden fields stay hidden
    ensureHiddenFields();
}

function setupWorkForceField() {
    const arbeitskraftField = document.getElementById('arbeitskraft');
    
    // 1. Remove readonly attribute
    arbeitskraftField.removeAttribute('readonly');
    
    // 2. Adjust appearance to look like a normal input field
    arbeitskraftField.style.backgroundColor = "#fff";
    arbeitskraftField.style.cursor = "text";
    
    // 3. Add optional placeholder
    arbeitskraftField.placeholder = "Name(n) der Arbeitskraft(e) eingeben";
    
    // 4. Add help text under the field
    const helpText = document.createElement('div');
    helpText.className = 'form-text';
    helpText.innerHTML = '<small>Mehrere Namen können mit Komma getrennt werden.</small>';
    arbeitskraftField.parentNode.appendChild(helpText);
    
    // 5. Include field in tab order
    arbeitskraftField.tabIndex = 0;
}

function ensureHiddenFields() {
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
}
