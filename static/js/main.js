// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
            if (alert && bootstrap.Alert.getOrCreateInstance) {
                bootstrap.Alert.getOrCreateInstance(alert).close();
            }
        });
    }, 5000);
});
