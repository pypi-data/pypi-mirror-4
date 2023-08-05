/**
 * Based on django-fluent-contents
 * (c) 2011-2012 Diederik van der Boor, Apache 2 Licensed.
 *
 * Refactored as jQuery plugin at Leukeleu.
 */

(function($){
  "use strict";

  function DjangoInline(group, options) {
    this.group = group;
    this.$group = $(group);
    this.options = options;

    // Get FormSet settings
    this.auto_id             = options.autoId || 'id_{prefix}';
    this.pk_field_name       = options.pkFieldName || 'id';                                    // can be `tablename_ptr` for inherited models.
    this.prefix              = options.prefix || this.$group.attr('id').replace(/-group$/, '');  // typically the model name in lower case.

    // Allow to configure classes, but use django-admin defaults.
    this.items_selector      = options.itemsSelector || '.inline-related';
    this.item_id_template    = options.itemIdTemplate || '{prefix}-{index}';
    this.empty_form_selector = options.emptyFormSelector || '.empty-form';

    if( options.form_template )
      this.$form_template = $(options.form_template);
    else
      this.$form_template = this.$group.find(this.empty_form_selector);  // the extra item to construct new instances.

    var myself = this;
    this._newFormTarget = options.newFormTarget || function() { return myself.$group; };
  }

  DjangoInline.prototype = {

    addForm: function() {
      if(! this.$form_template || this.$form_template.length == 0)
        throw new Error("No empty form available. Define the 'form_template' setting or add an '.empty-form' element in the '" + this.prefix + "' formset group!")

      // The Django admin/media/js/inlines.js API is not public, or easy to use.
      // Recoded the inline model dynamics.
      var group_prefix = this._getGroupFieldIdPrefix();
      var $total = $("#" + group_prefix + "-TOTAL_FORMS");
      if($total.length == 0)
        throw new Error("Missing '" + $total.selector + "'. Make sure the management form included!");

      var container = this._newFormTarget.apply(this.group);
      if(container == null || container.length == 0)
        throw new Error("No container found via custom 'newFormTarget' function!");

      // Clone the item.
      var new_index = $total[0].value;
      var item_id   = this._getFormId(new_index)
      var newhtml = _getOuterHtml(this.$form_template).replace(/__prefix__/g, new_index);
      var newitem = $(newhtml).removeClass("empty-form").attr("id", item_id);

      // Add it
      container.append(newitem);
      var formset_item = $("#" + item_id);
      if( formset_item.length == 0 )
        throw new Error("New FormSet item not found: #" + item_id);

      formset_item.data('djangoInlineIndex', new_index);
      if(this.options.onAdd)
        this.options.onAdd.call(this.group, formset_item, new_index, this.options);

      // Update administration
      $total[0].value++;
      return formset_item;
    },

    _getFormId: function(index) {
      // The form container is expected by the numbered as #prefix-NR
      return this.item_id_template
        .replace('{prefix}', this.prefix)
        .replace('{index}', index);
    },

    getFormAt: function(index) {
      return $('#' + this._getFormId(index));
    },

    getFormIndex: function(child_node) {
      var dominfo = this._getItemData(child_node);
      return dominfo ? dominfo.index : null;
    },

    getForms: function() {
      // typically:  .inline-related:not(.empty-form)
      return this.$group.children(this.items_selector + ":not(" + this.empty_form_selector + ")");
    },

    getEmptyForm: function() {
      // typically:  #modelname-group > .empty-form
      return this.$form_template;
    },

    _getGroupFieldIdPrefix: function() {
      // typically:  #id_modelname
      return this.auto_id.replace('{prefix}', this.prefix);
    },

    getFieldIdPrefix: function(item_index) {
      if(! $.isNumeric(item_index)) {
        var dominfo = this._getItemData(item_index);
        if(dominfo == null)
          throw new Error("Unexpected element in getFieldIdPrefix, needs to be item_index, or DOM child node.");
        item_index = dominfo.index;
      }

      // typically:  #id_modelname-NN
      return this._getGroupFieldIdPrefix() + "-" + item_index;
    },

    getFieldsAt: function(index) {
      var $form = this.getFormAt(index);
      return this.getFields($form);
    },

    getFields: function(child_node) {
      // Return all fields in a simple lookup object, with the prefix stripped.
      var dominfo = this._getItemData(child_node);
      if(dominfo == null)
        return null;

      var fields = {};
      var $inputs = dominfo.formset_item.find(':input');
      var name_prefix = this.prefix + "-" + dominfo.index;

      for(var i = 0; i < $inputs.length; i++) {
        var name = $inputs[i].name;
        if(name.substring(0, name_prefix.length) == name_prefix) {
          var suffix = name.substring(name_prefix.length + 1);  // prefix-<name>
          fields[suffix] = $inputs[i];
        }
      }

      return fields;
    },

    _getItemData: function(child_node) {
      var formset_item = $(child_node).closest(this.items_selector);
      if( formset_item.length == 0 )
        return null;

      // Split the ID, using the id_template pattern.
      // note that ^...$ is important, as a '-' char can occur multiple times with generic inlines (inlinetype-id / app-model-ctfield-ctfkfield-id)
      var id = formset_item.attr("id");
      var cap = (new RegExp('^' + this.item_id_template.replace('{prefix}', '(.+?)').replace('{index}', '(\\d+)') + '$')).exec(id);

      return {
        formset_item: formset_item,
        prefix: cap[1],
        index: parseInt(cap[2])   // or parseInt(formset_item.data('djangoInlineIndex'))
      };
    },

    _getFormSetData: function(child_node) {
      var dominfo = this._getItemData(child_node);
      if( dominfo == null )
        return null;

      var group_prefix = this._getGroupFieldIdPrefix();
      var field_prefix = this.getFieldIdPrefix(dominfo.index);

      return $.extend({}, dominfo, {
        // management form item
        total_forms: $("#" + group_prefix + "-TOTAL_FORMS")[0],

        // Item fields
        pk_field: $('#' + field_prefix + '-' + this.pk_field_name),
        delete_checkbox: $("#" + field_prefix + "-DELETE")
      });
    },

    removeFormAt: function(index) {
      return this.removeForm(this.getForm(index));
    },

    removeForm: function(child_node)
    {
      // Get dom info
      var dominfo = this._getFormSetData(child_node);
      if( dominfo == null )
        throw new Error("No form found for the selector '" + child_node.selector + "'!");

      var total_count = parseInt(dominfo.total_forms.value);

      // Final check
      if( dominfo.pk_field.length == 0 )
        throw new Error("PK field not found for deleting objects!");

      if(this.options.onBeforeRemove)
        this.options.onBeforeRemove.call(this.group, dominfo.formset_item, this.options);

      // In case there is a delete checkbox, save it.
      if( dominfo.delete_checkbox.length )
      {
        dominfo.pk_field.remove().insertAfter(dominfo.total_forms);
        dominfo.delete_checkbox.attr('checked', true).remove().insertAfter(dominfo.total_forms);
      }
      else
      {
        // Newly added item, renumber in reverse order
        for( var i = dominfo.index + 1; i < total_count; i++ )
        {
          this._renumberItem(this.getFormAt(i), i - 1);
        }

        dominfo.total_forms.value--;
      }

      // And remove item
      dominfo.formset_item.remove();

      if(this.options.onRemove)
        this.options.onRemove.call(this.group, dominfo.formset_itemm, this.options);

      return dominfo.formset_item;
    },

    // Based on django/contrib/admin/media/js/inlines.js
    _renumberItem: function($formset_item, new_index)
    {
      var id_regex = new RegExp("(" + this._getFormId('(\\d+|__prefix__)') + ")");
      var replacement = this._getFormId(new_index);
      $formset_item.data('djangoInlineIndex', new_index);

      // Loop through the nodes.
      // Getting them all at once turns out to be more efficient, then looping per level.
      var nodes = $formset_item.add( $formset_item.find("*") );
      for( var i = 0; i < nodes.length; i++ )
      {
        var node = nodes[i];
        var $node = $(node);

        var for_attr = $node.attr('for');
        if( for_attr && for_attr.match(id_regex) )
          $node.attr("for", for_attr.replace(id_regex, replacement));

        if( node.id && node.id.match(id_regex) )
          node.id = node.id.replace(id_regex, replacement);

        if( node.name && node.name.match(id_regex) )
          node.name = node.name.replace(id_regex, replacement);
      }
    }
  };


  function _getOuterHtml($node)
  {
    if( $node.length )
    {
      if( $node[0].outerHTML )
        return $node[0].outerHTML;
      else
        return $("<div>").append($node.clone()).html();
    }
    return null;
  }


  // jQuery plugin definition
  // Separated from the main code, as demonstrated by Twitter bootstrap.
  $.fn.djangoInline = function(option) {
    var args = Array.prototype.splice.call(arguments, 1);
    var call_method = (typeof option == 'string');
    var plugin_result = (call_method ? undefined : this);

    this.filter('.inline-group').each(function() {
      var $this = $(this);
      var data = $this.data('djangoInline');

      if (! data) {
        var options = typeof option == 'object' ? option : {};
        $this.data('djangoInline', (data = new DjangoInline(this, options)));
      }

      if (typeof option == 'string') {
        plugin_result = data[option].apply(data, args);
      }
    });

    return plugin_result;
  };

  // Also expose inner object
  $.fn.djangoInline.Constructor = DjangoInline;

})(jQuery);
