$(function() {
	var url = window.location.href;
	var a = url.split('/');
	var bid = a[a.length - 1];

	$('#reading-btn').on('click', function(event) {
		BootstrapDialog.show({
			title: 'Review',
			message: $('<div></div>').load('/reading_rating/' + bid)
		});
	});

	$('#read-btn').on('click', function(event) {
		BootstrapDialog.show({
			title: 'Review',
			message: $('<div></div>').load('/read_rating/' + bid)
		});
	});
});