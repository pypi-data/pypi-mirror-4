(function($) {
  $(document).ready(function() {

    var djsels2limit = 20;

    var $selectitems = $("[data-selectable-type=select2]");
    $selectitems.each( function(index) {
        var loading_more = ""; // a string for indicating of loading more results
        var $selectitem = $(this);
        var djs2url = $selectitem.data('selectableUrl');
        var clearonparentchange = $selectitem.data('djsels2Clearonparentchange');

        var parents = [], parents_tmp = $selectitem.data('djsels2ParentIds');
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
        var get_parents_for_data = function ($s2element) {
          var obj = {};
          var parent_name_map = {};
          var parent_name_map_tmp = $s2element.data('djsels2ParentNamemap');
          if (typeof parent_name_map_tmp !== "undefined") {
            // convert a comma delimited list to an object
            var _i, _len, _iter = parent_name_map_tmp.split(",");
            for (_i = 0, _len = _iter.length; _i < _len; _i = _i + 2 ) {
              parent_name_map[_iter[_i]] = _iter[_i + 1];
            }
          }

          $.each(parents, function(index, $parent) {
            var val, name = parent_name_map[$parent.attr("id")];
            if (typeof name == "undefined") {
              name = $parent.attr("name");
            }
            if ($parent.hasOwnProperty("select2")) {
              val = $parent.select2("val");
            } else {
              val = $parent.val();
            }
            if (val !== "") {
              obj[name] = val;
            }
          });
          return obj;
        };

        $selectitem.select2({
            // minimumInputLength : 1,
            width            :  'resolve',
            minimumResultsForSearch: djsels2limit,
            allowClear       :  true,
            ajax             :  {
                                  url : djs2url,
                                  dataType: 'json',
                                  data : function (term, page) {
                                      var obj = { term : term, page: page};
                                      var parent_obj = get_parents_for_data($selectitem);
                                      if (parent_obj) {
                                        $.extend(obj, parent_obj);
                                      }
                                       return obj;
                                  },
                                  results : function (data, page) {
                                      var more = data.meta.next_page ? true : false;
                                      loading_more = data.meta.more;
                                      return { results : data.data, more : more };
                                  }
                                },
            initSelection    :  function (element, callback) {
                                  /** TODO: adjust this to work with multiple selection */
                                    var data = {};
                                    var el_val = element.val();
                                    var initial_selection = element.data('djsels2Initialselection');
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
            formatLoadMore: function (pageNumber) {
              return loading_more;
            },
            escapeMarkup: function(markup) { return markup; }
        });
     });
  });
})(jQuery);
