// Validación de fechas para inhabilitar propiedad

document.addEventListener('DOMContentLoaded', function() {
    // Utilidades para rangos
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

    let hoy = new Date();
    hoy.setHours(0,0,0,0);
    let reservasPendientes = [];
    let reservasConcretadas = [];
    let reservasEnCurso = [];
    let ocupacionesFuturas = [];
    let ocupacionesEnCurso = [];

    // Clasificar reservas
    if (window.fechasReservadas) {
        window.fechasReservadas.forEach(function(reserva) {
            let rIni = new Date(reserva.inicio);
            let rFin = new Date(reserva.fin);
            // Mostrar todas las reservas en el calendario
            if (reserva.estado === 'pendiente') {
                if (rIni <= hoy && rFin >= hoy) {
                    reservasEnCurso.push(reserva);
                } else {
                    reservasPendientes.push(reserva);
                }
            } else if (reserva.estado === 'concretada') {
                if (rIni <= hoy && rFin >= hoy) {
                    reservasEnCurso.push(reserva);
                } else if (rIni > hoy) {
                    reservasConcretadas.push(reserva);
                } else {
                    // pasada
                }
            } else {
                // Otras reservas (cancelada, etc) también deben mostrarse como bloqueadas
                reservasConcretadas.push(reserva);
            }
        });
    }

    // Clasificar ocupaciones
    if (window.fechasOcupadas) {
        window.fechasOcupadas.forEach(function(ocupacion) {
            let oIni = new Date(ocupacion.inicio);
            let oFin = new Date(ocupacion.fin);
            if (oIni <= hoy && oFin >= hoy) {
                ocupacionesEnCurso.push(ocupacion);
            } else if (oIni > hoy) {
                ocupacionesFuturas.push(ocupacion);
            }
        });
    }

    // --- Flatpickr: bloquear fechas con reservas/ocupaciones en curso ---
    function isFechaBloqueada(date) {
        // Bloquear reservas en curso
        for (let reserva of reservasEnCurso) {
            let rIni = new Date(reserva.inicio);
            let rFin = new Date(reserva.fin);
            if (date >= rIni && date <= rFin) return true;
        }
        // Bloquear ocupaciones en curso
        for (let ocup of ocupacionesEnCurso) {
            let oIni = new Date(ocup.inicio);
            let oFin = new Date(ocup.fin);
            if (date >= oIni && date <= oFin) return true;
        }
        return false;
    }

    const fechaInicio = flatpickr("#fecha_inicio", {
        dateFormat: "Y-m-d",
        minDate: "today",
        disable: [isFechaBloqueada],
        onChange: function(selectedDates, dateStr, instance) {
            if (fechaFin) fechaFin.set('minDate', dateStr);
            checkRangoSeleccionado();
        }
    });
    const fechaFin = flatpickr("#fecha_fin", {
        dateFormat: "Y-m-d",
        minDate: "today",
        disable: [isFechaBloqueada],
        onChange: function(selectedDates, dateStr, instance) {
            checkRangoSeleccionado();
        }
    });

    // --- Visualización de colores en el calendario ---
    function pintarFechasEspeciales() {
        setTimeout(function() {
            document.querySelectorAll('.flatpickr-day').forEach(function(day) {
                let fecha = day.dateObj ? day.dateObj.toISOString().slice(0,10) : day.getAttribute('aria-label');
                if (!fecha) return;
                // Reservas pendientes
                for (let r of reservasPendientes) {
                    if (fecha >= r.inicio && fecha <= r.fin) {
                        day.classList.add('fecha-reserva-futura');
                    }
                }
                // Reservas concretadas
                for (let r of reservasConcretadas) {
                    if (fecha >= r.inicio && fecha <= r.fin) {
                        day.classList.add('fecha-reserva-futura');
                        day.style.background = '#0d3a5e';
                        day.style.color = '#fff';
                    }
                }
                // Ocupaciones futuras
                for (let o of ocupacionesFuturas) {
                    if (fecha >= o.inicio && fecha <= o.fin) {
                        if (o.tipo === 'inhabilitacion') {
                            day.classList.add('fecha-bloqueada');
                        } else {
                            day.classList.add('fecha-ocupacion-futura');
                        }
                    }
                }
            });
        }, 10);
    }
    document.addEventListener('click', pintarFechasEspeciales);
    document.addEventListener('input', pintarFechasEspeciales);
    pintarFechasEspeciales();

    // --- Lógica de rango seleccionado ---
    function checkRangoSeleccionado() {
        const fechaInicioVal = document.getElementById('fecha_inicio').value;
        const fechaFinVal = document.getElementById('fecha_fin').value;
        const btnConfirmar = document.getElementById('btn-inhabilitar');
        const accionReserva = document.getElementById('accion_reserva');
        // Deshabilitar botón si no hay ambas fechas
        if (!fechaInicioVal || !fechaFinVal) {
            if (btnConfirmar) btnConfirmar.disabled = true;
            mostrarReservasAfectadas([]);
            mostrarOcupacionesAfectadas([]);
            return;
        }
        const inicio = new Date(fechaInicioVal);
        const fin = new Date(fechaFinVal);
        // Si hay reserva u ocupación en curso en el rango, bloquear
        if (hayReservaEnCursoEnRango(inicio, fin) || hayOcupacionEnCursoEnRango(inicio, fin)) {
            if (btnConfirmar) btnConfirmar.disabled = true;
            mostrarReservasAfectadas([]);
            mostrarOcupacionesAfectadas([]);
            return;
        }
        // Si hay reserva pendiente en el rango, mostrar opciones de upgrade/reembolso
        const reservasPendientesEnRango = hayReservaPendienteEnRango(inicio, fin);
        console.log('Reservas pendientes en el rango:', reservasPendientesEnRango);
        mostrarReservasAfectadas(reservasPendientesEnRango);
        // Ocupaciones futuras en el rango
        const ocupacionesFuturasEnRango = hayOcupacionFuturaEnRango(inicio, fin);
        mostrarOcupacionesAfectadas(ocupacionesFuturasEnRango);
        // Habilitar botón solo si no hay reservas pendientes o si hay y se seleccionó acción
        if (reservasPendientesEnRango.length > 0) {
            document.getElementById('reservas-afectadas').style.display = 'block';
            if (btnConfirmar) btnConfirmar.disabled = !accionReserva.value;
        } else {
            document.getElementById('reservas-afectadas').style.display = 'none';
            if (btnConfirmar) btnConfirmar.disabled = false;
        }
    }

    function hayReservaEnCursoEnRango(inicio, fin) {
        for (let r of reservasEnCurso) {
            let rIni = new Date(r.inicio);
            let rFin = new Date(r.fin);
            if (!(fin < rIni || inicio > rFin)) return true;
        }
        return false;
    }
    function hayOcupacionEnCursoEnRango(inicio, fin) {
        for (let o of ocupacionesEnCurso) {
            let oIni = new Date(o.inicio);
            let oFin = new Date(o.fin);
            if (!(fin < oIni || inicio > oFin)) return true;
        }
        return false;
    }
    function hayReservaPendienteEnRango(inicio, fin) {
        let reservas = [];
        for (let r of reservasPendientes) {
            let rIni = new Date(r.inicio);
            let rFin = new Date(r.fin);
            if (!(fin < rIni || inicio > rFin)) reservas.push(r);
        }
        return reservas;
    }
    function hayOcupacionFuturaEnRango(inicio, fin) {
        let ocupaciones = [];
        for (let o of ocupacionesFuturas) {
            let oIni = new Date(o.inicio);
            let oFin = new Date(o.fin);
            if (!(fin < oIni || inicio > oFin)) ocupaciones.push(o);
        }
        return ocupaciones;
    }

    // Mostrar reservas afectadas (solo pendientes)
    function mostrarReservasAfectadas(reservas) {
        const panel = document.getElementById('reservas-afectadas');
        const lista = document.getElementById('lista-reservas');
        const btnReintegrar = document.getElementById('btn-reintegrar');
        const btnUpgrade = document.getElementById('btn-upgrade');
        const accionReserva = document.getElementById('accion_reserva');
        const btnConfirmar = document.getElementById('btn-inhabilitar');
        if (!panel || !lista) return;
        panel.style.display = 'none';
        lista.innerHTML = '';
        if (btnReintegrar) { btnReintegrar.style.display = 'none'; btnReintegrar.onclick = null; }
        if (btnUpgrade) { btnUpgrade.style.display = 'none'; btnUpgrade.onclick = null; }
        if (accionReserva) accionReserva.value = '';
        if (reservas.length > 0) {
            reservas.forEach(function(reserva) {
                const item = document.createElement('div');
                item.className = 'reserva-afectada';
                item.innerHTML = `
                    <p class="mb-1"><strong>Cliente ID:</strong> ${reserva.cliente_id || 'N/A'}</p>
                    <p class="mb-1"><strong>Fechas:</strong> ${reserva.inicio} a ${reserva.fin}</p>
                    <p class="mb-0"><strong>Estado:</strong> ${reserva.estado}</p>
                `;
                lista.appendChild(item);
            });
            panel.style.display = 'block';
            if (btnReintegrar && btnUpgrade && accionReserva && btnConfirmar) {
                btnReintegrar.style.display = 'inline-block';
                btnUpgrade.style.display = 'inline-block';
                btnReintegrar.onclick = function() {
                    accionReserva.value = 'reintegrar';
                    btnConfirmar.disabled = false;
                    btnReintegrar.classList.add('active');
                    btnUpgrade.classList.remove('active');
                };
                btnUpgrade.onclick = function() {
                    accionReserva.value = 'upgrade';
                    btnConfirmar.disabled = false;
                    btnUpgrade.classList.add('active');
                    btnReintegrar.classList.remove('active');
                };
                btnConfirmar.disabled = true;
            }
        }
    }
    
    // Mostrar ocupaciones afectadas (futuras)
    function mostrarOcupacionesAfectadas(ocupaciones) {
        const panel = document.getElementById('ocupaciones-afectadas');
        const lista = document.getElementById('lista-ocupaciones');
        if (!panel || !lista) return;
        
        if (ocupaciones.length > 0) {
            lista.innerHTML = '';
            ocupaciones.forEach(function(ocupacion) {
                const item = document.createElement('div');
                item.className = 'ocupacion-afectada';
                const tipo = ocupacion.tipo === 'encargado' ? 'Encargado' : 'Administrador';
                item.innerHTML = `
                    <p class="mb-1"><strong>Tipo:</strong> ${tipo}</p>
                    <p class="mb-1"><strong>Fechas:</strong> ${ocupacion.inicio} a ${ocupacion.fin}</p>
                    ${ocupacion.encargado_id ? `<p class="mb-0"><strong>Encargado ID:</strong> ${ocupacion.encargado_id}</p>` : ''}
                `;
                lista.appendChild(item);
            });
            panel.style.display = 'block';
        } else {
            panel.style.display = 'none';
        }
    }

    // Limpiar acción seleccionada si se cambia el rango
    document.getElementById('fecha_inicio').addEventListener('change', function() {
        const accionReserva = document.getElementById('accion_reserva');
        if (accionReserva) accionReserva.value = '';
        checkRangoSeleccionado();
    });
    document.getElementById('fecha_fin').addEventListener('change', function() {
        const accionReserva = document.getElementById('accion_reserva');
        if (accionReserva) accionReserva.value = '';
        checkRangoSeleccionado();
    });
    
    // Verificar estado inicial del botón
    checkRangoSeleccionado();
}); 