if(window.DavizEdit === undefined){
  var DavizEdit = {'version': '4.0'};
  DavizEdit.Events = {};
}

/** Events
*/
DavizEdit.Events.facet = {
  changed: 'daviz-facet-changed',
  deleted: 'daviz-facet-deleted',
  refreshed: 'daviz-facets-refreshed'
};

DavizEdit.Events.views = {
  refresh: 'daviz-views-refresh',
  refreshed: 'daviz-views-refreshed',
  clicked: 'daviz-view-clicked'
};

/** Status
*/
DavizEdit.Status = {
  initialize: function(){
    this.area = jQuery('.daviz-settings');
    this.area.append(jQuery('<div>').addClass('daviz-cleanup'));
    this.lock = jQuery('<div>').addClass('daviz-status-lock');
    this.message = jQuery('<div>').addClass('daviz-ajax-loader');
    this.lock.prepend(this.message);
    this.area.prepend(this.lock);

    this.lock.dialog({
      show: 'slow',
      hide: 'slow',
      modal: true,
      closeOnEscape: false,
      autoOpen: false,
      draggable: false,
      resize: false,
      dialogClass: 'daviz-loading-overlay'
    });
  },

  start: function(msg){
    this.message.html(msg);
    this.lock.dialog('open');
  },

  stop: function(msg){
    this.message.html(msg);
    this.lock.dialog('close');
  }
};


/** Confirm dialog
*/
DavizEdit.Confirm = {
  initialize: function(){
    var self = this;
    self.event = null;
    self.kwargs = {};

    self.area = jQuery('<div>').addClass('daviz-confirm').attr('title', 'Confirm');
    jQuery('daviz-views-edit').after(self.area);
    self.area.dialog({
      bgiframe: true,
      autoOpen: false,
      modal: true,
      dialogClass: 'daviz-confirm-overlay',
      buttons:  {
        Yes: function(){
          if(self.event !== null){
            jQuery(document).trigger(self.event, self.kwargs);
          }
          jQuery(this).dialog('close');
        },
        No: function(){
          jQuery(this).dialog('close');
        }
      }
    });
  },

  confirm: function(msg, event, kwargs){
    var self = this;
    self.area.html(msg);
    self.event = event;
    self.kwargs = kwargs;
    self.area.dialog('open');
  }
};


