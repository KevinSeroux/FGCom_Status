$(document).ready(function() {
    updateMap();

    $('#users').bootstrapTable().on('click-row.bs.table',
      function (e, row, $element) {
        center(row.longitude, row.latitude);
    });
});

window.setInterval(function() {
    $('#users').bootstrapTable('refresh');
    updateMap();
}, 5000);  // Refresh every 5 secs

window.setInterval(function() {
    $('#auto_info').bootstrapTable('refresh');
}, 60000);  // Refresh every minutes

function rowStyle(row, index) {
    classes = {};

    if(row.description == undefined) {
        classes['classes'] = 'warning';
    }

    return classes;
}