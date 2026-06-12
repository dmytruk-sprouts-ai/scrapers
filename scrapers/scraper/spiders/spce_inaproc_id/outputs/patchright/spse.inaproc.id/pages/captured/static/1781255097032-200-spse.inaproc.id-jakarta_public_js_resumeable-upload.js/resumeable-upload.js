
var notSupportedMsg = "<b>Warning!</b> Your browser does not seem to support the features necessary to run tus-js-client. The buttons below may work but probably will fail silently.";
$(document).on('change', '.resumable-input', function(e) {
	var upload = null
	var inputFile = $(e.currentTarget);
	var file = e.target.files[0];
	var alertBox = $("#"+inputFile.data('alert'));
	
	// check if supported by browser
	if (!tus.isSupported) {
		alertBox.attr('class', 'alert alert-danger').html(notSupportedMsg);
	}

	
	var progressDiv = "#"+inputFile.data('progress');
	var progressBar = $(progressDiv + " .progress-bar");
	var endpoint = inputFile.data('url');
	var chunkSize = 1024*500; // 500 kB chunk size
	
	console.log("selected file", file);
	console.log("targ", inputFile.data('url'));
	$(progressDiv).show();

	var options = {
		endpoint: endpoint,
		resume: true,
		chunkSize: chunkSize,
		metadata: {
	        filename: file.name
	    },
	    onError: function(error) {
	    	reset(inputFile, alertBox);
	    	//alert("Failed because: " + error);
	    	alertBox.attr('class', 'alert alert-danger').html("Failed because: " + error);
	    },
	    onProgress: function(bytesUploaded, bytesTotal) {
	      var percentage = (bytesUploaded / bytesTotal * 100).toFixed(2);
	      progressBar.css('width', percentage + '%');
	      console.log(bytesUploaded, bytesTotal, percentage + "%");
	    },
	    onSuccess: function() {
	      reset(inputFile, alertBox);
	      var result = $.parseJSON(upload._xhr.response);
	      $.each(result.files, function (index, file) {
				var content = '<a href="'+file.download_url+'"><i class="glyphicon glyphicon-download"></i> '+file.name+'</a> - '+file.size+' ('+file.upload_date+')';
              $('<li/>').addClass('list-group-item').html(content).appendTo('#files');
          });
          $('#progress').hide();
	    }
	  }

	  upload = new tus.Upload(file, options);
	  upload.start();
})
$(document).on('change', '.resumable-input-tesapendo', function(e) {
	var upload = null
	var inputFile = $(e.currentTarget);
	var file = e.target.files[0];
	var alertBox = $("#"+inputFile.data('alert'));
	
	// check if supported by browser
	if (!tus.isSupported) {
		alertBox.attr('class', 'alert alert-danger').html(notSupportedMsg);
	}

	
	var progressDiv = "#"+inputFile.data('progress');
	var progressBar = $(progressDiv + " .progress-bar");
	var endpoint = inputFile.data('url');
	var endpointCommit = inputFile.data('url-commit');
	var access_token = inputFile.data('access-token');
	var chunkSize = 1024*500; // 500 kB chunk size
	
	console.log("selected file", file);
	console.log("targ", inputFile.data('url'));
	$(progressDiv).show();

	var options = {
		endpoint: endpoint,
		resume: true,
		chunkSize: chunkSize,
		metadata: {
	        filename: file.name
	    },
	    headers: {
	    	access_token: access_token
	    },
	    onError: function(error) {
	    	reset(inputFile, alertBox);
	    	//alert("Failed because: " + error);
	    	alertBox.attr('class', 'alert alert-danger').html("Failed because: " + error);
	    },
	    onProgress: function(bytesUploaded, bytesTotal) {
	      var percentage = (bytesUploaded / bytesTotal * 100).toFixed(2);
	      progressBar.css('width', percentage + '%');
	      console.log(bytesUploaded, bytesTotal, percentage + "%");
	    },
	    onSuccess: function() {
	      reset(inputFile, alertBox);
	      var result = $.parseJSON(upload._xhr.response);
	      $.ajax({
	    	  method: "POST",
	    	  url: endpointCommit,
	    	  data: { uuid: result.uuid, berlaku:30, surat:"tes", hash:'e4696a6fc384c45f4ee1bf85fc231806', access_token:access_token }
	      })
	      	.done(function( msg ) {
	      		alert( "Data Saved: " + msg );
	      	});
          $('#progress').hide();
	    }
	  }

	  upload = new tus.Upload(file, options);
	  upload.start();
})

function reset(inputFile, alertBox) {
	alertBox.attr('class', '');
	inputFile.value = ""
}
