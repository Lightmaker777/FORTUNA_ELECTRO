// Script für Kalenderfunktionen 
document.addEventListener('DOMContentLoaded', function() {
    // Kalenderinitalisierung
    const calendarDays = document.getElementById('calendarDays');
    const currentMonthYearEl = document.getElementById('currentMonthYear');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    
    // Projektmodal und Tab-Steuerung
    const projectsModal = document.getElementById('projectsModal');
    const statCards = document.querySelectorAll('.stat-card');
    const tabSelector = document.getElementById('tabSelector');
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const sortSelect = document.getElementById('sortProjects');
    const projectItems = document.querySelectorAll('.project-item');

    // Aktuelles Datum festlegen
    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();

    // Urlaubsdaten und Feiertage
    let vacations = [];
    
    // Feiertage für Berlin (Deutschland)

const holidays = [
    { name: 'Neujahr', date: new Date(currentYear, 0, 1) }, // 1. Januar
    { name: 'Internationaler Frauentag', date: new Date(currentYear, 2, 8) }, // 8. März
    { name: 'Karfreitag', date: getEasterRelatedDate(currentYear, -2) }, // Freitag vor Ostersonntag
    { name: 'Ostersonntag', date: getEasterRelatedDate(currentYear, 0) }, // Ostersonntag (nicht gesetzlicher Feiertag überall, in Berlin kein gesetzlicher Feiertag)
    { name: 'Ostermontag', date: getEasterRelatedDate(currentYear, 1) }, // Montag nach Ostersonntag
    { name: 'Tag der Arbeit', date: new Date(currentYear, 4, 1) }, // 1. Mai
    { name: 'Christi Himmelfahrt', date: getEasterRelatedDate(currentYear, 39) }, // 39 Tage nach Ostersonntag
    { name: 'Pfingstsonntag', date: getEasterRelatedDate(currentYear, 49) }, // Pfingstsonntag (nicht gesetzlicher Feiertag überall, in Berlin auch nicht offiziell frei)
    { name: 'Pfingstmontag', date: getEasterRelatedDate(currentYear, 50) }, // 50 Tage nach Ostersonntag
    { name: 'Tag der Deutschen Einheit', date: new Date(currentYear, 9, 3) }, // 3. Oktober
    { name: 'Reformationstag', date: new Date(currentYear, 9, 31) }, // 31. Oktober (seit 2018 in Berlin gesetzlicher Feiertag)
    { name: '1. Weihnachtstag', date: new Date(currentYear, 11, 25) }, // 25. Dezember
    { name: '2. Weihnachtstag', date: new Date(currentYear, 11, 26) } // 26. Dezember
];

// Funktion, um bewegliche Feiertage zu berechnen (basierend auf Ostersonntag)
function getEasterRelatedDate(year, offsetDays) {
    const easter = calculateEaster(year);
    const date = new Date(easter);
    date.setDate(date.getDate() + offsetDays);
    return date;
}

// Funktion zur Berechnung des Ostersonntags (nach Gauß'scher Formel)
function calculateEaster(year) {
    const f = Math.floor,
        G = year % 19,
        C = f(year / 100),
        H = (C - f(C / 4) - f((8 * C + 13) / 25) + 19 * G + 15) % 30,
        I = H - f(H / 28) * (1 - f(29 / (H + 1)) * f((21 - G) / 11)),
        J = (year + f(year / 4) + I + 2 - C + f(C / 4)) % 7,
        L = I - J,
        month = 3 + f((L + 40) / 44),
        day = L + 28 - 31 * f(month / 4);
    return new Date(year, month - 1, day);
}


    // Local Storage Key für Urlaubsdaten
    const VACATIONS_STORAGE_KEY = 'vacation_data';

    // Lade Urlaubsdaten aus localStorage
    function loadLocalVacations() {
        const savedVacations = localStorage.getItem(VACATIONS_STORAGE_KEY);
        if (savedVacations) {
            try {
                // Parse gespeicherte Daten und konvertiere Strings zu Date-Objekten
                const parsedVacations = JSON.parse(savedVacations);
                return parsedVacations.map(vacation => ({
                    ...vacation,
                    start: new Date(vacation.start),
                    end: new Date(vacation.end)
                }));
            } catch (e) {
                console.error('Fehler beim Laden der gespeicherten Urlaubsdaten:', e);
                return [];
            }
        }
        return [];
    }

    // Speichere Urlaubsdaten im localStorage
    function saveLocalVacations() {
        try {
            localStorage.setItem(VACATIONS_STORAGE_KEY, JSON.stringify(vacations));
        } catch (e) {
            console.error('Fehler beim Speichern der Urlaubsdaten:', e);
        }
    }

    // Beim Laden der Seite Urlaubsdaten abrufen
    async function loadVacations() {
        try {
            // Versuche zuerst, Daten von der API zu laden
            const response = await fetch('/api/vacations');
            if (response.ok) {
                const data = await response.json();
                // Konvertiere Datumsstrings zu Date-Objekten
                vacations = data.map(vacation => ({
                    ...vacation,
                    start: new Date(vacation.start),
                    end: new Date(vacation.end)
                }));
            } else {
                // Wenn API-Aufruf fehlschlägt, lade aus localStorage
                console.warn('API-Aufruf fehlgeschlagen, verwende lokale Daten');
                vacations = loadLocalVacations();
            }
        } catch (error) {
            console.error('Fehler beim Laden der Urlaubsdaten:', error);
            // Bei Fehler lokale Daten laden
            vacations = loadLocalVacations();
        }
        
        // Kalender und Liste aktualisieren
        renderCalendar();
        updateVacationList();
    }

    // Lade Urlaubsdaten beim Start
    if (calendarDays) {
        loadVacations();
    }

    // Event Listener für Monatswechsel
    if (prevMonthBtn && nextMonthBtn) {
        prevMonthBtn.addEventListener('click', function() {
            if (currentMonth === 0) {
                currentMonth = 11;
                currentYear--;
            } else {
                currentMonth--;
            }
            renderCalendar();
        });

        nextMonthBtn.addEventListener('click', function() {
            if (currentMonth === 11) {
                currentMonth = 0;
                currentYear++;
            } else {
                currentMonth++;
            }
            renderCalendar();
        });
    }

    // Speichern eines neuen Urlaubs
    const saveVacationBtn = document.getElementById('saveVacation');
    if (saveVacationBtn) {
        saveVacationBtn.addEventListener('click', async function() {
            const nameInput = document.getElementById('vacationName');
            const startDateInput = document.getElementById('startDate');
            const endDateInput = document.getElementById('endDate');
            const typeInput = document.getElementById('vacationType');
            
            if (!nameInput || !startDateInput || !endDateInput || !typeInput) {
                console.error('Urlaubsformular-Elemente nicht gefunden');
                return;
            }
            
            const name = nameInput.value;
            const startDateStr = startDateInput.value;
            const endDateStr = endDateInput.value;
            const type = typeInput.value;

            if (!name || !startDateStr || !endDateStr) {
                alert('Bitte alle Pflichtfelder ausfüllen!');
                return;
            }

            try {
                // Versuche, den Urlaub über die API zu speichern
                const response = await fetch('/api/vacations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        name, 
                        start_date: startDateStr, 
                        end_date: endDateStr, 
                        type 
                    }),
                });

                if (response.ok) {
                    await loadVacations(); // Aktualisiere die Anzeige
                } else {
                    // Wenn API-Aufruf fehlschlägt, speichere lokal
                    console.warn('API-Speicherung fehlgeschlagen, speichere lokal');
                    addLocalVacation(name, startDateStr, endDateStr, type);
                }
            } catch (error) {
                console.error('Fehler beim Speichern des Urlaubs:', error);
                // Fallback: Lokal speichern
                addLocalVacation(name, startDateStr, endDateStr, type);
            }

            // Modal schließen und Formular zurücksetzen
            const newVacationModal = bootstrap.Modal.getInstance(document.getElementById('newVacationModal'));
            if (newVacationModal) {
                newVacationModal.hide();
            }
            
            const vacationForm = document.getElementById('vacationForm');
            if (vacationForm) {
                vacationForm.reset();
            }
        });
    }

    // Funktion zum lokalen Hinzufügen eines Urlaubs
    function addLocalVacation(name, startDateStr, endDateStr, type) {
        const startDate = new Date(startDateStr);
        const endDate = new Date(endDateStr);
        
        // Neuen Urlaub zum Array hinzufügen
        vacations.push({
            id: Date.now(), // Verwende Timestamp als eindeutige ID
            name: name,
            start: startDate,
            end: endDate,
            type: type
        });

        // Speichere im localStorage
        saveLocalVacations();

        // Kalender neu rendern
        renderCalendar();

        // Liste der Urlaube aktualisieren
        updateVacationList();
    }
