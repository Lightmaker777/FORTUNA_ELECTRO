// preview.js
// Vorschau-Modal

let updatePreview;

document.addEventListener('DOMContentLoaded', () => {
    updatePreview = () => {
        const previewDatum = document.getElementById('preview-datum');
        const previewBv = document.getElementById('preview-bv');
        const previewArbeitskraft = document.getElementById('preview-arbeitskraft');
        const previewAnAbreise = document.getElementById('preview-an-abreise');
        const arbeitseinsatzPreview = document.getElementById('preview-arbeitseinsatz');
        const previewStundenSumme = document.getElementById('preview-stunden-summe');
        const materialPreview = document.getElementById('preview-material');
        const notesSection = document.getElementById('preview-notes-section');
        const previewNotes = document.getElementById('preview-notes');

        if (previewDatum) previewDatum.textContent = document.getElementById('datum')?.value || '';
        if (previewBv) previewBv.textContent = document.getElementById('bauvorhaben')?.value || '';
        if (previewArbeitskraft) previewArbeitskraft.textContent = document.getElementById('arbeitskraft')?.value || '';
        if (previewAnAbreise) previewAnAbreise.textContent = document.getElementById('an_abreise')?.value || '';

        if (arbeitseinsatzPreview) {
            arbeitseinsatzPreview.innerHTML = '';
            let totalHours = 0;

            try {
                const arbeitseinsatzDataField = document.getElementById('arbeitseinsatz_data');
                const data = arbeitseinsatzDataField ? JSON.parse(arbeitseinsatzDataField.value || '[]') : [];
                data.forEach(item => {
                    totalHours += parseFloat(item.std) || 0;
                    const row = document.createElement('tr');
                    row.innerHTML = `<td>${item.activityText}</td><td>${item.von}</td><td>${item.bis}</td><td>${parseFloat(item.std).toFixed(1)}</td>`;
                    arbeitseinsatzPreview.appendChild(row);
                });
            } catch (e) {
                console.error('Fehler beim Laden der Arbeitseinsatz-Daten:', e);
            }

            if (previewStundenSumme) previewStundenSumme.textContent = totalHours.toFixed(1);
        }

        if (materialPreview) {
            materialPreview.innerHTML = '';
            try {
                const materialDataField = document.getElementById('material_data');
                const mData = materialDataField ? JSON.parse(materialDataField.value || '[]') : [];
                if (mData.length === 0) {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = `<td colspan="2" class="text-center text-muted">Keine Materialien eingetragen</td>`;
                    materialPreview.appendChild(emptyRow);
                } else {
                    mData.forEach(item => {
                        const row = document.createElement('tr');
                        row.innerHTML = `<td>${item.materialText}</td><td>${item.menge}</td>`;
                        materialPreview.appendChild(row);
                    });
                }
            } catch (e) {
                console.error('Fehler beim Laden der Material-Daten:', e);
            }
        }

        const notesField = document.querySelector('#notes');
        const notes = notesField ? notesField.value.trim() : '';
        
        if (notesSection && previewNotes) {
            if (notes) {
                notesSection.style.display = 'block';
                previewNotes.textContent = notes;
            } else {
                notesSection.style.display = 'none';
            }
        }
    };

    const previewModal = document.getElementById('previewModal');
    previewModal?.addEventListener('show.bs.modal', updatePreview);
});