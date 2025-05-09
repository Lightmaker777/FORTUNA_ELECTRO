// static/js/new_fortuna.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script started!");
    console.log("Form IDs:", {
    activity: "{{ form.other_activity.id }}",
    material: "{{ form.other_material.id }}",
    notes: "{{ form.notes.id }}"
    }); 
  // Utility functions
  const $ = selector => document.querySelector(selector);
  const $$ = selector => document.querySelectorAll(selector);
  
  // Calculate hours between two time values
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
  
  // Update all time entries and calculate total hours
  function updateAllHours() {
    let totalHours = 0;
    
    $$('#arbeitseinsatz-table tbody tr').forEach(row => {
      const timeFrom = row.querySelector('.time-from').value;
      const timeTo = row.querySelector('.time-to').value;
      const hours = calculateHours(timeFrom, timeTo);
      
      row.querySelector('.time-hours').value = hours.toFixed(1);
      totalHours += hours;
    });
    
    $('.total-hours').value = totalHours.toFixed(1);
    updateJsonData();
  }
  
  // Add a new time entry row
  function addTimeRow() {
    const tbody = $('#arbeitseinsatz-table tbody');
    const originalSelect = $('.activity-select');
    const optionsHTML = Array.from(originalSelect.options)
      .map(opt => `<option value="${opt.value}">${opt.text}</option>`)
      .join('');
    
    const newRow = document.createElement('tr');
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
    
    // Add event listeners to new elements
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
    setupTimeAutocomplete();
    applyDarkStyles();
  }
  
  // Toggle visibility of remove buttons based on row count
  function updateRemoveButtons() {
    const rows = $$('#arbeitseinsatz-table tbody tr');
    rows.forEach(row => {
      const btn = row.querySelector('.remove-row-btn');
      btn.style.display = rows.length > 1 ? 'block' : 'none';
    });
  }
  
  // Add a new material row
  function addMaterialRow() {
    const tbody = $('#material-table tbody');
    const newRow = document.createElement('tr');
    
    newRow.innerHTML = `
      <td>
        <select class="form-select material-name">
          <option value="">Bitte auswählen</option>
          {% for value, label in material_choices %}
          <option value="{{ value }}">{{ label }}</option>
          {% endfor %}
          <option value="other">Andere Materialien</option>
        </select>
      </td>
      <td>
        <input type="text" class="form-control material-quantity" placeholder="z.B. 25m">
      </td>
      <td class="text-center">
        <button type="button" class="btn btn-sm btn-outline-danger remove-material-btn">
          <i class="fas fa-times"></i>
        </button>
      </td>
    `;
    
    tbody.appendChild(newRow);
    
    // Add event listeners
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
    applyDarkStyles();
  }
  
  // Toggle visibility of material remove buttons based on row count
  function updateMaterialRemoveButtons() {
    const rows = $$('#material-table tbody tr');
    rows.forEach(row => {
      const btn = row.querySelector('.remove-material-btn');
      btn.style.display = rows.length > 1 ? 'block' : 'none';
    });
  }
  
  // Collect material data for form submission
  function collectMaterialData() {
    const materialData = [];
    
    $$('#material-table tbody tr').forEach(row => {
      const materialSelect = row.querySelector('.material-name');
      const quantityInput = row.querySelector('.material-quantity');
      
      // Skip empty selections
      if (materialSelect.value === "") return;
      
      // Get the displayed text
      let materialText;
      if (materialSelect.value === 'other') {
        materialText = $('#{{ form.other_material.id }}').value.trim() || "Andere Materialien";
      } else {
        const selectedOption = materialSelect.options[materialSelect.selectedIndex];
        materialText = selectedOption ? selectedOption.text : "";
      }
      
      const quantity = quantityInput.value.trim();
      
      // Only add if at least one field is filled
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
  
  // Update JSON data for the form
  function updateJsonData() {
    // Collect work data
    const arbeitseinsatzData = [];
    $$('#arbeitseinsatz-table tbody tr').forEach(row => {
      const activitySelect = row.querySelector('.activity-select');
      const activity = activitySelect.value;
      
      // Get activity text, handling "andere" specially
      let activityText;
      if (activity === 'andere') {
        activityText = $('#{{ form.other_activity.id }}').value.trim() || "Andere Tätigkeit";
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
    const materialData = collectMaterialData();
    
    // Set JSON data in hidden fields
    $('#arbeitseinsatz_data').value = JSON.stringify(arbeitseinsatzData);
    $('#material_data').value = JSON.stringify(materialData);
    
    // Set main activity (first row)
    if (arbeitseinsatzData.length > 0) {
      $('#activity-hidden').value = arbeitseinsatzData[0].activity;
    }
    
    // Update preview
    updatePreview();
  }
  
  // Check if "Other Activity" is selected and show/hide the appropriate field
  function checkForOtherActivity() {
    let hasOtherActivity = false;
    $$('.activity-select').forEach(select => {
      if (select.value === 'andere') {
        hasOtherActivity = true;
      }
    });
    
    const otherActivityDiv = $('#other-activity-div');
    if (hasOtherActivity) {
      otherActivityDiv.style.display = 'block';
      
      // Add event listener to update JSON data when field changes
      const otherActivityInput = $('#{{ form.other_activity.id }}');
      otherActivityInput.addEventListener('input', updateJsonData);
    } else {
      otherActivityDiv.style.display = 'none';
    }
  }
  
  // Check if "Other Material" is selected and show/hide the appropriate field
  function checkForOtherMaterial() {
    let hasOtherMaterial = false;
    $$('.material-name').forEach(select => {
      if (select.value === 'other') {
        hasOtherMaterial = true;
      }
    });
    
    const otherMaterialDiv = $('#other-material-div');
    if (hasOtherMaterial) {
      otherMaterialDiv.style.display = 'block';
      
      // Add event listener to update JSON data when field changes
      const otherMaterialInput = $('#{{ form.other_material.id }}');
      otherMaterialInput.addEventListener('input', updateJsonData);
    } else {
      otherMaterialDiv.style.display = 'none';
    }
  }
  
  // Update the preview modal with current data
  function updatePreview() {
    // Header data
    $('#preview-datum').textContent = $('#datum').value;
    $('#preview-bv').textContent = $('#bauvorhaben').value;
    $('#preview-arbeitskraft').textContent = $('#arbeitskraft').value;
    $('#preview-an-abreise').textContent = $('#an_abreise').value;

    // Work data
    const arbeitseinsatzPreview = $('#preview-arbeitseinsatz');
    arbeitseinsatzPreview.innerHTML = '';
    let totalHours = 0;
    
    // Parse the JSON data
    let arbeitseinsatzData = [];
    try {
      arbeitseinsatzData = JSON.parse($('#arbeitseinsatz_data').value || '[]');
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
    
    $('#preview-stunden-summe').textContent = totalHours.toFixed(1);

    // Material data
    const materialPreview = $('#preview-material');
    materialPreview.innerHTML = '';
    
    // Get material data from JSON
    let materialData = [];
    try {
      materialData = JSON.parse($('#material_data').value || '[]');
    } catch (e) {
      console.error('Error parsing material data:', e);
    }
    
    // Display material data
    if (materialData.length > 0) {
      materialData.forEach(item => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
          <td>${item.materialText}</td>
          <td>${item.menge}</td>
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
    const notes = $('#{{ form.notes.id }}').value.trim();
    if (notes) {
      $('#preview-notes-section').style.display = 'block';
      $('#preview-notes').textContent = notes;
    } else {
      $('#preview-notes-section').style.display = 'none';
    }
  }
  
  // Set up character counter for notes
  function setupCharCounter() {
    const notesField = $('#{{ form.notes.id }}');
    const charCounter = $('#char-count');
    
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
  
  // Set up keyboard shortcuts
  function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
      // Ctrl+S to save
      if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        $('#save-btn').click();
      }
      
      // Ctrl+P for preview
      if (event.ctrlKey && event.key === 'p') {
        event.preventDefault();
        $('[data-bs-target="#previewModal"]').click();
      }
    });
  }
  
  // Set up form validation
  function setupFormValidation() {
    const form = $('#timesheet-form');
    
    form.addEventListener('submit', function(event) {
      // Validate date
      const datumInput = $('#datum');
      if (!datumInput.value) {
        event.preventDefault();
        datumInput.classList.add('is-invalid');
        datumInput.focus();
        return;
      }
      
      // Validate worker name
      const arbeitskraftInput = $('#arbeitskraft');
      if (!arbeitskraftInput.value.trim()) {
        event.preventDefault();
        arbeitskraftInput.classList.add('is-invalid');
        arbeitskraftInput.focus();
        return;
      }
      
      // Validate hours
      const totalHours = parseFloat($('.total-hours').value);
      if (totalHours <= 0) {
        event.preventDefault();
        alert('Bitte tragen Sie mindestens eine Tätigkeit mit gültiger Zeiterfassung ein.');
        return;
      }
      
      // Validate "Other Activity" if selected
      const hasOtherActivity = Array.from($$('.activity-select')).some(select => select.value === 'andere');
      if (hasOtherActivity) {
        const otherActivityInput = $('#{{ form.other_activity.id }}');
        if (!otherActivityInput.value.trim()) {
          event.preventDefault();
          otherActivityInput.classList.add('is-invalid');
          otherActivityInput.focus();
          return;
        }
      }

      // Validate "Other Material" if selected
      const hasOtherMaterial = Array.from($$('.material-name')).some(select => select.value === 'other');
      if (hasOtherMaterial) {
        const otherMaterialInput = $('#{{ form.other_material.id }}');
        if (!otherMaterialInput.value.trim()) {
          event.preventDefault();
          otherMaterialInput.classList.add('is-invalid');
          otherMaterialInput.focus();
          return;
        }
      }
      
      // Clear autosave before submission
      localStorage.removeItem(AUTOSAVE_KEY);
    });
  }
  
  // Set up confirmation before leaving page with unsaved changes
  function setupLeaveConfirmation() {
    let formChanged = false;
    
    // Watch for changes
    const formInputs = $$('input, select, textarea');
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
    
    // Disable confirmation for cancel and save buttons
    $('a.btn-outline-secondary').addEventListener('click', function() {
      formChanged = false;
    });
    
    $('#save-btn').addEventListener('click', function() {
      formChanged = false;
    });
  }
  
  // Set today's date automatically
  function setDateToday() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    
    const datumInput = $('#datum');
    if (!datumInput.value) {
      datumInput.value = `${year}-${month}-${day}`;
    }
  }
  
  // Set up time autocomplete
  function setupTimeAutocomplete() {
    const commonStartTimes = ['07:00', '07:30', '08:00', '08:30', '09:00'];
    const commonEndTimes = ['16:00', '16:30', '17:00', '17:30', '18:00'];
    
    // Create datalists if they don't exist
    function ensureDatalist(id, options) {
      let datalist = document.getElementById(id);
      if (!datalist) {
        datalist = document.createElement('datalist');
        datalist.id = id;
        document.body.appendChild(datalist);
        
        options.forEach(option => {
          const opt = document.createElement('option');
          opt.value = option;
          datalist.appendChild(opt);
        });
      }
      return datalist;
    }
    
    const fromDatalistId = 'time-from-options';
    const toDatalistId = 'time-to-options';
    
    ensureDatalist(fromDatalistId, commonStartTimes);
    ensureDatalist(toDatalistId, commonEndTimes);
    
    // Assign datalists to input fields
    $$('.time-from').forEach(input => input.setAttribute('list', fromDatalistId));
    $$('.time-to').forEach(input => input.setAttribute('list', toDatalistId));
  }
  
  // Set up autosave functionality
  const AUTOSAVE_KEY = 'timesheet_autosave_' + window.location.pathname;
  const AUTOSAVE_INTERVAL = 30000; // 30 seconds
  
  function setupAutosave() {
    // Restore autosaved data
    try {
      const savedData = localStorage.getItem(AUTOSAVE_KEY);
      if (savedData) {
        const data = JSON.parse(savedData);
        
        // Restore header data
        if (data.date) $('#datum').value = data.date;
        if (data.arbeitskraft) $('#arbeitskraft').value = data.arbeitskraft;
        if (data.an_abreise) $('#an_abreise').value = data.an_abreise;
        
        // Restore work data
        if (data.arbeitseinsatz && data.arbeitseinsatz.length > 0) {
          // First row
          const firstRow = $('#arbeitseinsatz-table tbody tr');
          firstRow.querySelector('.activity-select').value = data.arbeitseinsatz[0].activity;
          firstRow.querySelector('.time-from').value = data.arbeitseinsatz[0].von;
          firstRow.querySelector('.time-to').value = data.arbeitseinsatz[0].bis;
          
          // Additional rows
          for (let i = 1; i < data.arbeitseinsatz.length; i++) {
            addTimeRow();
            const row = $$('#arbeitseinsatz-table tbody tr')[i];
            row.querySelector('.activity-select').value = data.arbeitseinsatz[i].activity;
            row.querySelector('.time-from').value = data.arbeitseinsatz[i].von;
            row.querySelector('.time-to').value = data.arbeitseinsatz[i].bis;
          }
        }
        
        // Restore material data
        if (data.material && data.material.length > 0) {
          // First row
          const firstRow = $('#material-table tbody tr');
          if (firstRow) {
            firstRow.querySelector('.material-name').value = data.material[0].material;
            firstRow.querySelector('.material-quantity').value = data.material[0].menge;
          
            // Additional rows
            for (let i = 1; i < data.material.length; i++) {
              addMaterialRow();
              const row = $$('#material-table tbody tr')[i];
              row.querySelector('.material-name').value = data.material[i].material;
              row.querySelector('.material-quantity').value = data.material[i].menge;
            }
          } else {
            // If no first row exists, add one for each material item
            data.material.forEach(item => {
              addMaterialRow();
              const lastRow = $('#material-table tbody').lastElementChild;
              lastRow.querySelector('.material-name').value = item.material;
              lastRow.querySelector('.material-quantity').value = item.menge;
            });
          }
        }
        
        // Restore notes
        if (data.notes) $('#{{ form.notes.id }}').value = data.notes;
        
        // Update interface
        updateAllHours();
        checkForOtherActivity();
        checkForOtherMaterial();
        
        // Show autosave info
        showAutosaveNotification();
      }
    } catch (error) {
      console.error('Error restoring autosave data:', error);
    }
    
    // Set up regular saving
    setInterval(performAutosave, AUTOSAVE_INTERVAL);
  }
  
  function performAutosave() {
    try {
      // Collect data
      const data = {
        date: $('#datum').value,
        arbeitskraft: $('#arbeitskraft').value,
        an_abreise: $('#an_abreise').value,
        arbeitseinsatz: JSON.parse($('#arbeitseinsatz_data').value || '[]'),
        material: JSON.parse($('#material_data').value || '[]'),
        notes: $('#{{ form.notes.id }}').value
      };
      
      // Save to localStorage
      localStorage.setItem(AUTOSAVE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Autosave error:', error);
    }
  }
  
  function showAutosaveNotification() {
    const autosaveInfo = document.createElement('div');
    autosaveInfo.className = 'alert alert-info animate__animated animate__fadeIn';
    autosaveInfo.innerHTML = `
      <i class="fas fa-history me-2"></i>
      <strong>Automatisch gespeicherte Daten wiederhergestellt.</strong>
      <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Schließen"></button>
    `;
    $('.card-body').insertBefore(autosaveInfo, $('form'));
    
    // Hide alert after 5 seconds
    setTimeout(() => {
      autosaveInfo.classList.add('animate__fadeOut');
      setTimeout(() => autosaveInfo.remove(), 500);
    }, 5000);
  }
  
  // Apply dark styles to form elements
  function applyDarkStyles() {
    $$('.form-control, .form-select').forEach(input => {
      input.style.setProperty('background-color', '#14304d', 'important');
      input.style.setProperty('color', 'var(--accent)', 'important');
    });
  }
  
  // Make arbeitskraft field editable
  function makeArbeitskraftEditable() {
    const arbeitskraftField = $('#arbeitskraft');
    
    arbeitskraftField.removeAttribute('readonly');
    arbeitskraftField.style.backgroundColor = "#fff";
    arbeitskraftField.style.cursor = "text";
    arbeitskraftField.placeholder = "Name(n) der Arbeitskraft(e) eingeben";
    arbeitskraftField.tabIndex = 0;
    
    const helpText = document.createElement('div');
    helpText.className = 'form-text';
    helpText.innerHTML = '<small>Mehrere Namen können mit Komma getrennt werden.</small>';
    arbeitskraftField.parentNode.appendChild(helpText);
  }
  
  // Ensure hidden fields stay hidden
  function hideHiddenFields() {
    ['arbeitseinsatz_data', 'material_data', 'activity-hidden', 'material-hidden'].forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.style.display = 'none';
        element.style.position = 'absolute';
        element.style.left = '-9999px';
      }
    });
  }
  
  // Set up event listeners
  function setupEventListeners() {
    // Form inputs
    $$('#timesheet-form input, #timesheet-form select, #timesheet-form textarea').forEach(input => {
      input.addEventListener('input', updateJsonData);
    });
    
    // Time table
    $$('.time-from, .time-to').forEach(input => {
      input.addEventListener('change', updateAllHours);
    });
    
    $$('.activity-select').forEach(select => {
      select.addEventListener('change', checkForOtherActivity);
    });
    
    // Add row buttons
    $('#add-row-btn').addEventListener('click', addTimeRow);
    $('#add-material-btn').addEventListener('click', addMaterialRow);
    
    // Material inputs
    $$('.material-name, .material-quantity').forEach(input => {
      input.addEventListener('input', updateJsonData);
    });
    
    // Preview modal
    $('#previewModal').addEventListener('show.bs.modal', updatePreview);
    
    // Material table event delegation
    $('#material-table').addEventListener('change', function(event) {
      if (event.target.classList.contains('material-name')) {
        checkForOtherMaterial();
      }
    });
  }
  
  // Initialize everything
  function init() {
    makeArbeitskraftEditable();
    hideHiddenFields();
    setupEventListeners();
    setupCharCounter();
    setupKeyboardShortcuts();
    setupFormValidation();
    setupLeaveConfirmation();
    setDateToday();
    setupTimeAutocomplete();
    setupAutosave();
    
    // Initial state updates
    updateAllHours();
    updateJsonData();
    updateRemoveButtons();
    updateMaterialRemoveButtons();
    checkForOtherActivity();
    checkForOtherMaterial();
    applyDarkStyles();
    
    // Set up observer for dynamic elements
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        if (mutation.addedNodes) {
          mutation.addedNodes.forEach(node => {
            if (node.querySelectorAll) {
              applyDarkStyles();
            }
          });
        }
      });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
  }
  console.log("Script finished.");
  // Start everything
  init();
});