window.setInterval(function() {
    $('#users').bootstrapTable('refresh');
    updateMap();
}, 5000);  // Refresh every 5 secs

window.setInterval(function() {
    $('#atis').bootstrapTable('refresh');
}, 60000);  // Refresh every minutes

$(document).ready(function() {
    updateMap();
});