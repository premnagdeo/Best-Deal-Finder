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
		// Create Results Title
		$(".results_div").append(
			$('<h2>').prop({
			id: 'results_title',
			innerHTML: 'Results:'
		})
	);

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
					dataType: 'json',
					success: function (response) {
						// console.log("RESPONSE: " + response);
						let checkbox_name = data_to_send['name'];
						products_data[checkbox_name] = response;
						if (Object.keys(response).length==0) {
							console.log(checkbox_name + " " + "came back empty");
						}
						else{
							success_function(checkbox_name, response);
						}

						// console.log("DEBUG");
						// console.log(checkbox_name);
						// console.log(products_data);
					},
					error: function (error) {
						console.log(error);
						let checkbox_name = data_to_send['name'];
						products_data[checkbox_name] = {};
						error_function(checkbox_name, response);
					},
					complete: function (data) {
						received_response_count++;
						console.log("Debug1" + received_response_count);
					}

				});


				function success_function(checkbox_name, curr_response){


					console.log("Yo success " + checkbox_name + " " + curr_response);
					create_product_title_div(checkbox_name);

					$.each(curr_response, function(k, v) {
						create_product_details_div(k, v);
			  	});


				}

				function error_function(checkbox_name, response){
					console.log("Yo error " + checkbox_name + " " +response);
				}

				function create_product_title_div(checkbox_name) {
					let website_dict = {
									    'amazon_checkbox': 'Amazon:',
									    'flipkart_checkbox': 'Flipkart:',
									    'mdcomputers_checkbox': 'MD Computers:',
									    'vedantcomputers_checkbox': 'Vedant Computers:',
									    'neweggindia_checkbox': 'Newegg India:',
									    'primeabgb_checkbox': 'Prime ABGB:'
										};
					let website_name = website_dict[checkbox_name];

					$('.results_div').append(
							$('<div>').prop(
								{
									innerHTML: website_name,
										className: 'results_product_title'
								}
							)
					);



				}

				function create_product_details_div(item_number, product_data) {
					// console.log("create_product_details_div" + count + " " + typeof(item_number) + " " + product_data + " " + typeof(product_data));
					item_number = parseInt(item_number, 10) + 1;
					$('.results_div').append(
							$('<div>').prop(
								{
									innerHTML: "Item " + item_number.toString() + ":",
										className: 'results_products_item_title'
								}
							)
					);

					/*
					$.each(product_data, function(k, v){
						$('.results_div').append(
								$('<div>').prop(
									{
										innerHTML: v,
										className: 'results_products_details'
									}
								)
						);
					});
					*/

					// Product Name
						$('.results_div').append(
								$('<div>').prop(
									{
										innerHTML: "Product Name: " + product_data['item_name'],
										className: 'results_products_details'
									}
								)
						);

						// Product Rating
							$('.results_div').append(
									$('<div>').prop(
										{
											innerHTML: "Product Rating: " + product_data['item_rating'],
											className: 'results_products_details'
										}
									)
							);

						// Product Price
							$('.results_div').append(
									$('<div>').prop(
										{
											innerHTML: "Product Price: " + product_data['item_price'],
											className: 'results_products_details'
										}
									)
							);


						// Product Link
						$('.results_div').append(
								$('<div>').prop(
									{
										innerHTML: "Product Link: " + product_data['item_link'],
										className: 'results_products_details'
									}
								)
						);

				}


			}

		}


	}

});
