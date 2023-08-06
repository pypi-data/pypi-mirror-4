jQuery = $ = jQuery || django.jQuery;

$(function() {
    $.fn.extend({       
        ajaxCallback: function(opts) {
            this.bind(opts.type, function() {
                var elem = $(this);
                var data = elem.is("select, input") ? {selected: elem.val()} : {}
                if (opts.dataFn) {
                    data = $.extend(data, $.proxy(opts.dataFn, elem)());
                }
                
                $.ajax($.extend({
                    url: opts.url,
                    type: 'POST',
                    dataType: 'json',
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                    },
                    data: $.extend(data, opts.data),
                    success: function(response) {
                        $.proxy(opts.success, elem)(response);
                    }
                }, opts.ajax))
            })
            $.each(this, function() {
                if ($(this).val()) {
                    $(this).trigger(opts.type);    
                }
            })
        },

        exist: function(yCallback, nCallback) {
            var len = this.length;
            if (len) {
                if (yCallback) {
                    $.each(this, function() {
                        $.proxy(yCallback, this)();
                    })
                }
            }
            else {
                if (nCallback) {
                    nCallback();
                }
            }
            return len ? true: false
        },

        leaveOptions: function(options, exclude, trigger) {
            $.each(this.find("option"), function() {
                inArray = $.inArray($(this).val(), options) >= 0
                if (exclude) {
                    inArray = !inArray;   
                }
                if (!inArray) {
                    $(this).attr("disabled", true);
                }
            })
            exclude ? this.val("eq") : this.val(options[0]);
            if (trigger) {
                this.trigger("change");
            }
        }
    })
})