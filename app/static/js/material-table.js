// material-table.js
// Fügt Materialzeilen hinzu
let addMaterialRow, collectMaterialData, loadMaterialData, updateMaterialRemoveButtons;

// material-module.js - Handles material tracking functionality

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
    
    // Apply dark styles to the new row
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
            materialText = document.getElementById('otherMaterialId').value.trim() || "Andere Materialien";
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

function loadMaterialData() {
    const tbody = document.querySelector('#material-table tbody');
    tbody.innerHTML = ''; // Clear table
    
    let materialData = [];
    try {
        const materialDataJson = document.getElementById('material_data').value;
        if (materialDataJson) {
            materialData = JSON.parse(materialDataJson);
        }
    } catch (e) {
        console.error('Error parsing material data:', e);
        materialData = [];
    }
    
    // If no data is available, add an empty row
    if (materialData.length === 0) {
        addMaterialRow();
        return;
    }
    
    // Load existing data
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
            document.getElementById('otherMaterialId').value = item.materialText;
        }
    });
    
    // Make sure to update the other material field visibility
    checkForOtherMaterial();
}

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
        const otherMaterialInput = document.getElementById('otherMaterialId');
        otherMaterialInput.addEventListener('input', updateJsonData);
    } else {
        otherMaterialDiv.style.display = 'none';
    }
}

function setupMaterialModule() {
    // Set up event listeners for material tracking
    document.getElementById('add-material-btn').addEventListener('click', addMaterialRow);
    
    // Event delegation for material selects
    document.getElementById('material-table').addEventListener('change', function(event) {
        if (event.target.classList.contains('material-name')) {
            checkForOtherMaterial();
        }
    });
    
    // Material input event listeners
    const materialInputs = document.querySelectorAll('.material-name, .material-quantity');
    materialInputs.forEach(input => {
        input.addEventListener('input', updateJsonData);
    });
    
    // Initialize
    checkForOtherMaterial();
}
