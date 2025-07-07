// Lógica para habilitar/deshabilitar el botón de confirmación de upgrade
// El select debe tener id="select-propiedad-upgrade" y el botón id="btn-confirmar-upgrade"

document.addEventListener('DOMContentLoaded', function() {
    const selectProp = document.getElementById('select-propiedad-upgrade');
    const btnConfirmar = document.getElementById('btn-confirmar-upgrade');
    if (!selectProp || !btnConfirmar) return;

    // Deshabilitar el botón por defecto
    btnConfirmar.disabled = true;

    // Habilitar solo si hay una opción válida seleccionada
    selectProp.addEventListener('change', function() {
        btnConfirmar.disabled = !selectProp.value;
    });

    // Por si el valor ya está seteado (autofill, etc)
    btnConfirmar.disabled = !selectProp.value;
});
