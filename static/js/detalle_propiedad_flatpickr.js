// Flatpickr initialization for date blocking

document.addEventListener('DOMContentLoaded', function() {
    // Helper: get all blocked dates as array of strings (YYYY-MM-DD)
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

    // Flatpickr config
    const blockedDates = getBlockedDates();
    const today = new Date().toISOString().slice(0,10);
    const flatpickrOptionsInicio = {
        dateFormat: 'Y-m-d',
        minDate: today,
        disable: blockedDates,
        locale: 'es',
        allowInput: false,
        onChange: function(selectedDates, dateStr, instance) {
            if (window.flatpickrFin) {
                window.flatpickrFin.set('minDate', dateStr);
            }
        }
    };
    const flatpickrOptionsFin = {
        dateFormat: 'Y-m-d',
        minDate: today,
        disable: blockedDates,
        locale: 'es',
        allowInput: false
    };
    // Init flatpickr on both date inputs if present
    if (document.getElementById('fecha_inicio')) {
        window.flatpickrInicio = flatpickr('#fecha_inicio', flatpickrOptionsInicio);
    }
    if (document.getElementById('fecha_fin')) {
        window.flatpickrFin = flatpickr('#fecha_fin', flatpickrOptionsFin);
    }
});

// --- Flatpickr para deshabilitar fechas ocupadas/reservadas ---
document.addEventListener('DOMContentLoaded', function() {
    // Helper: obtener todas las fechas bloqueadas como array de strings (YYYY-MM-DD)
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
    // Flatpickr config
    const blockedDates = getBlockedDates();
    const today = new Date().toISOString().slice(0,10);
    const flatpickrOptionsInicio = {
        dateFormat: 'Y-m-d',
        minDate: today,
        disable: blockedDates,
        locale: 'es',
        allowInput: false,
        onChange: function(selectedDates, dateStr, instance) {
            if (window.flatpickrFin) {
                window.flatpickrFin.set('minDate', dateStr);
            }
        }
    };
    const flatpickrOptionsFin = {
        dateFormat: 'Y-m-d',
        minDate: today,
        disable: blockedDates,
        locale: 'es',
        allowInput: false
    };
    // Inicializar flatpickr en los inputs de fecha
    if (document.getElementById('fecha_inicio')) {
        window.flatpickrInicio = flatpickr('#fecha_inicio', flatpickrOptionsInicio);
    }
    if (document.getElementById('fecha_fin')) {
        window.flatpickrFin = flatpickr('#fecha_fin', flatpickrOptionsFin);
    }
});

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
}
