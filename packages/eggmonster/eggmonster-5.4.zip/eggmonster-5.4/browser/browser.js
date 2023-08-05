// override Array.groupBy with a method for grouping by function
Array.prototype.groupBy = function(key_func) {
	var res = {};
	this.forEach(function(x) {
		var k = key_func(x);
		var v = res[k];
		if (!v) v = res[k] = [];
		v.push(x);
	});
	return res;
};

function set_revisions(data, textStatus, jqXHR) {
	// sort by number
	data.sort(function(a,b){return a.number - b.number;});
	// group by revision date
	var revision_date = function(rev) {return rev.datetime.date;}
	$.each(data.groupBy(revision_date), function(date, revs) {
		var list = $('<ul>').text(date).appendTo('#revisions');
		$.each(revs, function(key, rev) {
		var number = rev['number'];
			if(number < 2) return;
			text = number;
			$('<li>').text(text)
				.click(function(){$("#revisions li").css("background-color", "white"); $(this).css("background-color", "green"); diff_rev(number);})
				.appendTo(list);
		});
	});
}

function load_revisions() {
	$("#revisions").hide();
	var server = $('input').val();
	if(!server) return;
	var loc = 'http://'+server+'/config_files?callback=?';
	$.getJSON(loc, set_revisions)
		.error(function(jqXHR, textStatus, thrownError){
			alert("error loading revisions");
		});
	$("#revisions").show();
	$("#revisions ul").remove();
	$("#differences").hide();
}

function diff_rev(revision) {
	// for now, just load the contents to be viewed
	var server = $('input').val();
	$("#viewer").empty();
	if(!server || revision < 2) return;
	var loc_1 = 'http://'+server+'/config?revision='+revision+'&callback=?';
	var loc_0 = 'http://'+server+'/config?revision='+(revision-1)+'&callback=?';
	var error_callback = function() { alert("error loading config"); };
	$.getJSON(loc_0, function(data) {
		var orig_config = data[1];
		$.getJSON(loc_1, function(data) {
			var new_config = data[1];
			var diff = WDiffString(orig_config, new_config);
			diff = diff.replace(/<br>/g, '<br/>').replace(/&nbsp;/g, '&#160;');
			$(diff).appendTo("#viewer");
			$("#differences").show();
		}).error(error_callback);
	}).error(error_callback);
}

$(document).ready(function() {
	$('input').bind("keypress", function(e) {
		if(e.which != 13) return true;
		$('input').blur();
		return false;
	});
	$('input').focus();
	$('input').blur(load_revisions);
});
