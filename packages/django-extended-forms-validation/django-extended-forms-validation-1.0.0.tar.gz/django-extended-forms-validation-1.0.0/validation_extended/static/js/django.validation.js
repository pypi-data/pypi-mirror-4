(function($) {
    var callbacks = {
        other_field_equal_to: function(element, params) {
            return $("#id_" + params[0]).val() == params[1];
        }
    }

    $.fn.validateForm = function(options) {   
        var form = $(this);
        var rules = {};
        var messages = {};

        // to store fields data which does not exist on assignment
        form.data("validation_data", {})
        
        for (fieldname in options.rules) {
            rules[fieldname] = {}
            messages[fieldname] = {}
            form.data().validation_data[fieldname] = {}
    
            $.each(options.rules[fieldname], function() {
                var fieldSelector = "#id_" + fieldname;
                var rule = this.rule;
                
                form.data().validation_data[fieldname][rule] = {}
                if (rule == "remote") {
                    var validator_name = this.name;
                    
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
                                fields[i] = form.find("#id_" + val)
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
                                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                            },
                            data: $.extend({
                                __validator__: validator_name,
                                __field__: fieldname
                            }, data)
                        })
                        return true;
                    })
                    rules[fieldname][validator_name] = this.params ? this.params : true;
                }
                else {
                    var field = form.find(fieldSelector);
                    var rule_key = "rule_" + rule;
                    
                    rules[fieldname][rule] = this.params ? this.params : true;
                    if (field.length) field.data(rule_key, {})

                    if (this.msg) {
                        messages[fieldname][rule] = this.msg;
                        form.data().validation_data[fieldname][rule]["message"] = this.msg
                        if (field.length) field.data(rule_key).message = this.msg;
                    }
                    if (this.validator_data) {
                        form.data().validation_data[fieldname][rule]["data"] = this.validator_data
                        if (field.length) field.data(rule_key).data = this.validator_data;
                    }
                }
                
                // bind validate function to given events
                $(document).on(this.events, form.find(fieldSelector), function(event) {
                    if (form.find(fieldSelector).length) {
                        form.find(fieldSelector).valid();
                    }
                })
            })
        }
    
        form.validate($.extend({
            rules: rules,
            messages: messages,
            onkeyup: false,
            onfocusout: false,
            focusInvalid: true,
            focusCleanup: true
        }, options.settings));
        return this
    }
    
    $.fn.freezeForm = function(options) {
        var elems = $(this).find("input, select, textarea");
        elems.attr("disabled", true);
        this.data().frozen = true;
        return this
    }

    $.fn.unfreezeForm = function(options) {
        var elems = $(this).find("input, select, textarea");
        elems.attr("disabled", false);
        this.data().frozen = false;
        return this
    }
    
    $.fn.toggleFreeze = function(options) {
        this.data().frozen ? $(this).unfreezeForm() : $(this).freezeForm();
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
})(jQuery);
