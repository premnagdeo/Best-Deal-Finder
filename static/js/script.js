$(document).ready(function () {
	console.log("DEBUG script called");
	$("#search_button").on("click", function (e) {
		e.preventDefault();
		console.log("DEBUG button click");
		get_data();
	});

	$("#search_bar").keypress(function (e) {
		var key = e.which;
		if (key == 13) // the enter key code
		{
			e.preventDefault();
			console.log("DEBUG enter pressed");
			get_data();
			$('input[name = butAssignProd]').click();
			return false;
		}
	});

	function get_data() {
		console.log("DEBUG get_data function called");
		var data = $('form').serializeArray();
		console.log(data);
		$.ajax({
			url: '/check_connection',
			type: 'POST',
			success: function (response) {
				console.log(response);
			},
			error: function (error) {
				console.log(error);
			}


		});

	}

});
