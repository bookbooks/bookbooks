$(function(){
	var existedTags = $('#tags').val();
	$('#save-review').on('click', function(event){
		var status = $('#status').val();
		var bid = $('#bid').val();
		var rating = $('#rating').val();
		var review = $('#review').val();
		var tags = $('#tags').val();
		$.ajax({
			url: '/submit_review',
			method: 'POST',
			contentType: 'application/json;charset=UTF-8',
			data: JSON.stringify({
				bid: bid,
				rating: rating,
				review: review,
				tags: tags,
				status: status
			})
		}).done(function(){
			document.location.reload(true);
		}).fail(function(jqXHR, textStatus, errorThrown){
			console.log(textStatus);
			console.log(errorThrown);
		});;
	})
});