$(document).ready(function () {
	$("#search_button").on("click", function (e) {
		e.preventDefault();
		get_data();
	});

	$("#search_bar").keypress(function (e) {
		var key = e.which;
		if (key == 13) // user presses the enter key code in the search bar
		{
			e.preventDefault();
			get_data();
			$('input[name = butAssignProd]').click();
			return false;
		}
	});

	function get_data() {
		// Create Results Title after keypress
		$(".results_div").html(
			$('<h2>').prop({
				id: 'results_title',
				innerHTML: 'Results:'
			})
		);
		// Check connection with flask server
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

		var search_query = form_data[0]['value'];
		var search_count = form_data[1]['value'];


		// remove first two elements from array which are search_query and search_count
		var removed = form_data.splice(0, 2);

		// if items remain -> those are websites to query
		if (form_data.length > 0) {
			var products_data = new Object();
			var received_response_count = 0;

			// Send all ajax requests
			$.when(form_data.forEach(send_data)).then(function () {
				console.log("All complete");
				console.log(products_data);
			});


			var csvrows = [];
			create_csv(products_data);



			function send_data(item) {
				let query = {
					search_query: search_query,
					search_count: search_count
				};
				let data_to_send = Object.assign(query, item);

				$.ajax({
					url: '/data',
					type: 'POST',
					data: data_to_send,
					dataType: 'json',
					success: function (response) {

						// Check if empty object received from server
						let checkbox_name = data_to_send['name'];
						products_data[checkbox_name] = response;
						if (Object.keys(response).length == 0) {

							no_results_error_function(checkbox_name, response);
						}
						else {
							success_function(checkbox_name, response);
						}

					},
					error: function (error) {
						let checkbox_name = data_to_send['name'];
						products_data[checkbox_name] = {};
						server_error_function(checkbox_name, response);
					},
					complete: function (data) {
						received_response_count++;
					}

				});


				function success_function(checkbox_name, curr_response) {


					create_product_title_div(checkbox_name);

					$.each(curr_response, function (k, v) {
						create_product_details_div(k, v, checkbox_name);
					});


				}

				function no_results_error_function(curr_checkbox_name, curr_response) {
					create_product_title_div(curr_checkbox_name);
					let parent = '#' + curr_checkbox_name + '_result';

					$(parent).append(
						$('<h2>').prop({

							innerHTML: "No products were found.",
							className: 'error_text'
						})
					);


				}


				function server_error_function(curr_checkbox_name, curr_response) {

					create_product_title_div(curr_checkbox_name);
					let parent = '#' + curr_checkbox_name + '_result';

					$(parent).append(
						$('<h2>').prop({
							innerHTML: "Server Error while fetching results.",
							className: 'error_text'
						})
					);


				}

				function create_product_title_div(checkbox_name) {

					let website_dict = {
						'amazon_checkbox': 'Amazon:',
						'flipkart_checkbox': 'Flipkart:',
						'mdcomputers_checkbox': 'MD Computers:',
						'theitdepot_checkbox': 'The IT Depot:',
						'neweggindia_checkbox': 'Newegg India:',
						'primeabgb_checkbox': 'Prime ABGB:'
					};
					let website_name = website_dict[checkbox_name];

					$('.results_div').append(
						$('<div>').prop({
							id: checkbox_name + '_result',
							innerHTML: website_name,
							className: 'results_product_title'

						})
					);



				}

				function create_product_details_div(item_number, product_data, curr_checkbox_name) {
					item_number = parseInt(item_number, 10) + 1;
					let parent = '#' + curr_checkbox_name + '_result';


					$(parent).append(
						$('<div>').prop({
							innerHTML: "Item " + item_number.toString() + ":",
							className: 'results_products_item_title'
						})
					);


					// Product Name
					$(parent).append(
						$('<div>').prop({
							innerHTML: "Product Name: " + product_data['item_name'],
							className: 'results_products_details'
						})
					);

					// Product Rating
					$(parent).append(
						$('<div>').prop({
							innerHTML: "Product Rating: " + product_data['item_rating'],
							className: 'results_products_details'
						})
					);

					// Product Price
					let text = "Product Price: "
					if (product_data['item_price'] != "Unavailable") {
						text += "₹"
					}

					$(parent).append(
						$('<div>').prop({
							innerHTML: text + product_data['item_price'],
							className: 'results_products_details'
						})
					);


					// Product Link
					$(parent).append(
						$('<a>').prop({
							innerHTML: "Product Link: " + product_data['item_link'],
							href: product_data['item_link'],
							className: 'results_products_details'
						})
					);

					let row = [[curr_checkbox_name], [item_number.toString()], product_data['item_name'], product_data['item_rating'], product_data['item_price'], product_data['item_link']];
					csvrows.push(row.join(","));

				}

			}

				function create_csv(products_data){
					let csvheaders = [["Website"],	["Item Number"],	["Product Name"],	["Product Rating"],	["Product Price"],	["Product Link"]];
					csvrows.push(csvheaders.join(","));


				  $('.csv_div').append(
				    $('<input>').prop({
							type: "button",
							value: "Download CSV",
				      id: "csv_download_button",
				      className: 'download_button'
				    })
				  );


					$("#csv_download_button").on("click", function (e) {
						console.log("DOWNLOAD FUNCTION ACTIVATED");
						console.log(csvrows);
						var csvstring = csvrows.join("%0A");
						console.log(csvstring);
						var a=document.createElement('a');
						a.href = 'data:attachment/csv,' + csvstring;
						a.target = '_blank';
						a.download = 'myFile.csv';
						document.body.appendChild(a);
						a.click();
					});


				}



		}


	}

});
