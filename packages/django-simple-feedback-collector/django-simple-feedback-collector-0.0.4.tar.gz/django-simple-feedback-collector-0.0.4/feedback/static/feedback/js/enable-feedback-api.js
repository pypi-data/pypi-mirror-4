apply_feedback_api= function(handler_root, callback){
$(function(){
    $('form[data-feedback-campaign]').submit(function(){
        form = $(this);
        campaign= form.data('feedback-campaign');
        destination= handler_root + campaign+"/api/";
        formdata = form.serializeArray();
        $.ajax({url:destination,
                type:'POST', data: formdata, success: function(result){
                    callback(form);
    }});  
    return false;
    
});
});
};
