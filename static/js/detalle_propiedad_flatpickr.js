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
    const currentYear = new Date().getFullYear();

    function flatpickrOptions(inputId) {
        let options = {
            dateFormat: 'Y-m-d',
            minDate: today,
            disable: [
                function(date) {
                    const todayDate = new Date();
                    todayDate.setHours(0,0,0,0);
                    return date.getTime() === todayDate.getTime();
                }
            ].concat(blockedDates),
            locale: 'es',
            allowInput: false,
            onDayCreate: function(dObj, dStr, fp, dayElem) {
                const date = dayElem.dateObj;
                const dateStr = date.toISOString().slice(0,10);
                if (blockedDates.includes(dateStr) && dateStr >= today) {
                    dayElem.classList.add('fecha-reservada');
                }
            }
        };
        // Para encargados, limitar solo al año actual
        if (window.esEncargado) {
            options.maxDate = `${currentYear}-12-31`;
            options.minDate = today;
        }
        return options;
    }

    if (document.getElementById('fecha_inicio')) {
        window.flatpickrInicio = flatpickr('#fecha_inicio', Object.assign(flatpickrOptions('fecha_inicio'), {
            onChange: function(selectedDates, dateStr, instance) {
                if (window.flatpickrFin) {
                    let disables = blockedDates.slice();
                    let maxDate = null;
                    if (dateStr) {
                        disables.push(function(date) {
                            // Deshabilitar fechas menores o iguales a la de inicio
                            return date.toISOString().slice(0,10) <= dateStr;
                        });
                        window.flatpickrFin.set('minDate', dateStr);
                        // Calcular el primer día bloqueado posterior a la fecha de inicio
                        let nextBlocked = blockedDates
                            .filter(d => d > dateStr)
                            .sort()[0];
                        if (nextBlocked) {
                            // El máximo permitido es el día anterior al primer bloqueado
                            let max = new Date(nextBlocked);
                            max.setDate(max.getDate() - 1);
                            maxDate = max.toISOString().slice(0,10);
                            window.flatpickrFin.set('maxDate', maxDate);
                        } else {
                            // Para encargados, limitar al año actual
                            if (window.esEncargado) {
                                window.flatpickrFin.set('maxDate', `${currentYear}-12-31`);
                            } else {
                                window.flatpickrFin.set('maxDate', null);
                            }
                        }
                    } else {
                        window.flatpickrFin.set('minDate', today);
                        // Para encargados, limitar al año actual
                        if (window.esEncargado) {
                            window.flatpickrFin.set('maxDate', `${currentYear}-12-31`);
                        } else {
                            window.flatpickrFin.set('maxDate', null);
                        }
                    }
                    window.flatpickrFin.set('disable', disables);
                    // Forzar redibujado visual del calendario de fin
                    if (window.flatpickrFin.isOpen) {
                        window.flatpickrFin.close();
                        window.flatpickrFin.open();
                    }
                    // Si la fecha de fin es menor o igual a la de inicio, limpiar
                    const finVal = document.getElementById('fecha_fin').value;
                    if (finVal && finVal <= dateStr) {
                        document.getElementById('fecha_fin').value = '';
                    }
                    // Si la fecha de fin es mayor al máximo permitido, limpiar
                    if (maxDate && finVal && finVal > maxDate) {
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
                // Bloquear visualmente fechas menores o iguales a la de inicio
                const inicioVal = document.getElementById('fecha_inicio').value;
                if (inicioVal && dateStr <= inicioVal) {
                    dayElem.classList.add('flatpickr-disabled');
                    dayElem.classList.add('flatpickr-disabled-day');
                    dayElem.setAttribute('aria-disabled', 'true');
                }
                if (blockedDates.includes(dateStr) && dateStr >= today) {
                    dayElem.classList.add('fecha-reservada');
                }
            }
        }));
    }

    // --- Enable/disable Ocupar button for admin/superuser/encargado ---
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