/** Facets
*/
DavizEdit.Facets = {
  initialize: function(){
    var self = this;
    self.facets = {};
    self.area = jQuery('.daviz-facets-edit').addClass('daviz-facets-edit-ajax');

    // Events
    jQuery(document).bind(DavizEdit.Events.facet.deleted, function(evt, data){
      self.handle_delete(data);
    });

    jQuery(document).bind(DavizEdit.Events.facet.refreshed, function(evt, data){
      self.handle_refresh(data);
    });

    jQuery(document).bind(DavizEdit.Events.views.clicked, function(evt, data){
      self.handle_tab(data);
    });

    jQuery(document).trigger(DavizEdit.Events.facet.refreshed, {init: true});
  },

  handle_refresh: function(data){
    var self = this;
    if(data.init){
      self.setup();
    }else{
      var action = data.action;
      var i = action.indexOf('@@');
      action = action.slice(0, i) + '@@daviz-edit.facets.html';
      DavizEdit.Status.start('Refreshing ...');
      jQuery.get(action, {}, function(data){
        self.area.html(data);
        self.setup();
        DavizEdit.Status.stop("Done");
      });
    }
  },

  setup: function(){
    var self = this;
    // Add box
    jQuery('.daviz-facet-add', self.area).each(function(){
      var facet = jQuery(this);
      var add = new DavizEdit.FacetAdd(facet);
    });

    // Facets
    jQuery('.daviz-facet-edit', self.area).each(function(){
      var facet = jQuery(this);
      self.facets[facet.attr('id')] = new DavizEdit.Facet(facet);
    });

    // Sortable
    jQuery('.daviz-facets-edit-ajax').sortable({
      items: '.daviz-facet-edit',
      placeholder: 'ui-state-highlight',
      forcePlaceholderSize: true,
      opacity: 0.7,
      delay: 300,
      cursor: 'crosshair',
      tolerance: 'pointer',
      update: function(event, ui){
        self.sort(ui.item.parent());
      }
    });
  },

  sort: function(context){
    facets = jQuery('.facet-title', context);
    var order = jQuery.map(facets, function(value){
      return jQuery(value).text();
    });

    var action = jQuery('form', context).attr('action');
    var index = action.indexOf('@@');
    action = action.slice(0, index) + '@@daviz-edit.save';

    query = {'daviz.facets.save': 'ajax', order: order};
    DavizEdit.Status.start('Saving ...');
    jQuery.ajax({
      traditional: true,
      type: 'post',
      url: action,
      data: query,
      success: function(data){
       DavizEdit.Status.stop(data);
      }
    });
  },

  handle_delete: function(kwargs){
    var self = this;
    var facet = kwargs.facet;
    var name = facet.attr('id');

    var action = jQuery('form', facet).attr('action');
    var i = action.indexOf('@@');
    action = action.slice(0, i) + '@@daviz-edit.save';
    var query = {'daviz.facet.delete': 'ajax', name: name};

    facet.slideUp(function(){
      DavizEdit.Status.start('Saving ...');
      jQuery.ajax({
        traditional: true,
        type: 'post',
        url: action,
        data: query,
        success:  function(data){
          DavizEdit.Status.stop(data);
          var currentTab = 0;
          var tabs = jQuery('.daviz-views-edit ul');
          var tab = null;
          if(tabs.length){
            tabs = tabs.data('tabs');
            currentTab = tabs.getIndex();
            tab = tabs.getCurrentTab();
          }

          jQuery(document).trigger(DavizEdit.Events.views.refresh, {
            init: false,
            action: jQuery('form', facet).attr('action'),
            currentTab: currentTab,
            tab: tab
          });

          facet.remove();
          delete self.facets[name];
        }
      });
    });
  },

  handle_tab: function(kwargs){
    var self = this;
    var href = jQuery(kwargs.tab).attr('href');

    if(!href){
      return self.area.hide();
    }

    if(href === '#daviz-properties-tab'){
      return self.area.hide();
    }

    if(href.indexOf('#daviz-') !== 0){
      return self.area.hide();
    }

    if(jQuery(href + ' .daviz-view-form-disabled').length){
      return self.area.hide();
    }

    return self.area.show();
  }
};

/** Add facets box
*/
DavizEdit.FacetAdd = function(facet){
  this.initialize(facet);
};

DavizEdit.FacetAdd.prototype = {
  initialize: function(facet){
    var self = this;
    self.facet = facet;
    self.form = jQuery('form', facet);
    self.action = self.form.attr('action');
    self.button = jQuery('input[type=submit]', this.form).hide();

    self.form.submit(function(){
      return false;
    });

    self.form.dialog({
      bgiframe: true,
      autoOpen: false,
      modal: true,
      dialogClass: 'daviz-facet-add-overlay',
      buttons:  {
        Add: function(){
          self.submit();
          jQuery(this).dialog('close');
        },
        Cancel: function(){
          jQuery(this).dialog('close');
        }
      }
    });

   var plus = jQuery("<span>")
      .attr('title', 'Add new facet')
      .text('+')
      .addClass('ui-icon').addClass('ui-icon-plus').addClass('ui-corner-all');

    self.facet.prepend(plus);

    plus.click(function(){
      self.form.dialog('open');
    });
  },

  submit: function(){
    var self = this;
    var name = self.button.attr('name');
    var query = name + '=ajax&';
    query += self.form.serialize();

    DavizEdit.Status.start('Adding ...');
    jQuery.ajax({
      traditional: true,
      type: 'post',
      url: self.action,
      data: query,
      success: function(data){
        jQuery(document).trigger(DavizEdit.Events.facet.refreshed, {
          init: false, action: self.action});
        DavizEdit.Status.stop(data);
      }
    });
  }
};


/** Facet
*/
DavizEdit.Facet = function(facet){
  this.initialize(facet);
};

