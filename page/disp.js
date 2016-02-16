$(function(){
    function jsonload(filePath) {
        var data = new XMLHttpRequest();
        data.open("GET", filePath, false);
        data.send(null);
	return JSON.parse(data.responseText);
    }
    function rewriteBody() {
	var JSONPATH = 'gpu_state.json';
	var data = jsonload(JSONPATH);

	$('#lastupdated').text('Last Updated: ' + data.__LASTUPDATED__);

	$.each(data, function(server_name, value){
	    if (server_name == '__LASTUPDATED__') {
		return;
	    }
	    if (server_name == '__INTERVAL__') {
		return;
	    }
	    var firstflg = true;
	    if (value.GPUs.length == 0) {
		var commonstr = '<td class="danger">' +
		    + value.ErrorType + '</td>'+
		    '<td class="danger"></td>' +
		    '<td class="danger"></td>' +
		    '<td class="danger"></td>' +
		    '<td class="danger"></td>' +
		    '<td class="danger"></td>' +
		    '</tr>';
		$('#gputb').append('<tr><td rowspan="1">' +
				   server_name + '</td><td rowspan="1">' +
				   value.Owner + '</td>' +
				   commonstr);
		$('#gputb tbody').append();
	    }
	    for (var index = 0; index < value.GPUs.length; index++) {
		var commonstr;
		if (value.GPUs[index].used_memory < 23 || (value.GPUs[index].used_memory < 223 && value.GPUs[index].gpu_usage == 0)) {
		    commonstr = '<td>' + value.GPUs[index].id + '</td>'+
			'<td>' + value.GPUs[index].name + '</td>' +
			'<td>' + String(value.GPUs[index].used_memory/value.GPUs[index].total_memory).slice(0, 4) + '</td>' +
			'<td>' + value.GPUs[index].used_memory + '</td>' +
			'<td>' + value.GPUs[index].total_memory + '</td>' +
			'<td>' + value.GPUs[index].gpu_usage/100 + '</td>' +
			'</tr>';
		} else if (value.GPUs[index].id == 'error') {
		    commonstr = '<td class="danger">' + value.GPUs[index].id + '</td>'+
			'<td class="danger"></td>' +
			'<td class="danger"></td>' +
			'<td class="danger"></td>' +
			'<td class="danger"></td>' +
			'<td class="danger"></td>' +
			'</tr>';
		} else {
		    commonstr = '<td class="warning">' + value.GPUs[index].id + '</td>'+
			'<td class="warning">' + value.GPUs[index].name + '</td>' +
			'<td class="warning">' + String(value.GPUs[index].used_memory/value.GPUs[index].total_memory).slice(0, 4) + '</td>' +
			'<td class="warning">' + value.GPUs[index].used_memory + '</td>' +
			'<td class="warning">' + value.GPUs[index].total_memory + '</td>' +
			'<td class="warning">' + value.GPUs[index].gpu_usage/100 + '</td>' +
			'</tr>';
		}
		if (firstflg) {
		    $('#gputb').append('<tr><td rowspan="'+
				       value.GPUs.length +
				       '">' +
				       server_name + '</td><td rowspan="' +
				       value.GPUs.length +
				       '">' +
				       value.Owner + '</td>' +
				       commonstr);
		    firstflg = false;
		} else {
		    $('#gputb').append('<tr>' + commonstr);
		};
		$('#gputb tbody').append();
	    };
	});

	$.each(data, function(server_name, value){
	    if (server_name == '__LASTUPDATED__') {
		return;
	    }
	    if (server_name == '__INTERVAL__') {
		return;
	    }
	    var firstflg = true;
	    for (var index = 0; index < value.processes.length; index++) {
		var commonstr = '<td>' + value.processes[index].pid + '</td>'+
		    '<td>' + value.processes[index].gpu_id + '</td>' +
		    '<td>' + value.processes[index].user + '</td>' +
		    '<td>' + value.processes[index].lstart + '</td>' +
		    '<td>' + value.processes[index].gpu_memory + '</td>' +
		    '</tr>';
		if (firstflg) {
		    $('#processtb').append('<tr><td rowspan="'+
					   value.processes.length +
					   '">' +
					   server_name + '</td>' +
					   commonstr);
		    firstflg = false;
		} else {
		    $('#processtb').append('<tr>' + commonstr);
		};
		$('#processtb tbody').append();
	    };
	});
	if (!(data.__INTERVAL__ === undefined)) {
	    setTimeout(function(){
		location.reload();
	    }, 1000*data.__INTERVAL__);
	}
    };
    rewriteBody();
});