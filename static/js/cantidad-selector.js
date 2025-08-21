// Funciones para manejar selectores de cantidad en productos
function cambiarCantidad(productoId, delta) {
    const input = document.getElementById(`cantidad-${productoId}`);
    let valor = parseInt(input.value) || 1;
    valor = Math.max(1, Math.min(99, valor + delta));
    input.value = valor;
}

// Inicializar selectores de cantidad cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Agregar event listeners para inputs de cantidad
    const cantidadInputs = document.querySelectorAll('input[id^="cantidad-"]');
    cantidadInputs.forEach(input => {
        input.addEventListener('change', function() {
            let valor = parseInt(this.value) || 1;
            valor = Math.max(1, Math.min(99, valor));
            this.value = valor;
        });
    });
});