DavizEdit.Facet.prototype = {
  initialize: function(facet){
    var self = this;
    this.facet = facet;
    this.form = jQuery('form', facet);
    this.action = this.form.attr('action');
    this.button = jQuery('input[type=submit]', this.form);
    this.button.hide();

    var show = jQuery("div.field:has([id$=.show])", this.form).hide();
    this.show = jQuery("[id$=.show]", show);
    this.visible = this.show.attr('checked');

    var title = jQuery('h1', this.form);
    title.attr('title', 'Click and drag to change widget position');

    var html = title.html();
    var newhtml = jQuery('<div>').addClass('facet-title').html(html);
    title.html(newhtml);

    this.hide_icon(title);
    this.delete_icon(title);

    this.form.submit(function(){
      return false;
    });

    // Events
    jQuery(document).bind(DavizEdit.Events.facet.changed, function(evt, data){
      self.submit(data);
    });

    jQuery(':input', this.form).change(function(){
      var form = jQuery(this).parents('form');
      var label = jQuery('input[name*=.label]', form);
      var key = label.attr('name').replace('.label', '');
      var value = label.val();
      jQuery(document).trigger(DavizEdit.Events.facet.changed, {
        key: key,
        value: value
      });
      return false;
    });
  },

  hide_icon: function(title){
    var self = this;

    var msg = 'Hide facet';
    var css = 'ui-icon-hide';
    if(!self.visible){
      msg = 'Show facet';
      css = 'ui-icon-show';
      title.addClass('hidden');
    }
    var icon = jQuery('<div>')
      .html('h')
      .attr('title', msg)
      .addClass('ui-icon')
      .addClass(css);

    icon.click(function(){
      if(self.visible){
        self.visible = false;
        icon.removeClass('ui-icon-hide')
          .addClass('ui-icon-show')
          .attr('title', 'Show facet');
          title.addClass('hidden');
      }else{
        self.visible = true;
        icon.removeClass('ui-icon-show')
          .addClass('ui-icon-hide')
          .attr('title', 'Hide facet');
          title.removeClass('hidden');
      }
      self.show.click();
      self.submit();
    });
    title.prepend(icon);
  },

  delete_icon: function(title){
    var self = this;
    var icon = jQuery('<div>')
      .html('x')
      .attr('title', 'Delete facet')
      .addClass('ui-icon')
      .addClass('ui-icon-trash');

    icon.click(function(){
      var msg = "Are you sure you want to delete facet: <strong>" + self.facet.attr('id') + "</strong>. ";
      msg += "You should consider hiding it, instead of deleting it, otherwise ";
      msg += "you'll have to manually update Views properties if this facet id is used by any of them.";
      DavizEdit.Confirm.confirm(msg, DavizEdit.Events.facet.deleted, {facet: self.facet});
    });

    title.prepend(icon);
  },

  submit: function(options){
    var self = this;

    if(options){
      var label = jQuery('input[name=' + options.key + '.label]', this.form);
      if(!label.length){
        return;
      }
      label.val(options.value);
    }

    var name = this.button.attr('name');
    var query = name + '=ajax&';
    query += this.form.serialize();

    DavizEdit.Status.start('Saving ...');
    jQuery.ajax({
      traditional: true,
      type: 'post',
      url: self.action,
      data: query,
      success: function(data){
        DavizEdit.Status.stop(data);
      }
    });
  }
};