// Aktuallisieren liste
    function updateVacationList() {
    const vacationList = document.getElementById('vacationList');
    if (!vacationList) return;
    vacationList.innerHTML = '';

    if (vacations.length === 0) {
        const emptyItem = document.createElement('li');
        emptyItem.className = 'list-group-item fw-bold text-center text-dark';
        emptyItem.textContent = 'Keine Urlaube eingetragen';
        vacationList.appendChild(emptyItem);
        return;
    }

    vacations.forEach((vacation, index) => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

        // Farbliche Markierung je nach Urlaubstyp hinzufügen
        const typeColorClass = getVacationTypeClass(vacation.type);
        listItem.classList.add(typeColorClass);

        const infoDiv = document.createElement('div');
        const nameEl = document.createElement('h6');
        nameEl.className = 'mb-0 fw-bold text-white'; // Schwarz und bold für den Namen
        nameEl.textContent = vacation.name;

        // Zeige den Urlaubstyp an
        const typeEl = document.createElement('span');
        typeEl.className = `badge me-2`;
        typeEl.style.backgroundColor = getVacationTypeColor(vacation.type);
        typeEl.textContent = getVacationTypeName(vacation.type);

        // Wrapper für Name und Badge
        const headerDiv = document.createElement('div');
        headerDiv.className = 'd-flex align-items-center mb-1';
        headerDiv.appendChild(typeEl);
        headerDiv.appendChild(nameEl);

        const dateEl = document.createElement('small');
        dateEl.className = 'fw-bold text-white d-block mt-1';
        const startDate = vacation.start instanceof Date ? vacation.start : new Date(vacation.start);
        const endDate = vacation.end instanceof Date ? vacation.end : new Date(vacation.end);
        dateEl.textContent = `${formatDate(startDate)} - ${formatDate(endDate)}`;

        infoDiv.appendChild(headerDiv);
        infoDiv.appendChild(dateEl);

        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'vacation-actions';
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-icon btn-sm text-danger';
        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
        deleteBtn.addEventListener('click', async function () {
            if (confirm('Urlaub wirklich löschen?')) {
                try {
                    // Versuche erst, über die API zu löschen
                    const vacationId = vacation.id || index;
                    const response = await fetch(`/api/vacations/${vacationId}`, {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        await loadVacations();
                    } else {
                        // Fallback: Lokal löschen
                        vacations.splice(index, 1);
                        saveLocalVacations(); // Speichere die Änderung
                        updateVacationList();
                        renderCalendar();
                    }
                } catch (error) {
                    console.error('Fehler beim Löschen des Urlaubs:', error);
                    // Fallback: Lokal löschen
                    vacations.splice(index, 1);
                    saveLocalVacations(); // Speichere die Änderung
                    updateVacationList();
                    renderCalendar();
                }
            }
        });
        actionsDiv.appendChild(deleteBtn);

        listItem.appendChild(infoDiv);
        listItem.appendChild(actionsDiv);
        vacationList.appendChild(listItem);
    });
}
// Hilfsfunktion, um die CSS-Klasse für den Urlaubstyp zu bestimmen
function getVacationTypeClass(type) {
    switch (type) {
        case 'urlaub':
            return 'vacation-type-urlaub';
        case 'krankheit':
            return 'vacation-type-krankheit';
        case 'sonstiges':
            return 'vacation-type-sonstiges';
        default:
            return ''; // Fallback: keine Klasse
    }
}

