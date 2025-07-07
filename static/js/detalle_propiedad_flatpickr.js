// Validación para inputs nativos <input type='date'> en reserva

document.addEventListener('DOMContentLoaded', function() {
    function getBlockedDates() {
        let fechasBloqueadas = [];
        function getFechasEnRango(inicio, fin) {
            let fechas = [];
            let current = new Date(inicio);
            let end = new Date(fin);
            while (current <= end) {
                fechas.push(current.toISOString().slice(0,10));
                current.setDate(current.getDate() + 1);
            }
            return fechas;
        }
        (window.fechasOcupadas || []).forEach(function(r) {
            getFechasEnRango(r.inicio, r.fin).forEach(f => fechasBloqueadas.push(f));
        });
        (window.fechasReservadas || []).forEach(function(r) {
            getFechasEnRango(r.inicio, r.fin).forEach(f => fechasBloqueadas.push(f));
        });
        return Array.from(new Set(fechasBloqueadas));
    }

    const blockedDates = getBlockedDates();
    const today = new Date().toISOString().slice(0,10);

    function flatpickrOptions(inputId) {
        return {
            dateFormat: 'Y-m-d',
            minDate: today,
            disable: blockedDates,
            locale: 'es',
            allowInput: false,
            onDayCreate: function(dObj, dStr, fp, dayElem) {
                const date = dayElem.dateObj;
                const dateStr = date.toISOString().slice(0,10);
                if (blockedDates.includes(dateStr)) {
                    dayElem.classList.add('fecha-reservada');
                }
            }
        };
    }

    if (document.getElementById('fecha_inicio')) {
        window.flatpickrInicio = flatpickr('#fecha_inicio', Object.assign(flatpickrOptions('fecha_inicio'), {
            onChange: function(selectedDates, dateStr, instance) {
                if (window.flatpickrFin) {
                    let disables = blockedDates.slice();
                    if (dateStr) {
                        disables.push(function(date) {
                            return date.toISOString().slice(0,10) < dateStr;
                        });
                        window.flatpickrFin.set('minDate', dateStr);
                    } else {
                        window.flatpickrFin.set('minDate', today);
                    }
                    window.flatpickrFin.set('disable', disables);
                    // Forzar redibujado visual del calendario de fin
                    if (window.flatpickrFin.isOpen) {
                        window.flatpickrFin.close();
                        window.flatpickrFin.open();
                    }
                    // Si la fecha de fin es menor a la de inicio, limpiar
                    const finVal = document.getElementById('fecha_fin').value;
                    if (finVal && finVal < dateStr) {
                        document.getElementById('fecha_fin').value = '';
                    }
                }
            }
        }));
    }
    if (document.getElementById('fecha_fin')) {
        window.flatpickrFin = flatpickr('#fecha_fin', Object.assign(flatpickrOptions('fecha_fin'), {
            minDate: today,
            disable: blockedDates,
            onDayCreate: function(dObj, dStr, fp, dayElem) {
                const date = dayElem.dateObj;
                const dateStr = date.toISOString().slice(0,10);
                // Bloquear visualmente fechas menores a la de inicio
                const inicioVal = document.getElementById('fecha_inicio').value;
                if (inicioVal && dateStr < inicioVal) {
                    dayElem.classList.add('flatpickr-disabled');
                    dayElem.classList.add('flatpickr-disabled-day');
                    dayElem.setAttribute('aria-disabled', 'true');
                }
                if (blockedDates.includes(dateStr)) {
                    dayElem.classList.add('fecha-reservada');
                }
            }
        }));
    }

    // --- Enable/disable Ocupar button for admin/superuser ---
    var btnOcupar = document.getElementById('btn-ocupar-admin');
    var inputInicio = document.getElementById('fecha_inicio');
    var inputFin = document.getElementById('fecha_fin');
    function checkOcuparButtonState() {
        if (!btnOcupar || !inputInicio || !inputFin) return;
        const valInicio = inputInicio.value;
        const valFin = inputFin.value;
        if (valInicio && valFin) {
            // Check date validity
            const start = new Date(valInicio);
            const end = new Date(valFin);
            if (end >= start) {
                btnOcupar.disabled = false;
                return;
            }
        }
        btnOcupar.disabled = true;
    }
    if (btnOcupar && inputInicio && inputFin) {
        inputInicio.addEventListener('change', checkOcuparButtonState);
        inputFin.addEventListener('change', checkOcuparButtonState);
        // Also check on page load in case of autofill
        checkOcuparButtonState();
        // Validación extra para input manual
        inputFin.addEventListener('input', function() {
            if (inputInicio.value && inputFin.value && inputFin.value < inputInicio.value) {
                inputFin.value = '';
            }
            checkOcuparButtonState();
        });
        inputFin.addEventListener('blur', function() {
            if (inputInicio.value && inputFin.value && inputFin.value < inputInicio.value) {
                inputFin.value = '';
            }
            checkOcuparButtonState();
        });
    }
});