/** Views
*/
DavizEdit.Views = {
  initialize: function(){
    var self = this;

    jQuery(document).bind(DavizEdit.Events.views.refresh, function(evt, data){
      self.update_views(data);
    });
    jQuery(document).trigger(DavizEdit.Events.views.refresh, {
      init: true,
      action: jQuery('.daviz-views-edit form').attr('action'),
      currentTab: 0,
      tab: null
    });
  },

  update_views: function(form){
    var self = this;
    self.views = {};
    self.area = jQuery('.daviz-views-edit').addClass('daviz-views-edit-ajax');
    var action = form.action;
    var i = action.indexOf('@@');
    action = action.slice(0, i) + '@@daviz-edit.views.html';

    if(!form.init){
      DavizEdit.Status.start('Refreshing ...');
      jQuery.get(action, {}, function(data){
        self.area.html(data);
        self.update_tabs(action);
        jQuery(document).trigger(DavizEdit.Events.views.refreshed, form);
        DavizEdit.Status.stop("Done");
      });
    }else{
      self.update_tabs(action);
    }
  },

  update_tabs: function(action){
    var self = this;
    jQuery('.daviz-view-edit', self.area).each(function(){
      var view = jQuery(this);
      self.views[view.attr('id')] = new DavizEdit.View(view);
    });
    jQuery('fieldset', self.area).addClass('daviz-edit-fieldset');
    jQuery('form.daviz-view-form h1', self.area).hide();

    // Make tabs
    var ul = jQuery('ul.formTabs', self.area);
    ul.tabs('div.panes > div', {
      onClick: function(evt, index){
        var api = this;
        var tab = this.getTabs()[index];
        jQuery(document).trigger(DavizEdit.Events.views.clicked, {
          index: index,
          tab: tab,
          api: api
        });
      }
    });

    // Make tabs sortable
    jQuery('li:not(#daviz-properties-header)', ul)
      .attr('title', 'Click and drag to change tabs order');
    ul.sortable({
      items: 'li.formTab:not(#daviz-properties-header)',
      placeholder: 'formTab ui-state-highlight',
      cursor: 'crosshair',
      tolerance: 'pointer',
      delay: 300,
      update: function(event, ui){
        var order = jQuery('li:not(#daviz-properties-header)', ul);
        self.sort(order, action);
      }
    });

    jQuery(document).bind(DavizEdit.Events.views.refreshed, function(evt, data){
      var index = data.currentTab || 0;
      var tab = data.tab;
      var tabs = jQuery('ul', self.area).data('tabs');
      if(tab){
        jQuery.each(tabs.getTabs(), function(i, item){
          if(jQuery(tab).attr('href') == jQuery(item).attr('href')){
            tabs.click(i);
            return false;
          }
        });
      }else{
        tabs.click(index);
      }
    });
  },

  sort: function(order, action){
    var self = this;
    var i = action.indexOf('@@');
    action = action.slice(0, i) + '@@daviz-edit.save';

    order = jQuery.map(order, function(item){
      return jQuery(item).attr('data-name');
    });

    var query = {
      'daviz.views.save': 'ajax',
      order: order
    };

    DavizEdit.Status.start('Saving ...');
    jQuery.ajax({
      traditional: true,
      type: 'post',
      url: action,
      data: query,
      success: function(data){
       DavizEdit.Status.stop(data);
      }
    });
  }
};

/** View settings
*/
DavizEdit.View = function(view){
  this.initialize(view);
};

