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
    const flatpickrOptions = {
        dateFormat: 'Y-m-d',
        minDate: today,
        disable: blockedDates,
        locale: 'es',
        allowInput: false
    };
    // Init flatpickr on both date inputs if present
    if (document.getElementById('fecha_inicio')) {
        flatpickr('#fecha_inicio', flatpickrOptions);
    }
    if (document.getElementById('fecha_fin')) {
        flatpickr('#fecha_fin', flatpickrOptions);
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
    const flatpickrOptions = {
        dateFormat: 'Y-m-d',
        minDate: today,
        disable: blockedDates,
        locale: 'es',
        allowInput: false
    };
    // Inicializar flatpickr en los inputs de fecha
    if (document.getElementById('fecha_inicio')) {
        flatpickr('#fecha_inicio', flatpickrOptions);
    }
    if (document.getElementById('fecha_fin')) {
        flatpickr('#fecha_fin', flatpickrOptions);
    }
});
