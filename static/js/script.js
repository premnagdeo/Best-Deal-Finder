$(document).ready(function () {
	// console.log("DEBUG script called");
	$("#search_button").on("click", function (e) {
		e.preventDefault();
		// console.log("DEBUG button click");
		get_data();
	});

	$("#search_bar").keypress(function (e) {
		var key = e.which;
		if (key == 13) // the enter key code
		{
			e.preventDefault();
			// console.log("DEBUG enter pressed");
			get_data();
			$('input[name = butAssignProd]').click();
			return false;
		}
	});

	function get_data() {
		// console.log("DEBUG get_data function called");
		var form_data = $('form').serializeArray();
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
		// console.log(form_data);
		/* Working Send entire data
    $.ajax({
      url: '/data',
      type: 'POST',
      data: form_data,
      success:function (response) {
				console.log(response);
			},
			error: function (error) {
				console.log(error);
			}
    })

      */

		// Send data one by one

		var search_query = form_data[0]['value'];
		var search_count = form_data[1]['value'];


		// remove first two elements from array which are search_query and search_count
		var removed = form_data.splice(0, 2);

		// if items remain -> those are websites to query
		if (form_data.length > 0) {
			var products_data = new Object();
			var received_response_count = 0;
			// send request for each website selected
			form_data.forEach(send_data)

			// Wait for all ajax to complete
			console.log("LEN " + form_data.length);
			console.log("waiting");
			//   $.when(received_response_count == form_data.length).then(function(){
			//   console.log("All complete");
			//   console.log(products_data);
			//
			// });

			// TODO figure out how to make ajax wait for all replies
      // TODO maybe try to call a function on success of ajax to create the divs dynamically
			$.when(form_data.forEach(send_data)).then(function () {
				console.log("All complete");
				console.log(products_data);

			});


			function send_data(item) {
				let query = {
					search_query: search_query,
					search_count: search_count
				};
				let data_to_send = Object.assign(query, item);
				// console.log("Sending " + JSON.stringify(data_to_send));

				$.ajax({
					url: '/data',
					type: 'POST',
					data: data_to_send,
					success: function (response) {
						// console.log("RESPONSE: " + response);
						let checkbox_name = data_to_send['name'];
						products_data[checkbox_name] = response;
						// console.log("DEBUG");
						// console.log(checkbox_name);
						// console.log(products_data);
					},
					error: function (error) {
						console.log(error);
						let checkbox_name = data_to_send['name'];
						products_data[checkbox_name] = {};
					},
					complete: function (data) {
						received_response_count++;
						console.log("Debug1" + received_response_count);
					}

				});


			}

		}


	}

});