DavizEdit.View.prototype = {
  initialize: function(view){
    var self = this;
    self.view = view;
    self.form = jQuery('form.daviz-view-form', self.view);
    if(!self.form.length){
      self.form = jQuery('form.daviz-view-form-disabled', self.view);
    }

    self.jsondata = jQuery('div.field:has(label[for=daviz.properties.json])', self.form);
    if(self.jsondata.length){
      var jsondata = new DavizEdit.JsonGrid(self.jsondata);
    }
    self.table = jQuery('div:has(label[for=daviz.properties.sources]) table', self.form);
    if(self.table.length){
      self.table.addClass('daviz-sources-table');
      var table = new DavizEdit.SourceTable(self.table);
    }


    self.form.submit(function(){
      return false;
    });

    self.buttons = jQuery('.actionButtons input[type=submit]', self.form)
      .addClass('btn')
      .click(function(){
        var button = jQuery(this);
        self.submit(button);
      });

    self.inputs = jQuery(':input', self.form).change(function(evt){
      jQuery('fieldset', self.form).addClass('changed');
    });

    self.style();
  },

  style: function(){
    // Add links to URLs
    var self = this;
    var help = jQuery('.formHelp', this.view);
    help.each(function(){
      var here = jQuery(this);
      var text = self.replaceURL(here.text());
      here.html(text);
    });
  },

  replaceURL: function(inputText) {
    var replacePattern = /(\b(https?|ftp):\/\/[\-A-Z0-9+&@#\/%?=~_|!:,.;]*[\-A-Z0-9+&@#\/%=~_|])/gim;
    return inputText.replace(replacePattern, '<a href="$1" target="_blank">here</a>');
  },

  submit: function(button){
    var self = this;
    var action = self.form.attr('action');
    var query = {};
    var array = self.form.serializeArray();

    jQuery.each(array, function(){
      if(query[this.name]){
        query[this.name].push(this.value);
      }else{
        query[this.name] = [this.value];
      }
    });

    var name = button.attr('name');
    query[name] = 'ajax';

    DavizEdit.Status.start('Saving ...');
    jQuery.ajax({
      traditional: true,
      type: 'post',
      url: action,
      data: query,
      success: function(data){
        jQuery('fieldset', self.form).removeClass('changed');
        button.removeClass('submitting');
        DavizEdit.Status.stop(data);
        if((name === 'daviz.properties.actions.save') || (name.indexOf('.enable') !== -1) || (name.indexOf('.disable') !== -1)){
          var currentTab = 0;
          var tabs = jQuery('.daviz-views-edit ul');
          var tab = null;
          if(tabs.length){
            tabs = tabs.data('tabs');
            currentTab = tabs.getIndex();
            tab = tabs.getCurrentTab();
          }

          jQuery(document).trigger(DavizEdit.Events.views.refresh, {
            init: false,
            action: action,
            currentTab: currentTab,
            tab: tab
          });
        }
      }
    });
  }
};

DavizEdit.JsonGrid = function(context){
  this.initialize(context);
};

DavizEdit.JsonGrid.prototype = {
  initialize: function(context){
    var self = this;
    self.context = context;
    self.context.addClass('daviz-jsongrid');

    self.textarea = jQuery('textarea', self.context).hide();
    self.textdialog = self.textarea.clone().width('98%').height('98%').show();
    self.textdialog.wrap('<div title="Edit JSON" />');
    self.textdialog.parent().dialog({
      bgiframe: true,
      autoOpen: false,
      modal: true,
      width: 600,
      dialogClass: 'daviz-confirm-overlay',
      close: function(evt, ui){
        DavizEdit.Status.start('Reloading table ...');
        self.textdialog.change();
        self.reload();
        DavizEdit.Status.stop('Done');
      }
    });

    self.textdialog.change(function(){
      self.textarea.val(self.textdialog.val());
    });

    self.gridview = jQuery('<div>')
      .addClass('daviz-data-table')
      .appendTo(self.context)
      .width(self.context.parents('.daviz-view-edit').width());

    self.relatedItems = {};
    var action = self.context.parents('form').attr('action');
    var i = action.indexOf('@@');
    action = action.slice(0, i) + '@@daviz.json';
    DavizEdit.Status.start('Loading ...');
    jQuery.getJSON(action, {}, function(data){
        self.relatedItems = data;
        self.reload();
        DavizEdit.Status.stop('Done');
      });

    // Events
    jQuery(document).bind(DavizEdit.Events.facet.changed, function(evt, data){
      self.save_header(data);
    });
  },

  reload: function(){
    var self = this;
    self.gridview.empty();
    self.table = jQuery('<table>').attr('id', 'jsontable').appendTo(self.gridview);
    self.pager = jQuery('<div>').attr('id', 'jsonpager').appendTo(self.gridview);

    var data = JSON.parse(self.textdialog.val());
    var colNames = Object.keys(data.properties || {});

    var dataTypes = {};
    jQuery.each(colNames, function(index, key){
      dataTypes[key] = data.properties[key].columnType || data.properties[key].valueType;
    });

    var colModel = jQuery.map(colNames, function(key, index){
      var label = jQuery('input[name=' + key + '.label]');
      label = label ? label.val() : key;
      return {
        name: key,
        label: label,
        index: key,
        editable: false,
        sortable: false,
        stype: 'select',
        edittype: "select",
        align: 'center',
        searchoptions: {
          defaultValue: dataTypes[key],
          dataEvents: [
            {'type': 'change', fn: function(e){
              var name = e.target.name;
              var value = jQuery(e.target).val();
              data.properties[name].columnType = value;
              self.textdialog.val(JSON.stringify(data, null, "  "));
              self.textdialog.change();
            }}
          ]
        },
        editoptions: {
          // XXX Get this list dynamically from the list of IGuessType utilities
          value: {
            'boolean': 'Boolean',
            'date': 'Date',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'latlong': 'LatLong',
            'list': 'List',
            'number': 'Number',
            'text': 'Text',
            'url': 'URL'
          }
        }
      };
    });

    self.table.jqGrid({
      datatype: "local",
      gridview: true,
      colModel: colModel,
      autowidth: true,
      rowNum: 10,
      rownumbers: true,
      pager: self.pager,
      editurl: '#',
      onSelectRow: function(id){
        return;
      },
      gridComplete: function(){
        var header = jQuery('.ui-jqgrid-sortable', self.gridview);
        header.attr('title', 'Click to edit');
        header.unbind('click');
        header.click(function(){
          self.edit_header(this);
        });
      }
    });

    // Populate table with remote data
    jQuery.each(self.relatedItems.items, function(index, item){
      if(index > 11){
        return false;
      }
      self.table.jqGrid('addRowData', index+1, item);
    });

    self.table.setGridParam({ rowNum: 6 }).trigger("reloadGrid");

    // Column types
    self.table.jqGrid('filterToolbar', {
      searchOnEnter: false,
      autosearch: false
    });

    // Table buttons
    self.table.jqGrid('navGrid', '#jsonpager', {
      refresh: false,
      edit: true,
      add: false,
      del: false,
      search: false,
      edittitle: 'Edit JSON',
      editfunc: function(index){
        self.textdialog.parent().dialog('open');
      }
    });
    self.gridview.delegate('#edit_jsontable', 'mouseover', function(){
      var row = self.table.jqGrid('getDataIDs')[0];
      self.table.jqGrid('setSelection', row);
    });
  },

  edit_header: function(header){
    var self = this;
    header = jQuery(header);
    var text = header.text();
    header.empty();
    var input = jQuery('<input>')
      .attr('type', 'text')
      .val(text)
      .appendTo(header)
      .focus()
      .blur(function(){
        header.text(jQuery(this).val());
      })
      .change(function(){
        var key = header.attr('id').replace('jqgh_jsontable_', '');
        jQuery(document).trigger(DavizEdit.Events.facet.changed, {
          key: key,
          value: jQuery(this).val()
        });
      });
  },

  save_header: function(options){
    var self = this;
    var header = jQuery('#jqgh_jsontable_' + options.key, self.gridview);
    header.text(options.value);
  }
};

DavizEdit.SourceTable = function(table){
  this.initialize(table);
};

DavizEdit.SourceTable.prototype = {
  initialize: function(table){
    var self = this;
    self.table = table;
    self.count = jQuery('input[name=daviz.properties.sources.count]', table.parent());

    self.button_add = jQuery('input[name=daviz.properties.sources.add]', table);
    self.button_add.click(function(){
      self.add(jQuery(this));
      return false;
    });

    self.button_remove = jQuery('input[name=daviz.properties.sources.remove]', table);
    if (!self.button_remove.length){
      self.button_remove = jQuery('<input>').attr('type', 'submit')
        .attr('name', 'daviz.properties.sources.remove')
        .val("Remove selected items");
      self.button_add.parent('td').prepend(self.button_remove);
    }

    self.button_remove.click(function(){
      self.remove(jQuery(this));
      return false;
    });

  },

  add: function(button){
    var self = this;
    button.removeClass('submitting');
    var count = parseInt(self.count.val(), 10);

    var check = jQuery('<input />').attr('type', 'checkbox')
      .addClass('editcheck')
      .attr('name', 'daviz.properties.sources.remove_' + count);
    var text = jQuery('<input />').attr('type', 'text').attr("value", "")
      .addClass('textType')
      .attr('name', 'daviz.properties.sources.' + count + '.');

    var td = jQuery('<td>').append(check).append(text);
    var row = jQuery('<tr>').append(td);

    self.table.prepend(row);

    count += 1;
    self.count.val(count);
  },

  remove: function(button){
    var self = this;
    button.removeClass('submitting');

    var checked = jQuery('input[type=checkbox]:checked', self.table);
    checked.each(function(){
      jQuery(this).parent().parent('tr').remove();
    });

    var count = parseInt(self.count.val(), 10);
    count -= checked.length;
    self.count.val(count);
  }
};


jQuery(document).ready(function(){
  DavizEdit.Status.initialize();
  DavizEdit.Confirm.initialize();
  DavizEdit.Facets.initialize();
  DavizEdit.Views.initialize();
});
