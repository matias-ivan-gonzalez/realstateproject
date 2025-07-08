// Lógica para habilitar/deshabilitar el botón de confirmación de upgrade en upgrade_reserva.html
// El botón se habilita solo si todos los selects tienen una opción válida seleccionada

document.addEventListener('DOMContentLoaded', function() {
    // Buscar todos los selects de upgrade
    const selects = document.querySelectorAll('select[id^="upgrade_"]');
    const btnConfirmar = document.querySelector('button[type="submit"].btn-success');
    if (!btnConfirmar || selects.length === 0) return;

    function checkAllSelected() {
        for (let select of selects) {
            // Si el select está visible y tiene required, debe tener valor
            if (!select.disabled && select.required && !select.value) {
                btnConfirmar.disabled = true;
                return;
            }
        }
        btnConfirmar.disabled = false;
    }

    selects.forEach(function(select) {
        select.addEventListener('change', checkAllSelected);
    });

    // Inicial
    checkAllSelected();
});
