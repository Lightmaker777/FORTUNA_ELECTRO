// time-utils.js
// Hilfsfunktionen wie calculateHours()
// time-module.js - Handles time tracking functionality

// Helper function for time calculation
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

// Functions for work time table
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
    
    // Clone options from the original select
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
    
    // Add event listeners
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
        const otherActivityInput = document.getElementById('otherActivityId');
        otherActivityInput.addEventListener('input', updateJsonData);
    } else {
        otherActivityDiv.style.display = 'none';
    }
}

function setupTimeAutocomplete() {
    // Suggestions for common work times
    const commonStartTimes = ['07:00', '07:30', '08:00', '08:30', '09:00'];
    const commonEndTimes = ['16:00', '16:30', '17:00', '17:30', '18:00'];
    
    // Datalist for start time
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
    
    // Datalist for end time
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
    
    // Assign datalists to input fields
    document.querySelectorAll('.time-from').forEach(input => {
        input.setAttribute('list', fromDatalistId);
    });
    
    document.querySelectorAll('.time-to').forEach(input => {
        input.setAttribute('list', toDatalistId);
    });
}

function setupTimeModule() {
    // Set up event listeners for time tracking
    document.querySelectorAll('.time-from, .time-to').forEach(input => {
        input.addEventListener('change', updateAllHours);
    });
    
    document.querySelectorAll('.activity-select').forEach(select => {
        select.addEventListener('change', checkForOtherActivity);
    });
    
    document.getElementById('add-row-btn').addEventListener('click', addTimeRow);
    
    // Set today's date
    setDateToday();
    setupTimeAutocomplete();
    checkForOtherActivity();
}

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
// Global variables and functions
let updateAllHours, addTimeRow, updateRemoveButtons;
let addMaterialRow, collectMaterialData, loadMaterialData, updateMaterialRemoveButtons;
let updateJsonData, setupEventListeners, setupFormValidation, setupLeaveConfirmation, setDateToday, setupAutosave;
let updatePreview, checkForOtherActivity, checkForOtherMaterial, setupCharCounter, setupTimeAutocomplete, applyDarkStyles, hideHiddenFields;