// Hilfsfunktion, um die Farbe für den Urlaubstyp zu bestimmen
function getVacationTypeColor(type) {
    switch (type) {
        case 'urlaub':
            return '#58a763'; // Grün
        case 'krankheit':
            return '#dc3545'; // Rot
        case 'sonstiges':
            return '#0d6efd'; // Blau
        default:
            return '#6c757d'; // Grau als Fallback
    }
}
// Hilfsfunktion, um den angezeigten Namen für den Urlaubstyp zu bestimmen
function getVacationTypeName(type) {
    switch(type) {
        case 'urlaub':
            return 'Urlaub';
        case 'krankheit':
            return 'Krank';
        case 'sonstiges':
            return 'Sonstiges';
        default:
            return 'Abwesenheit';
    }
}

    // Formatiert ein Datum im deutschen Format
    function formatDate(date) {
        if (!(date instanceof Date) || isNaN(date)) {
            console.error('Ungültiges Datum:', date);
            return 'Ungültiges Datum';
        }
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    // Hilfsfunktion für Datumsformatierung in Input-Felder
    function formatDateForInput(date) {
        if (!(date instanceof Date) || isNaN(date)) {
            console.error('Ungültiges Datum für Input:', date);
            return '';
        }
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Rendert den Kalender
    function renderCalendar() {
        if (!calendarDays || !currentMonthYearEl) return;

        const monthNames = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
                           'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
        currentMonthYearEl.textContent = `${monthNames[currentMonth]} ${currentYear}`;

        // Kalender leeren
        calendarDays.innerHTML = '';

        // Ersten Tag des Monats bestimmen
        const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
        let startingDayOfWeek = firstDayOfMonth.getDay(); // 0 = Sonntag, 1 = Montag,...
        // Anpassen für Montag als ersten Tag der Woche
        if (startingDayOfWeek === 0) startingDayOfWeek = 7;
        startingDayOfWeek--; // 0 = Montag, 1 = Dienstag,...

        // Letzten Tag des Monats bestimmen
        const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0);
        const daysInMonth = lastDayOfMonth.getDate();

        // Tage des vorherigen Monats anzeigen
        const prevMonthDays = new Date(currentYear, currentMonth, 0).getDate();
        for (let i = 0; i < startingDayOfWeek; i++) {
            const dayEl = createDayElement(prevMonthDays - startingDayOfWeek + i + 1, 'other-month');
            calendarDays.appendChild(dayEl);
        }

        // Tage des aktuellen Monats anzeigen
        const today = new Date();
        for (let i = 1; i <= daysInMonth; i++) {
            const isToday = today.getDate() === i && 
                            today.getMonth() === currentMonth && 
                            today.getFullYear() === currentYear;
            const dayEl = createDayElement(i, 'current-month' + (isToday ? ' today' : ''));

            // Prüfen, ob an diesem Tag ein Urlaub ist
            const currentDateObj = new Date(currentYear, currentMonth, i);
            const hasVacation = checkForVacation(currentDateObj);
            const hasHoliday = checkForHoliday(currentDateObj);

            if (hasVacation) {
                dayEl.classList.add('has-vacation');
                // Tooltips für Urlaub
                dayEl.setAttribute('data-bs-toggle', 'tooltip');
                dayEl.setAttribute('data-bs-html', 'true');

                // Erhalte alle Urlaubspersonen für diesen Tag
                const vacationPersons = getVacationPersons(currentDateObj);
                dayEl.setAttribute('data-bs-title', vacationPersons.join('<br>'));
            }

            if (hasHoliday) {
                dayEl.classList.add('has-holiday');
                // Tooltips für Feiertage
                const holiday = holidays.find(h => h.date.getDate() === i && 
                                    h.date.getMonth() === currentMonth &&
                                    h.date.getFullYear() === currentYear);
                if (holiday) {
                    dayEl.setAttribute('data-bs-toggle', 'tooltip');
                    dayEl.setAttribute('data-bs-title', holiday.name);
                }
            }

            calendarDays.appendChild(dayEl);
        }

        // Tage des nächsten Monats anzeigen
        const totalDaysShown = startingDayOfWeek + daysInMonth;
        const nextMonthDays = 42 - totalDaysShown; // 6 Reihen x 7 Tage = 42
        for (let i = 1; i <= nextMonthDays; i++) {
            const dayEl = createDayElement(i, 'other-month');
            calendarDays.appendChild(dayEl);
        }

        // Tooltips initialisieren
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Helfer-Funktion zum Erstellen von Tageselementen
    function createDayElement(day, className) {
        const dayEl = document.createElement('div');
        dayEl.className = `calendar-day col ${className}`;
        dayEl.textContent = day;

        // Klick-Event für den Tag
        dayEl.addEventListener('click', function() {
            showDayDetails(day, className);
        });

        return dayEl;
    }

    // Prüft, ob an einem bestimmten Tag ein Urlaub ist
    function checkForVacation(date) {
        return vacations.some(vacation => {
            const start = vacation.start instanceof Date ? vacation.start : new Date(vacation.start);
            const end = vacation.end instanceof Date ? vacation.end : new Date(vacation.end);
            
            // Setze Zeiten auf 00:00:00 für korrekten Vergleich
            const checkDate = new Date(date);
            checkDate.setHours(0, 0, 0, 0);
            
            const checkStart = new Date(start);
            checkStart.setHours(0, 0, 0, 0);
            
            const checkEnd = new Date(end);
            checkEnd.setHours(0, 0, 0, 0);
            
            return checkDate >= checkStart && checkDate <= checkEnd;
        });
    }

    // Prüft, ob ein bestimmter Tag ein Feiertag ist
    function checkForHoliday(date) {
        return holidays.some(holiday => {
            return date.getDate() === holiday.date.getDate() &&
                   date.getMonth() === holiday.date.getMonth() &&
                   date.getFullYear() === holiday.date.getFullYear();
        });
    }

    // Gibt alle Personen zurück, die an einem bestimmten Tag im Urlaub sind
    function getVacationPersons(date) {
        const personsOnVacation = [];
        vacations.forEach(vacation => {
            const start = vacation.start instanceof Date ? vacation.start : new Date(vacation.start);
            const end = vacation.end instanceof Date ? vacation.end : new Date(vacation.end);
            
            // Setze Zeiten auf 00:00:00 für korrekten Vergleich
            const checkDate = new Date(date);
            checkDate.setHours(0, 0, 0, 0);
            
            const checkStart = new Date(start);
            checkStart.setHours(0, 0, 0, 0);
            
            const checkEnd = new Date(end);
            checkEnd.setHours(0, 0, 0, 0);
            
            if (checkDate >= checkStart && checkDate <= checkEnd) {
                personsOnVacation.push(vacation.name);
            }
        });
        return personsOnVacation;
    }

    // Zeigt Details zu einem bestimmten Tag an
function showDayDetails(day, className) {
    if (className.includes('other-month')) return;
    const selectedDate = new Date(currentYear, currentMonth, day);

    // Immer das Modal öffnen, unabhängig von bestehenden Urlauben
    const newVacationModalElement = document.getElementById('newVacationModal');
    if (newVacationModalElement) {
        // Datum im Modal vorausfüllen
        const startDateInput = document.getElementById('startDate');
        const endDateInput = document.getElementById('endDate');
        
        if (startDateInput && endDateInput) {
            startDateInput.value = formatDateForInput(selectedDate);
            endDateInput.value = formatDateForInput(selectedDate);
        }
        
        // Sicherstellen, dass das Modal-Objekt korrekt erstellt wird
        const newVacationModal = new bootstrap.Modal(newVacationModalElement);
        newVacationModal.show();
    } else {
        console.error('Modal-Element nicht gefunden');
    }
}

    // Projektmodal-Funktionalitäten
    if (projectsModal) {
        projectsModal.addEventListener('show.bs.modal', function(event) {
            // Button, der das Modal ausgelöst hat
            const button = event.relatedTarget;
            
            // Tabziel aus dem data-tab-target-Attribut extrahieren
            const tabTarget = button && button.getAttribute('data-tab-target');
            
            if (tabTarget) {
                // Entsprechenden Tab aktivieren
                const tab = document.getElementById(tabTarget);
                if (tab) {
                    // Bootstrap Tab-Objekt erstellen und aktivieren
                    const bsTab = new bootstrap.Tab(tab);
                    bsTab.show();
                    
                    // Dropdown für mobile Ansicht aktualisieren
                    if (tabSelector) {
                        tabSelector.value = tabTarget.replace('-tab', '');
                    }
                }
            }
        });

        // Animation für Modal hinzufügen
        projectsModal.addEventListener('shown.bs.modal', function() {
            const projectItems = document.querySelectorAll('.project-item');
            projectItems.forEach((item, index) => {
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, 100 * index);
            });
        });
    }
    
    // Hover-Animation für Statistikkarten
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const iconWrapper = this.querySelector('.stat-icon-wrapper');
            if (iconWrapper) {
                iconWrapper.style.animation = 'pulse 1s infinite';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const iconWrapper = this.querySelector('.stat-icon-wrapper');
            if (iconWrapper) {
                iconWrapper.style.animation = '';
            }
        });
    });
    
    // Mobile Tab-Selector
    if (tabSelector) {
        tabSelector.addEventListener('change', function() {
            const selectedValue = this.value;
            const tabId = selectedValue + '-tab';
            const tab = document.getElementById(tabId);
            
            if (tab) {
                const bsTab = new bootstrap.Tab(tab);
                bsTab.show();
            }
        });
    }
    
    // Event-Listener für Tab-Wechsel zur Synchronisierung des Dropdown-Selectors
    const tabElements = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabElements.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const tabId = event.target.id;
            const tabValue = tabId.replace('-tab', '');
            
            if (tabSelector) {
                tabSelector.value = tabValue;
            }
        });
    });
    
    // Filter- und Suchfunktion für Projekte
    function filterProjects() {
        if (!searchInput || !statusFilter || !projectItems.length) return;
        
        const searchTerm = searchInput.value.toLowerCase();
        const statusValue = statusFilter.value;
        let visibleCount = 0;
        
        projectItems.forEach(item => {
            const projectName = item.getAttribute('data-name').toLowerCase();
            const projectStatus = item.getAttribute('data-status');
            
            const matchesSearch = projectName.includes(searchTerm);
            const matchesStatus = statusValue === 'all' || projectStatus === statusValue;
            
            if (matchesSearch && matchesStatus) {
                item.style.display = '';
                visibleCount++;
                
                // Animation beim Anzeigen hinzufügen
                item.style.animation = 'fadeIn 0.3s ease forwards';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Wenn keine Ergebnisse gefunden wurden, zeige eine Nachricht an
        const noResultsMsg = document.getElementById('noResultsMessage');
        const projectContainer = document.querySelector('.project-cards');
        
        if (visibleCount === 0 && projectContainer) {
            if (!noResultsMsg) {
                const msgDiv = document.createElement('div');
                msgDiv.id = 'noResultsMessage';
                msgDiv.className = 'text-center py-4 mt-3';
                msgDiv.innerHTML = `
                    <i class="fas fa-search fa-2x text-muted mb-3"></i>
                    <h5>Keine Projekte gefunden</h5>
                    <p class="text-muted">Versuchen Sie es mit anderen Suchbegriffen oder Filtern</p>
                `;
                
                projectContainer.appendChild(msgDiv);
            }
        } else if (noResultsMsg) {
            noResultsMsg.remove();
        }
    }
    
    // Sortierung von Projekten
    function sortProjects() {
        if (!sortSelect || !projectItems.length) return;
        
        const sortValue = sortSelect.value;
        const projectContainer = document.querySelector('.project-cards');
        if (!projectContainer) return;
        
        const projectsArray = Array.from(projectItems);
        
        projectsArray.sort((a, b) => {
            const aName = a.getAttribute('data-name').toLowerCase();
            const bName = b.getAttribute('data-name').toLowerCase();
            const aDate = a.getAttribute('data-date');
            const bDate = b.getAttribute('data-date');
            
            if (sortValue === 'az') {
                return aName.localeCompare(bName);
            } else if (sortValue === 'za') {
                return bName.localeCompare(aName);
            } else if (sortValue === 'newest') {
                return bDate.localeCompare(aDate);
            } else if (sortValue === 'oldest') {
                return aDate.localeCompare(bDate);
            }
            return 0;
        });
        
        projectsArray.forEach(project => {
            projectContainer.appendChild(project);
        });
    }
    
    // Event-Listener für Suchfunktionen
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(filterProjects, 300);
        });
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterProjects);
    }
    
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            sortProjects();
            filterProjects();
        });
    }
    
    // Direkter Aufruf des Modals mit URL-Parameter
    function checkForModalParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        const modalParam = urlParams.get('modal');
        const tabParam = urlParams.get('tab');
        
        if (modalParam === 'projects' && projectsModal) {
            const modal = new bootstrap.Modal(projectsModal);
            modal.show();
            
            if (tabParam) {
                const tabId = tabParam + '-tab';
                const tabElement = document.getElementById(tabId);
                
                if (tabElement) {
                    const tab = new bootstrap.Tab(tabElement);
                    tab.show();
                    
                    // Dropdown für mobile Ansicht aktualisieren
                    if (tabSelector) {
                        tabSelector.value = tabParam;
                    }
                }
            }
        }
    }
    
    // Prüfen, ob das Modal angezeigt werden soll
    checkForModalParameter();
    
    // Touch-optimierte Interaktionen für mobile Geräte
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('touchstart', function() {
            this.classList.add('nav-link-touch');
        });
        
        link.addEventListener('touchend', function() {
            this.classList.remove('nav-link-touch');
        });
    });
    
    // Verbessertes visuelles Feedback beim Hover für alle interaktiven Elemente
    const hoverCards = document.querySelectorAll('.hover-card, .project-card');
    hoverCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
    
    // Initialer Kalender-Render, wenn die Elemente existieren
    if (calendarDays) {
        renderCalendar();
    }
});

