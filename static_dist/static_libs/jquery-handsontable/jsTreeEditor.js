(function (Handsontable) {
  var JsTreeEditor = Handsontable.editors.HandsontableEditor.prototype.extend();

  JsTreeEditor.prototype.init = function () {
    Handsontable.editors.HandsontableEditor.prototype.init.apply(this, arguments);
    this.div = document.createElement('DIV');
    Handsontable.Dom.addClass(this.div, 'jstree');
    this.div.style.display = 'none';
    this.div.style['background-color'] = 'white';
    this.div.style.with = this.TEXTAREA.style.with;
    $(this.TEXTAREA).after(this.div);
    $(this.TEXTAREA).attr('placeholder', 'Search');

    this.tree = $(this.div).jstree({
        'core' : {
            'animation': 0,
            'check_callback': true,
            'themes': { 'stripes': true },
            'data': []
        },
        'search' : {
            show_only_matches: true
        },
        'plugins' : [
            'search', 'checkbox'
        ]
    });
    this.tree.focus();
    var that = this;
    var to = false;
    $(this.TEXTAREA).keyup(function () {
        if(to) { clearTimeout(to); }
        to = setTimeout(function () {
            var v = that.$textarea.val();
            that.tree.jstree(true).search(v);
        }, 250);
    });
  };


JsTreeEditor.prototype.prepare = function(){
    Handsontable.editors.HandsontableEditor.prototype.prepare.apply(this, arguments);
    this.tree.jstree(true).settings.core.data = this.cellProperties.selectOptions;
    this.tree.jstree(true).refresh();
};

  JsTreeEditor.prototype.open = function () {
      Handsontable.editors.HandsontableEditor.prototype.open.apply(this, arguments);
      this.TEXTAREA.style.visibility = 'visible';
      this.focus();
      var tableContainer = $(this.instance.table).parents('div.handsontable');
      tableContainer.css('height', tableContainer.height() + this.tree.height());
      this.div.style.display = 'block';
  };

  JsTreeEditor.prototype.setValue = function (value) {
    var tree = this.tree;
    value = this.instance.getDataAtCell(this.row, this.getColumnNumber());
    tree.jstree('deselect_all');
    $.each(value, function(i, e){
        tree.jstree('select_node', e);
    });
  };

  JsTreeEditor.prototype.getValue = function () {
    var that = this, node;
    that.instance.setDataAtCell(that.row, that.getColumnNumber(), that.tree.jstree('get_selected'));
    var tags_data =  JSON.stringify([].map.call(that.tree.jstree('get_selected'), function(option) {
        node = that.tree.jstree('get_node', option);
        return {text: node.text, color: node.li_attr.background_color};
    }));
    that.instance.setDataAtCell(that.row, that.col, tags_data);
    return tags_data
  };

  JsTreeEditor.prototype.close = function () {
      var tableContainer = $(this.instance.table).parents('div.handsontable');
      tableContainer.css('height', tableContainer.height() - this.tree.height());
      Handsontable.editors.HandsontableEditor.prototype.close.apply(this, arguments);
//    this.$htContainer.handsontable('getInstance').removeHook('beforeKeyDown', onBeforeKeyDownInner);
      this.div.style.display = 'none';
  };

  Handsontable.editors.JsTreeEditor = JsTreeEditor;
  Handsontable.editors.registerEditor('jstree', JsTreeEditor);

})(Handsontable);
