// Scripts básicos para Belgrano Tickets
document.addEventListener('DOMContentLoaded', function() {
    console.log('Belgrano Tickets cargado correctamente');
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Función para actualizar estado de tickets
    function updateTicketStatus(ticketId, status) {
        fetch(`/api/tickets/${ticketId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status })
        })
        .then(response => response.json())
        .then(data => {
            showNotification('Estado actualizado correctamente', 'success');
        })
        .catch(error => {
            showNotification('Error al actualizar estado', 'danger');
        });
    }
    
    // Exponer funciones globalmente
    window.BelgranoTickets = {
        showNotification,
        updateTicketStatus
    };
});