// JavaScript für die Dashboard-Seite (index.html)
document.addEventListener('DOMContentLoaded', function() {
    // 1. Fix für den Countdown-Timer "WIRD GELADEN..."
    updateAllCountdownTimers();
    // Alle 30 Sekunden aktualisieren
    setInterval(updateAllCountdownTimers, 30000);
    
    // 2. Event-Listener für die Schnellauswahl-Buttons in allen Modals
    setupQuickSelectButtons();
    
    // 3. Formular-Validierung und Übermittlung für alle End-Date-Formulare
    setupEndDateForms();
});

// Funktion zum Aktualisieren aller Countdown-Timer auf der Seite
function updateAllCountdownTimers() {
    // Alle Countdown-Timer auf der Seite finden
    const countdownTimers = document.querySelectorAll('[id^="countdown-timer"]');
    
    countdownTimers.forEach(timer => {
        // Projekt-ID aus dem Timer-Element oder dem übergeordneten Element extrahieren
        const row = timer.closest('tr');
        if (!row) return;
        
        // Projekt-ID aus der Modal-ID oder einem data-Attribut extrahieren
        const modalId = row.querySelector('[data-bs-target^="#changeEndDateModal_"]');
        if (!modalId) return;
        
        const projectId = modalId.getAttribute('data-bs-target').split('_')[1];
        
        updateTimerForProject(timer, projectId);
    });
}

