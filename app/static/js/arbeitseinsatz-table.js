// arbeitseinsatz-table.js
// Fügt Zeilen hinzu, berechnet Stunden

import { calculateHours } from './time-utils.js';

let updateAllHours, addTimeRow, updateRemoveButtons;

// Main initialization function
document.addEventListener('DOMContentLoaded', () => {
    // arbeitseinsatz-table.js functionality
    const tbody = document.querySelector('#arbeitseinsatz-table tbody');

    updateRemoveButtons = () => {
        document.querySelectorAll('#arbeitseinsatz-table tbody tr').forEach(row => {
            const btn = row.querySelector('.remove-row-btn');
            btn.style.display = tbody.children.length > 1 ? 'block' : 'none';
        });
    };

    updateAllHours = () => {
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
    };

    addTimeRow = () => {
        const originalSelect = document.querySelector('.activity-select');
        const optionsHTML = Array.from(originalSelect.options)
            .map(opt => `<option value="${opt.value}">${opt.text}</option>`)
            .join('');

        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><select class="form-select activity-select">${optionsHTML}</select></td>
            <td><input type="time" class="form-control time-from" value="00:00"></td>
            <td><input type="time" class="form-control time-to" value="00:00"></td>
            <td><input type="text" class="form-control time-hours" value="0.0" readonly></td>
            <td class="text-center">
                <button type="button" class="btn btn-sm btn-outline-danger remove-row-btn">
                    <i class="fas fa-times"></i>
                </button>
            </td>
        `;
        tbody.appendChild(newRow);

        const timeFromInput = newRow.querySelector('.time-from');
        const timeToInput = newRow.querySelector('.time-to');
        const activitySelect = newRow.querySelector('.activity-select');
        const removeBtn = newRow.querySelector('.remove-row-btn');

        timeFromInput.addEventListener('change', updateAllHours);
        timeToInput.addEventListener('change', updateAllHours);
        activitySelect.addEventListener('change', checkForOtherActivity);
        removeBtn.addEventListener('click', () => {
            tbody.removeChild(newRow);
            updateAllHours();
            updateRemoveButtons();
        });

        updateAllHours();
        updateRemoveButtons();
    };

    // Hook up add-row button
    const addRowBtn = document.getElementById('add-row-btn');
    if (addRowBtn) {
        addRowBtn.addEventListener('click', addTimeRow);
    }
});