options = {
    success: function(files) {
      var url = '/' + lab_pk + '/units/'+ window.unit_data['data-0-pk'] +'/dropxbox-upload/'
      var need_upload = $('.upload-file').is(":checked")
      $.post(url,{'files[]': JSON.stringify(files), 'need_upload': need_upload}, function(data){
        $('.blueimp-uploader').fileupload('destroy');
        $('.blueimp-uploader').find('.file_table').html("");
        update_uploaders()
      })
    },
    cancel: function() {},
    linkType: "direct",
    multiselect: true,
//    extensions: ['.pdf', '.doc', '.docx'],
};

    var exp_pk = $("#experiment_row").data('experiment-pk');
    window.unit_data = {}
    var treeElement = $('#tag-tree');

    $(function() {
      InitJSTree(treeElement,['search', 'checkbox']);

      // set height of comment block
      $('.comment-activities').css('max-height', window.innerHeight -430)
      if (window.innerHeight > 650) {
        $('.comment-activities').not('.comments-list').css('max-height', $('.main-sidebar').height() - 325)
      }
      $('#exp-workfow iframe').css('min-height', $('.main-sidebar').height() -100)
      setTimeout( function() {
            comments_scroll_to_end()
       }, 500);

      // fix bootstrap tabs urls
      var hash = window.location.hash;
      hash = hash.substr(0, 2) == '#/' ? '#' + hash.substr(2) :  hash;
      hash && $('ul.nav a[href="' + hash + '"]').tab('show');

      $('.nav-tabs.exp-nav a').click(function (e) {
        $(this).tab('show');
        var scrollmem = $('body').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(scrollmem);
      });

    });

    // fix handsontable bug with tabs
    $('a[href="#unit-measurements"]').on('shown.bs.tab', function (e) {
      if ($('#unit-measurements .btn').is(':visible')) {
        $('#dataTableEditable').handsontable('render');
      }
    });

    function update_unit_info(unit){
      /**
      * Update unit info tabs.
      * @param unit - object {id: unit_id} For the the compatibility with d3 function call.
      */
      var url = '/' + lab_pk + '/units/detail_json/'+ unit.id + '/'
      $.get(url, {unit_pk: unit.id}, function(data){
        // set global current unit

        function get_parents(unit_data) {
          /**
           * Return array of unit parents ids
           * @param unit_data - (string) serialized unit object
           */
          var unit_json = JSON.parse(unit_data)
          var parents = []
          for (var i=0; i< unit_json.parent.length; i++) {
            parents.push(unit_json.parent[i]['$oid'])
          }
          return parents
        }

        function get_tags(unit_data) {
          /**
           * Return array of unit parents ids
           * @param unit_data - (string) serialized unit object
           */
          var unit_json = JSON.parse(unit_data)
          var tags = []
          for (var i=0; i< unit_json.tags.length; i++) {
            tags.push(unit_json.tags[i]['$oid'])
          }
          return tags
        }

        var unit_json = JSON.parse(data.unit_data)
        window.unit_data = {
          'data-0-pk': data.pk,
          'data-0-sample': data.sample,
          'data-0-description': unit_json.description,
          'data-0-parent_pk[]': get_parents(data.unit_data),
          'data-0-experiments_pk[]': exp_pk,
          'data-0-tags_pk[]': get_tags(data.unit_data),
          'length':1
        }
        unit_data = window.unit_data

        // show hidden tab's buttons
        $('#unit-measurements .btn').show()
        $('#unit-desc .btn').show()
        $('#unit-tags .btn').show()

        // description
        $('.desc-area').html(data.description)
        update_uploaders()
        var button = Dropbox.createChooseButton(options);
        document.getElementById("dropbox").appendChild(button);
        addSelect2();

        // measurements
        var table = $("#dataTableEditable");
        var table_data = JSON.parse(data.measurements);
        var save_url = '/' + lab_pk + '/measurements/'+ unit.id + '/create/'
        table.data('url', save_url)
        table.handsontable('loadData', table_data);

        // revisions
        $('.revision-list').html('');
        if (data.revisions){
          var revisions = JSON.parse(data.revisions);
          for (var i = 0; i < revisions.length; i++) {
            var rev = revisions[i];
            var h = '<li><a href="javascript:void(0);" class="revert-revision" data-url="' + rev.url +'">' +rev.timestamp +'</a></li>'
            $('.revision-list').append(h);
          }
        }

        // tags
        treeElement.jstree('deselect_all')
        treeElement.jstree('select_node', JSON.parse(data.tags))

        // comments
        $('#unit-comments').html(data.comments)
        addSumernote();

        //edit button
//        var edit_url = '/{{ lab.pk }}/units/detail/'+ unit.id + '/'
//        $('.edit-unit').attr('href', edit_url);

        // set active unit in list
        $('.unit-item').removeClass('active')
        $('.unit-item').each(function(e){
          if($(this).data('unit-pk') == unit.id){
            $(this).addClass('active')
            return false
          }
        })
      });
    }

    // save unit tags
    $("#unit-tags").on( "click", "#tag-save", function() {
      var selected_tags = treeElement.jstree('get_selected')
      var save_url ='/'+ lab_pk +'/units/create/';
      unit_data['data-0-tags_pk[]'] = selected_tags;
      $.post(save_url, unit_data);
    });

    // revert table data on revision restore
    $('body').on('click',' .revert-revision', function (e) {
        var url = $(this).data('url');
        $.post(url, function (data) {
            var table = $("#dataTableEditable");
            var table_data = data.table_data;
            table_data.unshift(data.headers);
            table.handsontable('loadData', table_data);
        });

        reset_plot();

        return false
    });

     $('body').on('submit','.description-unit-form', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $form = $(e.target);
        var unit_data = window.unit_data
        unit_data['data-0-description'] = $form.find('textarea[name="description"]').val();

        $.post($form.attr('action'), unit_data)
            .fail(function (xhr) {
                form_fail($form, xhr)
            }).done(function (response) {
                var desc_value = $form.find('textarea[name="description"]').val()
                $form.find('.field-editor').hide().closest('.field-container').find('.field-show').show();
                $form.find('.field-editor').hide().closest('.field-container').find('.field-text').html(desc_value);

            });
    });

  $('body').on('submit','.sample-unit-form', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $form = $(e.target);
    var unit_data = window.unit_data
    var sample = $form.find('input[name="sample"]').val()
    unit_data['data-0-sample'] = sample;

    $.post($form.attr('action'), unit_data)
            .fail(function (xhr) {
              form_fail($form, xhr)
            }).done(function (response) {
              $form.find('.field-editor').hide().closest('.field-container').find('.field-show').show();
              $form.find('.field-editor').hide().closest('.field-container').find('.field-text').html(sample);
              graph.updateNodeText(response[0][1]['pk'], sample)

            });
  });

  $('body').on('submit','.parent-unit-form', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $form = $(e.target);
    var unit_data = window.unit_data

    var parents = $form.find('select[name="parent"]').val()
    if (parents) {
      unit_data['data-0-parent_pk[]'] = parents;
    } else {
      delete unit_data['data-0-parent_pk[]']
    }

    $.post($form.attr('action'), unit_data)
            .fail(function (xhr) {
              form_fail($form, xhr)
            }).done(function (response) {
              $form.find('.field-editor').hide().closest('.field-container').find('.field-show').show();
                $form.find('.field-editor').hide().closest('.field-container').find('.field-text').html(parents);
              graph.updateParents(response[0][1]['pk'], parents)
            });
  });

  $('body').on('submit','.links-unit-form', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $form = $(e.target);
        var link = $form.find('input[name="link"]').val();

        $.post($form.attr('action'), $form.serialize())
            .fail(function (xhr) {
                var data = xhr.responseJSON;
                $form.find('.has-error').removeClass('has-error').removeAttr('title');
                for (var name in data) {
                    if (data.hasOwnProperty(name)) {
                        var icon = $('<i>', {'class': 'fa fa-warning'}),
                            error_message = $('span', {
                                'class': 'text-red error-msg',
                                'id': 'error_' + $form.find('[name="' + name + '"]').id
                            }).text(data[name].join(', ')).append(icon);

                        $form.find('[name="' + name + '"]')
                            .after(error_message);
                        $form.find('[name="' + name + '"]')
                            .parents('.form-group')
                            .addClass('has-error')
                            .attr('title', data[name].join(', '));
                    }
                }
            }).done(function (response) {
                $('.link-list').append(response.html);
                $form.find('input[name="link"]').val('');
            });
    });

    $('body').on('click','.link-delete', function (e) {
        e.preventDefault();
        e.stopPropagation();

        if(confirm('Delete this link?')) {
          var delete_url = $(this).data("delete-url");
          var parent_box = $(this).closest('.box')
          $.post(delete_url, {}, function (response) {
            parent_box.remove();
          });
        }
        return false
    });

  $('body').on('click','.box-collapse', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).closest('.box').find('.box-body').toggle(200);
    });

    $('body').on('submit','.add-unit-form', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $form = $(e.target);

        $.post($form.attr('action'), $form.serialize())
            .fail(function (xhr) {
                form_fail($form, xhr)
            }).done(function (response) {

               $('#add_unit').modal('toggle');
               var units = $form.find('select[name="units"]').val();
                for (i in units){
                  graph.addNode({
                          id: units[i],
                          index: 0,
                          link: "#",
                          score: 2,
                          size: 1,
                          text:  $form.find('select[name="units"]').find('option[value=' + units[i]+ ']').text(),
                          type: "circle",
                          weight: 1,
                        });
                }

            });
      });

    //upload files from filemanager
    $('body').on('click', '.fm-choose', function(e){
      var file_url = $(this).data('path')
      var file_name = $(this).data('name');

      var url = '/' + lab_pk + '/units/'+ window.unit_data['data-0-pk'] +'/local-upload/'
      var need_upload = $('.upload-file').is(":checked")
      var file = {
        name:file_name,
        link:file_url,
      }
      $.post(url,{'files[]': JSON.stringify([file,]), 'need_upload': need_upload}, function(data){
        $('.blueimp-uploader').fileupload('destroy');
        $('.blueimp-uploader').find('.file_table').html("");
        update_uploaders()
      })
      $('#fm').modal('hide')
    })


  $(function() {
    var graph = window.graph  = new render_graph($('.graph-area').data('graph-json'), '.graph-area', update_unit_info)
    //graph.addLink("Cause", "Effect");

    $('.create-unit').click(function (e) {
      e.preventDefault();
      e.stopPropagation();
      var sample = 'New Unit #'
      var unit_data = {
        'length':1,
        'data-0-experiments_pk[]': exp_pk,
        'data-0-sample': sample,

      }

      $.post($(this).data('url'), unit_data, function (response) {

        graph.addNode({
          id: response[0][1]['pk'],
          index: 0,
          link: "#",
          score: 2,
          size: 1,
          text: sample,
          type: "circle",
          weight: 1,

        });

      });
    })


      $('.unit-item').click(function(e){
        var unit_id = $(this).data('unit-pk')
        update_unit_info({id: unit_id})
      })

      // fix d3 in hidden tabs
      $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        window.dispatchEvent(new Event('resize'));
      })

    });
//  $('body').on('click','.comment-input', function (e) {
//        e.preventDefault();
//        e.stopPropagation();
//        $(this).hide()
//        $(this).closest('form').find('.comment-editor').show();
//    });
  $('body').on('click','.comment-cancel', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).closest('form').find('.comment-input').show();
        $(this).closest('form').find('.comment-editor').hide();
    });