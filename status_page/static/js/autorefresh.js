window.setInterval(function() {
    $('#users').bootstrapTable('refresh');
}, 5000);  // Refresh every 5 secs

window.setInterval(function() {
    $('#atis').bootstrapTable('refresh');
}, 60000);  // Refresh every minutes