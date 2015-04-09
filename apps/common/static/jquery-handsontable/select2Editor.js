(function (Handsontable) {

  var Select2Editor = Handsontable.editors.SelectEditor.prototype.extend();

  Select2Editor.prototype.init = function(){
    Handsontable.editors.SelectEditor.prototype.init.apply(this, arguments);
    Handsontable.Dom.addClass(this.select, 'select2');
  };

  Select2Editor.prototype.prepareOptions = function(optionsToPrepare){

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

  Select2Editor.prototype.open = function () {
    Handsontable.editors.SelectEditor.prototype.open.apply(this, arguments);
    $(this.select).focus().select2();
  };

  Select2Editor.prototype.close = function () {
      $(this.select).select2("destroy");
      Handsontable.editors.SelectEditor.prototype.close.apply(this, arguments);
  };

  Select2Editor.prototype.getValue = function () {
      this.instance.setDataAtCell(this.row, this.getColumnNumber(), this.select.value);
      if (this.select.selectedIndex >= 0){
          return this.select.options[this.select.selectedIndex].text;
      }
      return '';
  };

  Handsontable.editors.Select2Editor = Select2Editor;
  Handsontable.editors.registerEditor('select2', Select2Editor);

})(Handsontable);
