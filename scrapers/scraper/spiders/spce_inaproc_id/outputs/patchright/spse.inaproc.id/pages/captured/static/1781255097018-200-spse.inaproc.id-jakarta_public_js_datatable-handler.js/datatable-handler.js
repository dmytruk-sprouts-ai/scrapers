/**
 * Generic error handler for DataTables AJAX requests
 * @param {string} tableId - The ID of the DataTable (without # prefix)
 * @param {object} xhr - XHR object from error callback
 * @param {string} error - Error type
 * @param {string} thrown - Error message
 * @param {string} [customMessage] - Optional custom error message
 */
function handleDataTableError(tableId, xhr, error, thrown, customMessage) {
    // Hide the processing indicator
    $('#' + tableId + '_processing').hide();
  
    var errorMessageId = tableId + '-error-message';
    var message;
    
    // Use custom message if provided
    if(customMessage !== undefined) {
      message = customMessage;
    } else {
      // Detect error type and set appropriate message
      if (error === "timeout" || xhr.status === 408) {
        message = MESSAGES.DATATABLE.TIMEOUT;
      } else if (xhr.status >= 500) {
        message = MESSAGES.DATATABLE.SERVER_ERROR;
      } else if (xhr.status === 403) {
        message = MESSAGES.DATATABLE.FORBIDDEN;
      } else if (xhr.status === 401) {
        message = MESSAGES.DATATABLE.UNAUTHORIZED;
      } else if (xhr.status === 0 && error === "error") {
        message = MESSAGES.DATATABLE.NETWORK_ERROR;
      } else {
        message = MESSAGES.DATATABLE.DEFAULT;
      }
    }
  
    // Create or show error message container
    if ($('#' + errorMessageId).length === 0) {
      $('#' + tableId).before(
        '<div id="' + errorMessageId + '" class="alert alert-danger alert-dismissible fade show" role="alert">' +
        message +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span></button></div>'
      );
    } else {
      $('#' + errorMessageId).html(message + 
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span></button>');
      $('#' + errorMessageId).show();
    }
    
    // Log detailed error information (only enable for debugging)
    // console.error("DataTables error:", error, thrown, xhr.status, xhr.responseText);
  }