(function($) {
    $(function() {
        $.autoInline = function(options) {
            new AutoInline(options);
        }

        $.fn.getCheckboxData = function() {
            return {title: $(this).parent().text().trim(), value: $(this).val()}
        }

       
        function AutoInline(options) {
            $.extend(this, {
                requiredMask: 1,
                sModule: "#{0}_set-group".format(options.inlineName),
                sRow: "tr.form-row".format(options.inlineName),
                sEmptyRow: "#{0}_set-empty".format(options.inlineName),
                sCheckboxes: "fieldset .field-{0} li input[type=checkbox]"
            }, options);

            this.requiredMask = this.castBoolArray(this.requiredMask.toString(), true);
	    this.init();
        }

        AutoInline.prototype.castBoolArray = function(array, mask) {
            var result = [];
          
            $.each(array, function(i, elem) {
                result.push(Boolean(mask ? parseInt(elem) : elem));
            })
            return result
        }

        AutoInline.prototype.getCheckboxes = function(index) {
            return $(this.sCheckboxes.format(this.controllers[index]))
        }
        
        AutoInline.prototype.getRecords = function(checkbox, controller) {
            var self = this;
            var controllerIndex = this.controllers.indexOf(controller);

            var result = [[]];
            result[0].length = this.controllers.length;
            result[0][controllerIndex] = checkbox.getCheckboxData();
            
            $.each(this.controllers, function(i) {
                if (controllerIndex != i) {
                    var records = [];

                    $.each(self.getCheckboxes(i).filter(":checked"), function() {
                        var checkbox = $(this);

                        $.each(result, function(j, rec) {
                            var record = rec.slice();
                            record[i] = checkbox.getCheckboxData();
                            records[records.length] = record;
                        })
                    })
                    result.push.apply(result, records);
                }
            })
            return this.checkRecords(result);
        }
        
        AutoInline.prototype.checkRecords = function(records) {
            var self = this;
            var result = [];
            
            $.each(records, function(i, record) {
                var rightRecord = true;
                var boolArray = self.castBoolArray(record);

                $.each(boolArray, function(j, flag) {
                    if ((self.requiredMask[j]) && (!flag)) rightRecord = false;
                })
                
                if (rightRecord) {
                    $.each(record, function(k, elem) {
                        record[k] = elem == undefined ? {} : elem;
                    })
                    result.push(record);
                };
            })
            return result
        }

        AutoInline.prototype.getRowByRecord = function(record) {
            var self = this;
            var result = $();
            var rows = [];
            
            $.each(record, function(index, elem) {
                var value = elem.value || "";                  
                rows.push.apply(rows, $(
                        "{0} tr:not(.empty-form) .field-{1} input"
                        .format(self.sModule, self.fields[index]))
                    .filter(function() {return $(this).val() == value})
                    .parents(self.sRow))
            })
            
            var dict = {}
            var array = [];
            $.each(rows, function(_, row) {
                var index = array.indexOf(row);
                if (index >= 0) {
                    dict[index] += 1
                }
                else {
                    array.push(row);
                    dict[array.indexOf(row)] = 1
                }
            })
            for (index in dict) {
                if (dict[index] == record.length) result = $(array[index]);
            }
            return result;
        }

        AutoInline.prototype.addDynamicLines = function(records) {
            var self = this;

            $.each(records, function(_, record) {
                var row = self.getRowByRecord(record);
                if (row.length) {
		    row.removeClass("removed-row").show();
		}
		else {
		    $("{0} .add-row a".format(self.sModule)).trigger('click');
		    $.each(self.fields, function(index, fieldName) {
			var field = $("{0} {1}:not(.empty-form):last .field-{2}"
			    .format(self.sModule, self.sRow, fieldName));
			field.find("input").val(record[index].value);
			field.find("strong").text(record[index].title || self.empty);
		    })
		}
            })
        }
        
        AutoInline.prototype.removeDynamicLines = function(field, value) {
            var self = this;
            var inputs = $("{0} {1} .field-{2} input[value={3}]"
                .format(this.sModule, this.sRow, field, value))
            
            $.each(inputs, function() {
                var row = $(this).parents(self.sRow);
                
                if (row.hasClass("has_original")) {
                    row.find("td.delete input").attr("checked", "cheked");
                    row.addClass("removed-row").hide();
                }
                else {
                    row.find(".inline-deletelink").trigger("click");
                }
            })
        }

        AutoInline.prototype.createSkeleton = function() {           
            var self = this;
            
            $.each(self.fields, function () {
                var fieldName = this;
                
                var sCell = "{0} .field-{1}, {2} .field-{1}".format(
                    self.sEmptyRow, this, self.sModule)
    
                $.each($(sCell), function() {
                    $(this).find("a").remove();
                    $(this).find("input").detach().attr("type", "hidden").appendTo($(this));
                    $(this).append($("<strong/>"));
                })            
            })
            $("<div/>", {
                class: "{0}-warning auto-warning".format(this.inlineName),
                text: this.hint
            }).appendTo($(this.sModule)).hide();  
        }

        AutoInline.prototype.bindClicks = function() {
            var self = this;

            $.each(this.controllers, function(index, controller) {
                self.getCheckboxes(index).click(function() {
                    if ($(this).is(":checked")) {
                        var records = self.getRecords($(this), controller);
                        self.addDynamicLines(records);
                    }
                    else {
                        var value = $(this).val()
                        self.removeDynamicLines(self.fields[index], value);
                    }
                    self.checkInlineContent();
                })
            })            
        }
        
        AutoInline.prototype.checkInlineContent = function() {        
            var sWarning = "{0} .{1}-warning".format(this.sModule, this.inlineName);
            var sRows = "{0} .form-row:not(.empty-form, .removed-row)".format(this.sModule)
            var rowsExist = $(sRows).length > 0;
            var warningIsHidden = ! $(sWarning).is(":visible");
    
            // no checkboxes checked and warning was hidden
            if (!((rowsExist) && (warningIsHidden))) {
                $(this.sModule).find("table").toggle();
                $(this.sModule).find(".{0}-warning".format(this.inlineName)).toggle();
            }
        }

        AutoInline.prototype.acceptCSS = function() {
            var self = this;

            $(this.sModule).addClass("auto-module");
            $(this.sRow).addClass("auto-row");
            
            $.each(this.controllers, function() {
                $("fieldset .field-{0}".format(this.toString())).addClass("auto-controller");
            })

            $.each(this.fields, function() {
                $("{0} .field-{1}".format(self.sModule, this)).addClass("auto-field");  
            })
        }
        
        AutoInline.prototype.init = function() {
            var self = this;

            this.createSkeleton();
            this.bindClicks();
            this.checkInlineContent();
            this.acceptCSS();
            
            $("{0} tr:not(.empty-form) input".format(this.sModule))
                .filter(function() {return $(this).val() == ""})
                .parent().find("strong").text(this.empty);
        }
    })  
})(jQuery || django.jQuery);