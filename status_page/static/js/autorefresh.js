$(document).ready(function() {
    updateMap();
});

window.setInterval(function() {
    $('#users').bootstrapTable('refresh');
    updateMap();
}, 5000);  // Refresh every 5 secs

window.setInterval(function() {
    $('#atis').bootstrapTable('refresh');
}, 60000);  // Refresh every minutes

function rowStyle(row, index) {
    classes = {};

    if(row.description == undefined) {
        classes['classes'] = 'warning';
    }

    return classes;
}