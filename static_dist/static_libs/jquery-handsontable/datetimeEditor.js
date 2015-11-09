(function (Handsontable) {
  var DateTimeEditor = Handsontable.editors.TextEditor.prototype.extend();

  DateTimeEditor.prototype.init = function () {
    Handsontable.editors.TextEditor.prototype.init.apply(this, arguments);
    this.isCellEdited = false;
    var that = this;
    this.instance.addHook('afterDestroy', function () {
      that.destroyElements();
    })
  };

  DateTimeEditor.prototype.createElements = function () {
    this.$body = $(document.body);
    this.TEXTAREA = document.createElement('INPUT');
    this.$textarea = $(this.TEXTAREA);

    Handsontable.Dom.addClass(this.TEXTAREA, 'handsontableInput');

    this.textareaStyle = this.TEXTAREA.style;
    this.textareaStyle.width = 0;
    this.textareaStyle.height = 0;

    this.TEXTAREA_PARENT = document.createElement('DIV');
    Handsontable.Dom.addClass(this.TEXTAREA_PARENT, 'handsontableInputHolder');

    this.textareaParentStyle = this.TEXTAREA_PARENT.style;
    this.textareaParentStyle.top = 0;
    this.textareaParentStyle.left = 0;
    this.textareaParentStyle.display = 'none';

    this.TEXTAREA.setAttribute('data-date-format', 'YYYY-MM-DD HH:mm');
    this.TEXTAREA_PARENT.appendChild(this.TEXTAREA);

    this.instance.rootElement[0].appendChild(this.TEXTAREA_PARENT);

    var that = this;
    Handsontable.hooks.add('afterRender', function () {
      that.instance._registerTimeout('refresh_editor_dimensions', function () {
        that.refreshDimensions();
      }, 0);
    });

    this.dateTimePicker = this.TEXTAREA_PARENT;
    Handsontable.Dom.addClass(this.dateTimePicker, 'input-group');
    Handsontable.Dom.addClass(this.dateTimePicker, 'date');
    this.datePickerStyle = this.dateTimePicker.style;
    this.datePickerStyle.position = 'absolute';
    this.datePickerStyle.top = 0;
    this.datePickerStyle.left = 0;
    this.datePickerStyle.zIndex = 199;
    this.Calendar = document.createElement('span');
    Handsontable.Dom.addClass(this.Calendar, 'input-group-addon');
    this.Calendar.style.position = 'relative';
    this.Calendar.style.width = 'inherit';
    this.Calendar.innerHTML = '<span class="glyphicon glyphicon-calendar"></span>';

    this.dateTimePicker.appendChild(this.Calendar);
    document.body.appendChild(this.dateTimePicker);
    this.$datePicker = $(this.dateTimePicker);


    this.$datePicker.datetimepicker({
        language: document.getElementsByTagName("html")[0].getAttribute("lang")
    }).change(function(e){
        var input = $(e.target).find('input');
        var val = input.val();
        that.setValue(val);
    });

    /**
     * Prevent recognizing clicking on jQuery Datepicker as clicking outside of table
     */
    this.$datePicker.on('mousedown', function (event) {
      event.stopPropagation();
    });

    this.hideDatepicker();
  };

  DateTimeEditor.prototype.destroyElements = function () {
    this.$datePicker.datetimepicker('destroy');
    this.$datePicker.remove();
  };

  DateTimeEditor.prototype.open = function () {
    Handsontable.editors.TextEditor.prototype.open.call(this);
    this.showDatepicker();
  };

  DateTimeEditor.prototype.finishEditing = function (isCancelled, ctrlDown) {
    this.hideDatepicker();
    Handsontable.editors.TextEditor.prototype.finishEditing.apply(this, arguments);
  };

  DateTimeEditor.prototype.showDatepicker = function () {
    var $td = $(this.TD);
    var offset = $td.offset();
    this.datePickerStyle.top = (offset.top ) + 'px';
    this.datePickerStyle.left = offset.left + 'px';
    this.datePickerStyle.width = this.dateTimePicker.style.width;

    var dateOptions = {
      defaultDate: this.originalValue || void 0
    };
    $.extend(dateOptions, this.cellProperties);
    this.$datePicker.datetimepicker("option", dateOptions);
    if (this.originalValue) {
      this.$datePicker.datetimepicker("setDate", this.originalValue);
    }
    this.datePickerStyle.display = 'table';
  };

  DateTimeEditor.prototype.hideDatepicker = function () {
    this.datePickerStyle.display = 'none';
  };


  Handsontable.editors.DateTimeEditor = DateTimeEditor;
  Handsontable.editors.registerEditor('datetime', DateTimeEditor);
})(Handsontable);
