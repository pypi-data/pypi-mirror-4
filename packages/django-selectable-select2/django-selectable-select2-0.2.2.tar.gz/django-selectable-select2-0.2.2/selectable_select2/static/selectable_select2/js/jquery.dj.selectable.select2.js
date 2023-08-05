(function($) {
  $(document).ready(function() {

    var djs2limit = 20;

    var $selectitems = $("[data-selectable-type=select2]");
    $selectitems.each( function(index) {
        var $selectitem = $(this);
        var djs2url = $selectitem.data('selectableUrl');
        var clearonparentchange = $selectitem.data('clearonparentchange');

        var parents = [], parents_tmp = $selectitem.data('parents');
        if (parents_tmp) {
          parents_tmp = parents_tmp.split(',');
          $.each(parents_tmp, function(index, parent) {
              if (parent) {
                var el = $('#' + parent);
                parents.push(el);

                /* attach a "clear child" action to parents */
                if (clearonparentchange) {
                  el.change(function(evo) {
                    var val = false;
                    if (!val) {
                      $selectitem.data('select2').clear();
                      $selectitem.trigger('change');
                    }
                  });
                }
              }
          });
        }


        /* get an object parent names and values - for sending via AJAX */
        var get_parents_for_data = function () {
          var obj = {};

          $.each(parents, function(index, $parent) {
            var val, name = $parent.attr("name");
            if ($parent.hasOwnProperty("select2")) {
              val = $parent.select2("val");
            } else {
              val = $parent.val();
            }
            obj[name] = val;
          });

          return obj;
        };

        $selectitem.select2({
            // minimumInputLength : 1,
            width            :  'resolve',
            minimumResultsForSearch: djs2limit,
            allowClear       :  true,
            ajax             :  {
                                  url : djs2url,
                                  dataType: 'json',
                                  data : function (term, page) {
                                      var obj = { term : term, page: page};
                                      var parent_obj = get_parents_for_data();
                                      if (parent_obj) {
                                        $.extend(obj, parent_obj);
                                      }
                                       return obj;
                                  },
                                  results : function (data, page) {
                                      var more = data.meta.next_page ? true : false;
                                      return { results : data.data, more : more };
                                  }
                                },
            initSelection    :  function (element, callback) {
                                  /** TODO: adjust this to work with multiple selection */
                                    var data = {};
                                    var el_val = element.val();
                                    var initial_selection = element.data('initialSelection');
                                    if (initial_selection) {
                                      data = {
                                        id : el_val,
                                        value : initial_selection
                                      };
                                    }

                                    callback(data);
                                },
            formatResult     :  function (state) {
              return state.label;
            },
            formatSelection  :  function (state) {
              return state.value;
            },
            escapeMarkup: function(markup) { return markup; }
        });
     });
  });
})(jQuery);
