$.jsonrpc.defaultUrl = me2_api_url;
function fetch_base_bottles(callback) {
	$.jsonrpc({
		method : 'manager.btrfs.list_base_bottles',
	}, {
		success : function(result) {
			callback(result.result);
		},
		error : function(error) {
			alert("ERROR"+error);
		}

	});
}

function start_base_bottle(bottle_id) {
	$.jsonrpc({
		method : 'manager.start',
		params : {bundle_id: bottle_id,
			config: null}
	}, {
		success : function(result) {
			console.log("Started "+bottle_id);
			reload_base_bottles();
		},
		error : function(error) {
			console.log("Failed Starting "+bottle_id);
		}

	});
}

function fetch_bottles(callback) {
	$.jsonrpc({
		method : 'manager.btrfs.list_bottles',
	}, {
		success : function(result) {
			callback(result.result);
		},
		error : function(error) {
			alert("ERROR"+error);
		}

	});
}

function trigger_start_base_bottle(bottle_id) {
	start_base_bottle(bottle_id);
}

function trigger_delete_bottle(bottle_id) {
	$.jsonrpc({
		method : 'manager.btrfs.remove',
		params : {bottle_id: bottle_id}
	}, {
		success : function(result) {
			console.log("Dispatch delete of bottle "+bottle_id);
			reload_bottles();
		},
		error : function(error) {
			console.log("Failed deleting of bottle"+bottle_id);
		}

	});
}
function setup_base_bottle_action_buttons(bottle_id) {
	group = $('<div>');
	group.attr('class', 'btn-group');
	clone_button = $('<button>');
	clone_button.attr('class', 'btn').text('Clone');
	clone_button.click(function() {
		trigger_start_base_bottle(bottle_id);
	});
	delete_button = $('<button>');
	delete_button.attr('class', 'btn btn-danger').text('Delete');
	group.append(clone_button);
	group.append(delete_button);
	return group;
}

function setup_bottle_action_buttons(bottle_id) {
	group = $('<div>');
	group.attr('class', 'btn-group');
	delete_button = $('<button>');
	delete_button.attr('class', 'btn btn-danger').text('Delete');
	delete_button.click(function() {
		trigger_delete_bottle(bottle_id);
	});
	group.append(delete_button);
	return group;
}

function update_base_bottles_table(data) {
	body = $("#base_bottles_table").find('tbody');
	body.find('tr').remove();
	for (bottle in data) {
		row = $('<tr>');
		cell1 = $('<td>');
		cell1.append(data[bottle]);
		cell2 = $('<td>');
		cell2.append(setup_base_bottle_action_buttons(data[bottle]));
		row.append(cell1);
		row.append(cell2);
		body.append(row);
	}
	
}

function update_bottles(data) {
	body = $("#bottles_table").find('tbody');
	body.find('tr').remove();
	for (bottle in data) {
		binfo = data[bottle]
		row = $('<tr>');
		cell1 = $('<td>');
		cell1.append(binfo['uuid']);
		cell2 = $('<td>');
		cell2.append(binfo['base-bottle']);
		cell3 = $('<td>');
		cell4 = $('<td>');
		cell4.append(setup_bottle_action_buttons(binfo['uuid']));
		row.append(cell1);
		row.append(cell2);
		row.append(cell3);
		row.append(cell4);
		body.append(row);
	}
}

function reload_base_bottles() {
	fetch_base_bottles(function(result) {
		update_base_bottles_table(result);
	});
}

function reload_bottles() {
	console.log("Reloading list of regular bottles");
	fetch_bottles(function(result) {
		update_bottles(result);
	});
}

$(document).ready(function() {
	reload_base_bottles();
	reload_bottles();
});