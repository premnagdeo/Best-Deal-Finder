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


		}),
		console.log(form_data);
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
    form_data.forEach(send_data);

      function send_data(item) {
        let query  = {search_query: search_query, search_count: search_count};
        let data_to_send = Object.assign(query, item);
        console.log("Sending " + JSON.stringify(data_to_send));

        $.ajax({
          url: '/data',
          type: 'POST',
          data: data_to_send,
          success:function (response) {
            console.log(response);
          },
          error: function (error) {
            console.log(error);
          }
        })



          }

    }






	}

});
