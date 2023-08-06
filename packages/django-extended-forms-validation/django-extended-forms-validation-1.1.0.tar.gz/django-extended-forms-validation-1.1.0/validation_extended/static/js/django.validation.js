(function($) {
    $.fn.validateForm = function(options) {   
        var form = $(this);
        var rules = {};
        var messages = {};
	var bindedEvents = {};

	function parseParams(params) {
	    function injectFormSelector(param) {
		return param.replace("_formSelector", options.formSelector)
	    }

	    if (params) {
		if (typeof params == "string") return injectFormSelector(params)
		$.each(params, function(i, val) {
		    params[i] = injectFormSelector(val);
		})
		return params
	    }
	    return true
	}

        // to store fields data which does not exist on assignment
        form.data("validation_data", {})

	// turn strings to functions
	$.each(options.settings, function(key, val) {
	    if (val.toString().indexOf("fn:") == 0) {
		var fnPath = val.substring(3).split(".");
		var fn = window;
		var proxyObj = fn[fnPath[0]];

		while (fnPath.length) {
		    fn = fn[fnPath[0]];
		    fnPath.shift();   
		}
		options.settings[key] = $.proxy(fn, proxyObj);
	    }
	})
	
	// set csrf getting function
	if (!options.settings.csrf) {
	    options.settings.csrf = function() {return $.cookie('csrftoken')}
	}
	
        for (fieldname in options.rules) {
	    var alias = fieldname;
	    if ((options.settings.aliases) && (options.settings.aliases[fieldname])) {
		alias = options.settings.aliases[fieldname]
	    }

            rules[alias] = {}
            messages[alias] = {}
            form.data().validation_data[alias] = {}
    
            $.each(options.rules[fieldname], function() {
                var fieldSelector = "#id_" + alias;
                var rule = this.rule;
                
                form.data().validation_data[alias][rule] = {}
                if (rule == "remote") {
                    var validator_name = this.name;
		    var pyform = this.py_form_cls;
                    
                    // define new method for remote validation
                    $.validator.addMethod(validator_name, function(val, el, params) {
                        var validator = this;
                        var fieldname = $(el).attr("name");
                        
                        var data = {}
                        var fields = [];
                                                
                        // save last invalid message which will be shown if value will not modified
                        var previous = validator.previousValue(el);
                        if (previous.message) {
                            validator.settings.messages[el.name][validator_name] = previous.message;
                        }

                        // get fields as jQuery objects
                        if (params == "*") {
                            fields = form.find("input, select, textarea")
                        }
                        else {
                            if (params == true) params = [fieldname];
                            $.each(params, function(i, val) {
				var field = form.find("#id_" + val);
				if (!field.length) field = form.find("input[name=" + val + "]");
                                fields[i] = field;
                            })
                        }
                        
                        // gather data
                        $.each(fields, function() {
                            data[$(this).attr("name")] = $(this).val();
                        })
                       
                        $.validator.methods.remote.call(this, val, el, {
                            type: "POST",
                            url: "/validation/validate",
                            beforeSend: function(xhr, settings) {
                                xhr.setRequestHeader("X-CSRFToken", options.settings.csrf());
                            },
                            data: $.extend({
                                _validator: validator_name,
                                _field: fieldname,
				_form: pyform
                            }, data)
                        })
			$(el).removeData("previousValue");
			return true
                    })
                    rules[alias][validator_name] = parseParams(this.params);
                }
                else {
                    var field = form.find(fieldSelector);
                    var rule_key = "rule_" + rule;
                    
                    rules[alias][rule] = parseParams(this.params);
                    if (field.length) field.data(rule_key, {})

                    if (this.msg) {
                        messages[alias][rule] = this.msg;
                        form.data().validation_data[alias][rule]["message"] = this.msg
                        if (field.length) field.data(rule_key).message = this.msg;
                    }
                    if (this.validator_data) {
                        form.data().validation_data[alias][rule]["data"] = this.validator_data
                        if (field.length) field.data(rule_key).data = this.validator_data;
                    }
                }
                
                // bind validate function to given events
		var selector = options.formSelector + " " + fieldSelector;
		var events = typeof this.events == "string" ? this.events.split(" ") : this.events;

		$.each(events, function(i, event) {
		    // group events to prevent multiple handling
		    if (!bindedEvents[selector]) bindedEvents[selector] = {}
		    if (!bindedEvents[selector][event]) {
			$(document).on(event, selector, function() {
			    $(selector).valid();
			})
			bindedEvents[selector][event] = true;
		    }
		})
            })
        }

	// validate form
        form.validate($.extend({
            rules: rules,
            messages: messages,
            onkeyup: false,
            onfocusout: false,
            focusInvalid: true,
            focusCleanup: true,
        }, options.settings));
	form.removeAttr("novalidate");
        return this
    }
    
    $.validator.addMethod("regex", function(value, element, params) {
        if (!value) return true;
        var pattern, modes = "";
        
        if (typeof(params) == "string") {
            pattern = params
        }
        else {
            pattern = params[0]
            modes = params[1]
        }
        var regexp = new RegExp(pattern, modes)
        return regexp.test(value);
    })
    
    $.validator.addMethod("empty", function() {
	return true;
    })
})(jQuery);
