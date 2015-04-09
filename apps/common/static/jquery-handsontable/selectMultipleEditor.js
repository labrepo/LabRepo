(function (Handsontable) {

  Handsontable.editors.BaseEditor.prototype.getColumnNumber = function(){
    var n_cols = this.instance.countCols(),
        i = 1,
        title = $("#dataTable").data('title'),
        inst = this.instance.getColHeader(this.col).split('<')[0].trim().toLowerCase(),
        name = (Object.keys(title).filter(function(item) {
            return title[item].toLowerCase() === inst
        })[0] + '_pk').toLowerCase();

    for (i=1; i<=n_cols; i++){
        if (typeof this.instance.getColHeader(i) !== 'undefined' && name == this.instance.getColHeader(i).toLowerCase()) {
            return i;
        }
    }
    return 0;
  };

  var SelectMultiplEditor = Handsontable.editors.SelectEditor.prototype.extend();

  SelectMultiplEditor.prototype.init = function(){
    this.select = document.createElement('SELECT');
    this.select.setAttribute('multiple', 'multiple');
    Handsontable.Dom.addClass(this.select, 'htSelectEditor');
    Handsontable.Dom.addClass(this.select, 'select2');
    this.select.style.display = 'none';
    this.instance.rootElement[0].appendChild(this.select);
  };

  SelectMultiplEditor.prototype.prepareOptions = function(optionsToPrepare){

    var preparedOptions = {};

    if (Handsontable.helper.isArray(optionsToPrepare)){
      for(var i = 0, len = optionsToPrepare.length; i < len; i++){
        preparedOptions[optionsToPrepare[i][0]] = optionsToPrepare[i][1];
      }
    }
    else if (typeof optionsToPrepare == 'object') {
      preparedOptions = optionsToPrepare;
    }

    return preparedOptions;

  };

  SelectMultiplEditor.prototype.getValue = function () {
    var value = [].map.call(this.select.selectedOptions, function(option) {
      return option.value;
    });
    this.instance.setDataAtCell(this.row, this.getColumnNumber(), value);

    return [].map.call(this.select.selectedOptions, function(option) {
      return option.text;
    });
  };

  SelectMultiplEditor.prototype.setValue = function (value) {
    var select = $(this.select);
    $.each(value.split(","), function(i,e){
        select.find("option[value='" + e + "']").prop("selected", true);
    });
  };

  var onBeforeKeyDown = function (event) {
    var instance = this;
    var editor = instance.getActiveEditor();

    switch (event.keyCode){
      case Handsontable.helper.keyCode.ARROW_UP:

        var previousOption = editor.select.find('option:selected').prev();

        if (previousOption.length == 1){
          previousOption.prop('selected', true);
        }

        event.stopImmediatePropagation();
        event.preventDefault();
        break;

      case Handsontable.helper.keyCode.ARROW_DOWN:

        var nextOption = editor.select.find('option:selected').next();

        if (nextOption.length == 1){
          nextOption.prop('selected', true);
        }

        event.stopImmediatePropagation();
        event.preventDefault();
        break;
    }
  };

  SelectMultiplEditor.prototype.open = function () {
    var width = Handsontable.Dom.outerWidth(this.TD); //important - group layout reads together for better performance
    var height = Handsontable.Dom.outerHeight(this.TD);
    var rootOffset = Handsontable.Dom.offset(this.instance.rootElement[0]);
    var tdOffset = Handsontable.Dom.offset(this.TD);

//    this.select.style.height = height +  + 10 + 'px';
    this.select.style.minWidth = width + 'px';
    this.select.style.top = tdOffset.top - rootOffset.top + 'px';
    this.select.style.left = tdOffset.left - rootOffset.left - 2 + 'px'; //2 is cell border
    this.select.style.display = '';
    this.instance.addHook('beforeKeyDown', onBeforeKeyDown);

    $(this.select).focus().select2();
  };

  SelectMultiplEditor.prototype.close = function () {
    $(this.select).select2("destroy");
    this.select.style.display = 'none';
    this.instance.removeHook('beforeKeyDown', onBeforeKeyDown);
  };

  SelectMultiplEditor.prototype.focus = function () {
    this.select.focus();
  };

  Handsontable.editors.SelectMultiplEditor = SelectMultiplEditor;
  Handsontable.editors.registerEditor('multi-select', SelectMultiplEditor);

})(Handsontable);
