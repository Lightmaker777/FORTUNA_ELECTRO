// ui-updates.js
// Dunkelmodus, Zeichenzähler

document.addEventListener('DOMContentLoaded', () => {
    // Arbeitskraft Feld bearbeiten
    const arbeitskraftField = document.getElementById('arbeitskraft');
    arbeitskraftField.removeAttribute('readonly');
    arbeitskraftField.style.backgroundColor = "#fff";
    arbeitskraftField.style.cursor = "text";
    arbeitskraftField.placeholder = "Name(n) der Arbeitskraft(e) eingeben";

    const helpText = document.createElement('div');
    helpText.className = 'form-text';
    helpText.innerHTML = '<small>Mehrere Namen können mit Komma getrennt werden.</small>';
    arbeitskraftField.parentNode.appendChild(helpText);
    arbeitskraftField.tabIndex = 0;

    // Char Counter
    setupCharCounter = () => {
        const notesField = document.querySelector('#notes');
        const charCounter = document.getElementById('char-count');
        
        if (notesField && charCounter) {
            notesField.addEventListener('input', () => {
                const length = notesField.value.length;
                charCounter.textContent = length;
                charCounter.classList.toggle('text-danger', length > 500);
                charCounter.classList.toggle('text-muted', length <= 500);
            });
        }
    };

    
        
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
    

    // Set up keyboard shortcuts
    document.addEventListener('keydown', e => {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            document.getElementById('save-btn')?.click();
        }
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            document.querySelector('[data-bs-target="#previewModal"]')?.click();
        }
    });

    hideHiddenFields = () => {
        ['arbeitseinsatz_data', 'material_data', 'activity-hidden', 'material-hidden'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.style.display = 'none';
                el.style.position = 'absolute';
                el.style.left = '-9999px';
            }
        });
    };

    applyDarkStyles = () => {
        const inputs = document.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            input.style.setProperty('background-color', '#14304d', 'important');
            input.style.setProperty('color', 'var(--accent)', 'important');
        });
    };

    function setupDarkStyles() {
        // Apply dark styles to all form elements
        const inputs = document.querySelectorAll('.form-control, .form-select');
        
        // Apply styles
        inputs.forEach(input => {
            input.style.setProperty('background-color', '#14304d', 'important');
            input.style.setProperty('color', 'var(--accent)', 'important');
        });
        
        // Also apply to new elements that are added later
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
    }
// Initialize everything
updateAllHours();
updateJsonData();
updateRemoveButtons();
updateMaterialRemoveButtons();
checkForOtherActivity();
checkForOtherMaterial();
setupEventListeners();
setupCharCounter();
setupFormValidation();
setupLeaveConfirmation();
setDateToday();
setupAutosave();
applyDarkStyles();
hideHiddenFields();
});