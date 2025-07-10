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
    let fechasInhabilitadas = [];
    if (window.fechasInhabilitadas) {
        window.fechasInhabilitadas.forEach(function(rango) {
            let ini = new Date(rango.inicio);
            let fin = new Date(rango.fin);
            while (ini <= fin) {
                fechasInhabilitadas.push(ini.toISOString().slice(0,10));
                ini.setDate(ini.getDate() + 1);
            }
        });
    }

    // Clasificar reservas
    if (window.fechasReservadas) {
        window.fechasReservadas.forEach(function(reserva) {
            let rIni = new Date(reserva.inicio);
            let rFin = new Date(reserva.fin);
            // Normalizar estado a minúsculas para evitar problemas de mayúsculas/minúsculas
            let estado = (reserva.estado || '').toLowerCase();
            if (estado === 'futura') {
                if (rIni <= hoy && rFin >= hoy) {
                    reservasEnCurso.push(reserva);
                } else {
                    reservasPendientes.push(reserva);
                }
            } else if (estado === 'concretada') {
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
    console.log('reservasPendientes:', reservasPendientes);

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

    function isFechaInhabilitada(date) {
        return fechasInhabilitadas.includes(date.toISOString().slice(0,10));
    }

    // --- Flatpickr: bloquear fechas con reservas/ocupaciones en curso e inhabilitadas ---
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
        // Bloquear fechas inhabilitadas
        if (isFechaInhabilitada(date)) return true;
        return false;
    }

    // Flatpickr config: agregar isFechaInhabilitada a disable
    const fechaInicio = flatpickr("#fecha_inicio", {
        dateFormat: "Y-m-d",
        minDate: "today",
        disable: [isFechaBloqueada, isFechaInhabilitada],
        onChange: function(selectedDates, dateStr, instance) {
            if (fechaFin) fechaFin.set('minDate', dateStr);
            checkRangoSeleccionado();
        }
    });
    const fechaFin = flatpickr("#fecha_fin", {
        dateFormat: "Y-m-d",
        minDate: "today",
        disable: [
            function(date) {
                const fechaInicioVal = document.getElementById('fecha_inicio').value;
                if (!fechaInicioVal) return true; // No permitir si no hay inicio
                const inicio = new Date(fechaInicioVal);
                const fin = date;
                // Contar reservas futuras en el rango
                let reservasEnRango = 0;
                for (let r of reservasPendientes) {
                    let rIni = new Date(r.inicio);
                    let rFin = new Date(r.fin);
                    if (!(fin < rIni || inicio > rFin)) reservasEnRango++;
                }
                // Contar ocupaciones futuras en el rango
                let ocupacionesEnRango = 0;
                for (let o of ocupacionesFuturas) {
                    let oIni = new Date(o.inicio);
                    let oFin = new Date(o.fin);
                    if (!(fin < oIni || inicio > oFin)) ocupacionesEnRango++;
                }
                // Contar fechas inhabilitadas en el rango
                let inhabilitadasEnRango = 0;
                let current = new Date(inicio);
                while (current <= fin) {
                    if (isFechaInhabilitada(current)) inhabilitadasEnRango++;
                    current.setDate(current.getDate() + 1);
                }
                // Permitir solo si la suma es 0 o 1 (máximo una reserva, ocupación o inhabilitación)
                return (reservasEnRango + ocupacionesEnRango + inhabilitadasEnRango) > 1;
            },
            isFechaBloqueada,
            isFechaInhabilitada
        ],
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
                // Solo mostrar reservas futuras
                for (let r of reservasPendientes) {
                    if (fecha >= r.inicio && fecha <= r.fin) {
                        day.classList.add('fecha-reserva-futura');
                    }
                }
                // Solo mostrar ocupaciones futuras (empleado/encargado/admin)
                for (let o of ocupacionesFuturas) {
                    if (fecha >= o.inicio && fecha <= o.fin) {
                        day.classList.add('fecha-ocupacion-futura');
                    }
                }
                // Bloquear visualmente días con reservas en curso
                for (let r of reservasEnCurso) {
                    if (fecha >= r.inicio && fecha <= r.fin) {
                        day.classList.add('flatpickr-disabled');
                        day.classList.add('flatpickr-disabled-day');
                        day.setAttribute('aria-disabled', 'true');
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
        // PERO SI HAY RESERVA FUTURA EN EL RANGO, mostrar los botones igual
        const reservasPendientesEnRango = hayReservaPendienteEnRango(inicio, fin);
        if ((hayReservaEnCursoEnRango(inicio, fin) || hayOcupacionEnCursoEnRango(inicio, fin)) && reservasPendientesEnRango.length === 0) {
            if (btnConfirmar) btnConfirmar.disabled = true;
            mostrarReservasAfectadas([]);
            mostrarOcupacionesAfectadas([]);
            return;
        }
        // Mostrar SIEMPRE los botones si hay reservas futuras, aunque haya reservas/ocupaciones en curso
        console.log('reservasPendientesEnRango:', reservasPendientesEnRango);
        mostrarReservasAfectadas(reservasPendientesEnRango);
        // Ocupaciones futuras en el rango
        const ocupacionesFuturasEnRango = hayOcupacionFuturaEnRango(inicio, fin);
        mostrarOcupacionesAfectadas(ocupacionesFuturasEnRango);
        // Habilitar botón solo si no hay reservas futuras o si hay y se seleccionó acción
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

    // Mostrar reservas afectadas (solo futuras)
    function mostrarReservasAfectadas(reservas) {
        const panel = document.getElementById('reservas-afectadas');
        const lista = document.getElementById('lista-reservas');
        const btnReintegrar = document.getElementById('btn-reintegrar');
        const btnUpgrade = document.getElementById('btn-upgrade');
        const accionReserva = document.getElementById('accion_reserva');
        const btnConfirmar = document.getElementById('btn-inhabilitar');
        if (!panel || !lista) return;
        lista.innerHTML = '';
        // Siempre ocultar botones y limpiar acciones al inicio
        if (btnReintegrar) { btnReintegrar.style.display = 'none'; btnReintegrar.onclick = null; btnReintegrar.classList.remove('active'); }
        if (btnUpgrade) { btnUpgrade.style.display = 'none'; btnUpgrade.onclick = null; btnUpgrade.classList.remove('active'); }
        if (accionReserva) accionReserva.value = '';
        panel.style.display = 'none';
        if (reservas.length > 0) {
            // Filtrar reservas válidas (que tengan cliente_id, inicio y fin)
            const reservasValidas = reservas.filter(r => r.cliente_id && r.inicio && r.fin);
            // Filtrar reservas duplicadas por cliente_id + fechas
            const reservasUnicas = [];
            const seen = new Set();
            reservasValidas.forEach(r => {
                const key = `${r.cliente_id}-${r.inicio}-${r.fin}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    reservasUnicas.push(r);
                }
            });
            // Obtener los IDs únicos de cliente
            const clienteIds = [...new Set(reservasUnicas.map(r => r.cliente_id).filter(Boolean))];
            // Llamar al backend para obtener los nombres
            fetch('/api/usuarios_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: clienteIds })
            })
            .then(response => response.json())
            .then(data => {
                const usuariosMap = {};
                if (data.usuarios) {
                    data.usuarios.forEach(u => {
                        usuariosMap[u.id] = `${u.nombre} ${u.apellido}`;
                    });
                }
                reservasUnicas.forEach(function(reserva) {
                    const item = document.createElement('div');
                    item.className = 'reserva-afectada';
                    const nombreCliente = usuariosMap[reserva.cliente_id] || 'Desconocido';
                    item.innerHTML = `
                        <p class=\"mb-1\"><strong>Cliente:</strong> ${nombreCliente}</p>
                        <p class=\"mb-1\"><strong>Fechas:</strong> ${reserva.inicio} a ${reserva.fin}</p>
                    `;
                    lista.appendChild(item);
                });
                panel.style.display = 'block';
                // Mostrar SIEMPRE los botones si hay reservas futuras
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
                    // El botón de confirmar debe estar deshabilitado hasta que se seleccione una acción
                    btnConfirmar.disabled = true;
                }
            });
        } else {
            // Si no hay reservas futuras, ocultar panel y botones
            panel.style.display = 'none';
            if (btnReintegrar) btnReintegrar.style.display = 'none';
            if (btnUpgrade) btnUpgrade.style.display = 'none';
        }
    }
    
    // Mostrar ocupaciones afectadas (futuras)
    function mostrarOcupacionesAfectadas(ocupaciones) {
        const panel = document.getElementById('ocupaciones-afectadas');
        const lista = document.getElementById('lista-ocupaciones');
        if (!panel || !lista) return;

        if (ocupaciones.length > 0) {
            lista.innerHTML = '<div class="ocupacion-afectada"><p class="mb-1">Hay ocupaciones afectadas.</p></div>';
            panel.style.display = 'block';
        } else {
            panel.style.display = 'none';
        }
    }

    // Limpiar acción seleccionada si se cambia el rango
    
    // Verificar estado inicial del botón
    checkRangoSeleccionado();
}); 