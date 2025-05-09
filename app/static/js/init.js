// init.js
 // Startet alle Funktionen beim Laden
 document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    setupTimeModule();
    setupMaterialModule();
    setupFormModule();
    setupUIModule();
    
    // Apply initial state
    updateAllHours();
    updateJsonData();
    updateRemoveButtons();
    updateMaterialRemoveButtons();
    checkForOtherActivity();
    checkForOtherMaterial();
    
    // Modal-Events for preview
    const previewModal = document.getElementById('previewModal');
    previewModal.addEventListener('show.bs.modal', updatePreview);
});