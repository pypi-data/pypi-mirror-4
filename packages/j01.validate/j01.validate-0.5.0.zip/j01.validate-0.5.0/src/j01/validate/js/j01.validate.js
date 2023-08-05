//-----------------------------------------------------------------------------
// j01.validator
//-----------------------------------------------------------------------------
jQuery.fn.j01Validate = function(p) {
    p = jQuery.extend({
        url: null,
        methodName: 'j01Validate',
        callback: renderResponse,
        requestId: 'j01Validate'
    }, p);

    function renderResponse(response) {
    	var ele = $('#'+ response.id);
    	if (response.result == 'OK') {
    	    $(ele).removeClass('invalide');
    	    $(ele).addClass('validated');
    	    $(ele).parent().find('div.errors').remove();
    	} else {
        	$(ele).addClass('invalide');
        	$(ele).removeClass('validated');
        	$(ele).parent().find('div.errors').remove();
    	    $(ele).after('<div class="errors">'+ response.result +'</div>');
    	}
    }

    return this.each(function(){
        $(this).blur(function(){
        	var id = $(this).attr("id");
        	var value = $(this).val();
        	var proxy = getJSONRPCProxy(p.url);
        	proxy.addMethod(p.methodName, p.callback, p.requestId);
        	proxy[p.methodName](id, value);
        });

    });
};
