 glyph_opts = {
    map: {
      doc: "glyphicon glyphicon-file",
      docOpen: "glyphicon glyphicon-file",
      checkbox: "glyphicon glyphicon-unchecked",
      checkboxSelected: "glyphicon glyphicon-check",
      checkboxUnknown: "glyphicon glyphicon-share",
      dragHelper: "glyphicon glyphicon-play",
      dropMarker: "glyphicon glyphicon-arrow-right",
      error: "glyphicon glyphicon-warning-sign",
      expanderClosed: "glyphicon glyphicon-plus-sign",
      expanderLazy: "glyphicon glyphicon-plus-sign",
      // expanderLazy: "glyphicon glyphicon-expand",
      expanderOpen: "glyphicon glyphicon-minus-sign",
      // expanderOpen: "glyphicon glyphicon-collapse-down",
      folder: "glyphicon glyphicon-folder-close",
      folderOpen: "glyphicon glyphicon-folder-open",
      loading: "glyphicon glyphicon-refresh"
    }
  };
$(function () {
    InitFancyTree($('#location-tree'));
});


function InitFancyTree(treeElement, plugins){

    if (typeof(treeElement)==='undefined') treeElement = $('#location-tree');
    if (typeof(plugins)==='undefined') plugins = ['search'];

    var pre_url = '/' + treeElement.data('lab') + '/tags/update/'
    searchElement = $('#search'),
        formContainerElement = $('#location-container'),
        // Initialize Fancytree
        tree = $("#location-tree").fancytree({
            extensions: ["dnd", "edit", "glyph", "wide", "filter"],
            checkbox: true,
            edit: {
                triggerStart: ["f2", "dblclick", "shift+click", "mac+enter"],
                beforeEdit: function(event, data){
                    // Return false to prevent edit mode
                },
                edit: function(event, data){
                    // Editor was opened (available as data.input)
                },
                beforeClose: function(event, data){
                    // Return false to prevent cancel/save (data.input is available)
                },
                save: function(event, data){
                    // Save data.input.val() or return false to keep editor open
                    var update_url = pre_url+data.node.key+'/';
                    $.post(update_url, {
                        'details': data.input.val(),
                        'parent': data.node.parent.key
                    })
                    return true;
                },
                close: function(event, data){
                    // Editor was removed
                    if( data.save ) {
                        // Since we started an async request, mark the node as preliminary
                        $(data.node.span).addClass("pending");
                    }
                }
            },
            dnd: {
                autoExpandMS: 400,
                focusOnClick: true,
                preventVoidMoves: true, // Prevent dropping nodes 'before self', etc.
                preventRecursiveMoves: true, // Prevent dropping nodes on own descendants
                dragStart: function(node, data) {
                    /** This function MUST be defined to enable dragging for the tree.
                     *  Return false to cancel dragging of node.
                     */
                    return true;
                },
                dragEnter: function(node, data) {
                    /** data.otherNode may be null for non-fancytree droppables.
                     *  Return false to disallow dropping on node. In this case
                     *  dragOver and dragLeave are not called.
                     *  Return 'over', 'before, or 'after' to force a hitMode.
                     *  Return ['before', 'after'] to restrict available hitModes.
                     *  Any other return value will calc the hitMode from the cursor position.
                     */
                    // Prevent dropping a parent below another parent (only sort
                    // nodes under the same parent)
                    /*           if(node.parent !== data.otherNode.parent){
                     return false;
                     }
                     // Don't allow dropping *over* a node (would create a child)
                     return ["before", "after"];
                     */
                    return true;
                },
                dragDrop: function(node, data) {
                    /** This function MUST be defined to enable dropping of items on
                     *  the tree.
                     */
                    data.otherNode.moveTo(node, data.hitMode);
                    var parent = data.otherNode.parent;
                    if (data.otherNode.parent.key == 'root_1') {
                        var parent = '';
                    } else {
                        var parent = data.otherNode.parent.key;
                    }
                    var update_url = pre_url + data.otherNode.key+'/';
                    $.post(update_url, {
                        'details': data.otherNode.title,
                        'parent': parent,
                    })

                }
            },
            filter: {
                autoApply: true, // Re-apply last filter if lazy data is loaded
                counter: true, // Show a badge with number of matching child nodes near parent icons
                hideExpandedCounter: true, // Hide counter badge, when parent is expanded
                mode: "dimm"  // "dimm": Grayout unmatched nodes, "hide": remove unmatched nodes
            },
            glyph: glyph_opts,
            selectMode: 2,
            source: treeElement.data('content'),
            toggleEffect: { effect: "drop", options: {direction: "left"}, duration: 400 },
            wide: {
                iconWidth: "1em",     // Adjust this if @fancy-icon-width != "16px"
                iconSpacing: "0.5em", // Adjust this if @fancy-icon-spacing != "3px"
                levelOfs: "1.5em"     // Adjust this if ul padding != "16px"
            },


        });
    var tree = treeElement.fancytree("getTree");

    // Search input
    $("#search").keyup(function (e) {
        var n;
        match = $(this).val();
        if (match) {
            n = tree.filterNodes(match, {autoExpand: true, leavesOnly: false});
        } else {
            tree.clearFilter();
        }
    }).focus();

    $('#location-remove').click(function (e) {
        e.preventDefault();
        var selected_nodes = tree.getSelectedNodes()
        var delete_url = '/' + treeElement.data('lab') + '/tags/delete/'
        var deleted_ids = []
        for (var i=0; i<selected_nodes.length; i++) {
            deleted_ids.push(selected_nodes[i].key)
        }

        $.post(delete_url || $(this).closest('form').attr('action'), {
            ids: deleted_ids,
            csrfmiddlewaretoken: csrftoken
        }).done(function (response) {
            for (var i=0; i<selected_nodes.length; i++) {
                selected_nodes[i].remove()
            }
            formContainerElement.html('');
            showMessage(false, response.message);
        }).fail(function (xhr) {
            showMessage(true, xhr.responseJSON);
            console.log(xhr.responseJSON);
        });
        $('#confirm-delete').modal('hide');

    });
};


