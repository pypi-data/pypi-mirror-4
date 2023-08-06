/*
 * Very much inspired by a script from NETTUTS.com [by James Padolsey]
 * @requires jQuery($), jQuery UI & sortable/draggable UI modules
 */
var iNettuts = {

  jQuery : $,

  settings : {
    columns : '.column',
    widgetSelector: '.widget',
    handleSelector: '.widget-head',
    contentSelector: '.widget-content',
    widgetDefault : {
      movable: true,
      removable: true,
      collapsible: true,
      editable: true,
      colorClasses : ['color-yellow', 'color-red', 'color-blue',
                      'color-white', 'color-orange', 'color-green']
    },
    widgetIndividual : {
      intro : {
        movable: false,
        removable: false,
        collapsible: false,
        editable: false
      }
    }
  },

  init : function () {
    this.addWidgetControls();
    this.makeSortable();
    $('#columns .unrelated-portlets .button a ').click(function() {
      $(this).closest('.unrelated-portlets').toggleClass('opened');
    });
  },

  getWidgetSettings : function (id) {
    var $ = this.jQuery,
      settings = this.settings;
    return ((id && settings.widgetIndividual[id])
            ? $.extend({},settings.widgetDefault,settings.widgetIndividual[id])
            : settings.widgetDefault);
  },

  _portletEid: function($widget) {
    return parseInt($widget.find(this.settings.contentSelector).attr('id').split('-')[1]);
  },

  savePortletState : function(domnode) {
    var $widget = $(domnode).closest('li.widget'), params = {};
    var eid = this._portletEid($widget);
    params['name'] = $widget.find(this.settings.handleSelector).find('h3').text();
    var color_match = /color-([^ ]+)/.exec($widget.attr('class'));
    if (color_match) {
      params['color'] = color_match[1];
    }
    params['collapsed'] = $widget.hasClass('collapsed');
    asyncRemoteExec('save_portlet_state', eid, params);
  },

  savePortalColumnsState : function(domnodes) {
    console.log('savePortalColumnsState %o', domnodes);
    var iNettuts = this, params = [];
    $(domnodes).each(function(index, domnode) {
      var $column = $(domnode).closest('.column');
      var eid = parseInt($column.attr('id').split('-')[2]);
      var portlet_eids = $.map($column.find(iNettuts.settings.widgetSelector),
        function(widget) {
          return iNettuts._portletEid($(widget));
        });
      params.push({'eid': eid, 'portlet_eids': portlet_eids});
    });
    asyncRemoteExec('save_portal_columns_state', params);
  },

  addWidgetControls : function () {
    var iNettuts = this,
      $ = this.jQuery,
      settings = this.settings;

    $(settings.widgetSelector, $(settings.columns)).each(function () {
      var thisWidgetSettings = iNettuts.getWidgetSettings(this.id);
      if (thisWidgetSettings.removable) {
        $('<a href="#" class="remove">CLOSE</a>').mousedown(function (e) {
          e.stopPropagation();
        }).click(function () {
            $(this).parents(settings.widgetSelector).animate(
              {opacity: 0},
              function () {
                $(this).wrap('<div/>').parent().slideUp(function () {
                  var $widget = $(this).find('.widget');
                  var orig_col = $(this).closest('.column')[0];
                  $widget.css('opacity', 1).appendTo($('.unrelated-portlets ul.column'))
		    .closest('.unrelated-portlets').addClass('opened');
                  $(this).remove();
                  iNettuts.savePortalColumnsState([orig_col]);
                });
              });
          return false;
        }).appendTo($(settings.handleSelector, this));
      }

      if (thisWidgetSettings.editable) {
        $('<a href="#" class="edit">EDIT</a>').mousedown(function (e) {
          e.stopPropagation();
        }).toggle(
          function () {
            $(this).css({backgroundPosition: '-66px 0', width: '55px'})
              .parents(settings.widgetSelector)
              .find('.edit-box').show().find('input').focus();
            return false;
          },
          function () {
            $(this).css({backgroundPosition: '', width: ''})
              .parents(settings.widgetSelector)
              .find('.edit-box').hide();
            iNettuts.savePortletState(this);
            return false;
          }).appendTo($(settings.handleSelector,this));
          var colorList = '';
          $(thisWidgetSettings.colorClasses).each(function () {
            colorList += '<li class="' + this + '"/>';
          });
          $('<div class="edit-box" style="display:none;"/>')
            .append('<ul><li class="item"><label>Titre</label>'
              + '<input value="' + $('h3',this).text() + '"/></li>'
              + '<li class="item"><label>Couleur</label>'
              + '<ul class="colors">' + colorList + '</ul></li></ul>')
            .insertAfter($(settings.handleSelector,this));
        }

        if (thisWidgetSettings.collapsible) {
          $('<a href="#" class="collapse">COLLAPSE</a>').mousedown(function (e) {
            e.stopPropagation();
          }).click(
            function () {
              $(this).closest(settings.widgetSelector).toggleClass('collapsed');
              iNettuts.savePortletState(this);
              return false;
            }).prependTo($(settings.handleSelector,this));
        }
    });

    $('.edit-box').each(function () {
      $('input',this).keyup(function () {
        $(this).parents(settings.widgetSelector).find('h3')
          .text($(this).val().length>20
                ? $(this).val().substr(0,20) + '...'
                : $(this).val());
        });
        $('ul.colors li',this).click(function () {
          var colorStylePattern = /\bcolor-[\w]{1,}\b/;
          var thisWidgetColorClass = $(this).parents(settings.widgetSelector)
            .attr('class').match(colorStylePattern);
          if (thisWidgetColorClass) {
            $(this).parents(settings.widgetSelector)
              .removeClass(thisWidgetColorClass[0])
              .addClass($(this).attr('class').match(colorStylePattern)[0]);
          }
          return false;
        });
    });
  },

  makeSortable : function () {
    var iNettuts = this,
      $ = this.jQuery,
      settings = this.settings,
      $sortableItems = (function () {
        var notSortable = '';
        $(settings.widgetSelector,$(settings.columns)).each(function (i) {
          var movable = iNettuts.getWidgetSettings(this.id).movable;
          if (!movable) {
            if (!this.id) {
              this.id = 'widget-no-id-' + i;
            }
            notSortable += '#' + this.id + ',';
          }
        });
        return $('> li' + (notSortable == '' ? '' : ':not(' + notSortable + ')'), settings.columns);
      })();

    $sortableItems.find(settings.handleSelector).css({
      cursor: 'move'
    }).mousedown(function (e) {
      $sortableItems.css({width:''});
      $(this).parent().css({
        width: $(this).parent().width() + 'px'
      });
    }).mouseup(function () {
      if(!$(this).parent().hasClass('dragging')) {
        $(this).parent().css({width:''});
      } else {
        $(settings.columns).sortable('disable');
      }
    });

    $(settings.columns).sortable({
      items: $sortableItems,
      connectWith: $(settings.columns),
      handle: settings.handleSelector,
      placeholder: 'widget-placeholder',
      forcePlaceholderSize: true,
      revert: 300,
      delay: 100,
      opacity: 0.8,
      containment: 'document',
      start: function (e,ui) {
        $(ui.helper).addClass('dragging');
      },
      stop: function (e,ui) {
        ui.item.css({width:''}).removeClass('dragging');
        $(settings.columns).sortable('enable');
        // When moving a portlet, 2 columns must be updated and reordered :
        // * the column of origin (`this`)
        // * the target column, if different
        // The unrelated-portlets special column must never be sent to the
        // the server though : it just represents portlets that are not related
        // to present portal
        var cols = [];
        $.each([this, ui.item.closest('.column')[0]], function(index, value) {
          if ($(value).closest('.unrelated-portlets').length==0 && cols.indexOf(value) == -1) {
            cols.push(value);
          }
        });
        if (cols.length > 0) {
          iNettuts.savePortalColumnsState(cols);
        }
      }
    });
  }
};