// Funktion zum Aktualisieren eines einzelnen Countdown-Timers
function updateTimerForProject(timerElement, projectId) {
    if (!timerElement || !projectId) return;
    
    fetch(`/api/project/${projectId}/remaining-time`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Netzwerkantwort war nicht ok');
            }
            return response.json();
        })
        .then(data => {
            // Countdown-Badge aktualisieren
            timerElement.textContent = data.remaining_detailed;
            timerElement.className = `badge bg-${data.status}`;
            
            // Fortschrittsbalken aktualisieren, falls vorhanden
            const progressBarId = `progress-bar-${projectId}`;
            const progressBar = document.getElementById(progressBarId);
            if (progressBar) {
                progressBar.style.width = `${data.progress_percentage}%`;
                progressBar.className = `progress-bar bg-${data.status}`;
            }
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der verbleibenden Zeit:', error);
            timerElement.textContent = 'Fehler';
            timerElement.className = 'badge bg-danger';
        });
}

// Funktion zum Einrichten der Schnellauswahl-Buttons für alle Modals
function setupQuickSelectButtons() {
    // Alle Schnellauswahl-Buttons finden
    const quickSelectButtons = document.querySelectorAll('.quick-select-btn');
    
    quickSelectButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Werte aus dem Button abrufen
            const value = parseInt(this.getAttribute('data-value'));
            const unit = this.getAttribute('data-unit');
            
            // Modal-ID finden, um die Projekt-ID zu extrahieren
            const modal = this.closest('.modal');
            if (!modal) return;
            
            const projectId = modal.id.split('_')[1];
            if (!projectId) return;
            
            console.log(`Quick select for project ${projectId}: +${value} ${unit}`);
            
            // Formular für die Schnellauswahl vorbereiten und absenden
            const adjustForm = document.getElementById(`adjustForm_${projectId}`);
            if (!adjustForm) return;
            
            // Versteckte Felder setzen
            let valueInput = adjustForm.querySelector('input[name="value"]');
            if (valueInput) valueInput.value = value;
            
            let unitInput = adjustForm.querySelector('input[name="unit"]');
            if (unitInput) unitInput.value = unit;
            
            // Formular absenden
            adjustForm.submit();
        });
    });
}

// Funktion zum Einrichten der Enddatum-Formulare
function setupEndDateForms() {
    // Alle Enddatum-Formulare finden
    const endDateForms = document.querySelectorAll('[id^="endDateForm_"]');
    
    endDateForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const dateInput = this.querySelector('input[name="end_date"]');
            
            if (!dateInput || !dateInput.value) {
                event.preventDefault();
                alert('Bitte ein gültiges Datum eingeben.');
                return false;
            }
            
            console.log('Submitting form with end date:', dateInput.value);
        });
    });
}    