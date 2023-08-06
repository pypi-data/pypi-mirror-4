/**
*  tn menu builder adapted from
 * wpadmin navmenu.js
 */


/* helpers */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jq.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var tnMenuBuilder;

var tnmb = tnMenuBuilder = {

    options : {
      menuItemDepthPerLevel : 30, // Do not use directly. Use depthToPx and pxToDepth instead.
      globalMaxDepth : 11
    },

    menuList : undefined,  // Set in init.
    menuID : undefined,  // Set in init.
    targetList : undefined, // Set in init.
    menuItemModel : undefined, // Set in init.
    menuMainForm : undefined, // Set in init.
    tempIds: new Array(),  // to store  temporary new ids
    menusChanged : false,
    isRTL: !! ( 'undefined' != typeof isRtl && isRtl ),
    negateIfRTL: ( 'undefined' != typeof isRtl && isRtl ) ? -1 : 1,

    // Functions that run on init.
    __init__ : function() {
      tnmb.menuList = jq('#menu-to-edit');
      tnmb.deleteList = jq("#menu-to-delete");
      tnmb.targetList = tnmb.menuList;
      tnmb.menuID = jq('#menu-id').val();
      tnmb.menuItemModel = jq('#item-model');
      tnmb.menuMainForm = jq('#menu-edit-form');

      this.jQueryExtensions();
      this.attachMenuEditListeners();
      if( tnmb.menuList.length )
        this.initSortables();
    },

    jQueryExtensions : function() {
      // jQuery extensions
      jq.fn.extend({
        menuItemDepth : function() {
          var margin = tnmb.isRTL ? this.eq(0).css('margin-right') : this.eq(0).css('margin-left');
          return tnmb.pxToDepth( margin && -1 != margin.indexOf('px') ? margin.slice(0, -2) : 0 );
        },
        updateDepthClass : function(current, prev) {
          return this.each(function(){
            var t = jq(this);
            prev = prev || t.menuItemDepth();
            jq(this).removeClass('menu-item-depth-'+ prev )
              .addClass('menu-item-depth-'+ current );
          });
        },
        shiftDepthClass : function(change) {
          return this.each(function(){
            var t = jq(this),
              depth = t.menuItemDepth();
            jq(this).removeClass('menu-item-depth-'+ depth )
              .addClass('menu-item-depth-'+ (depth + change) );
          });
        },
        allChildItems : function() {
          var result = jq();
          this.each(function(){
            var t = jq(this), depth = t.menuItemDepth(), next = t.next();
            while( next.length && next.menuItemDepth() > depth ) {
              result = result.add( next );
              next = next.next();
            }
          });
          return result;
        },
        childItems : function() {
          var result = jq();
          this.each(function(){
            var t = jq(this), depth = t.menuItemDepth(), next = t.next();
            while( next.length && next.menuItemDepth() > depth ) {
              if (next.menuItemDepth() == depth+1)
                result = result.add( next );
              next = next.next();
            }
          });
          return result;
        },
        updatePositionData : function(i, pId){
          return this.each(function(){
            var that = this;
            jq('.menu-item-data-position', that).val(i+1);
            jq('.menu-item-data-parent_id', that).val(pId);
            pId = this.id.replace('menu-item-', '');
            jq(that).childItems().each( function(i) {
              jq(this).updatePositionData(i, pId) });
          });
        },
        // used to get uidata on each form
        getUIItemData : function() {
          var itemData = {};
          var id = this.find('.menu-item-data-id').val();
          if( !id ) return itemData;
          jq('input[type="text"], textarea', this).each(function() {
            data_key = jq(this).attr('name');
            value = jq(this).val();
            itemData[data_key]=value;
          });
          return itemData;
        },
        // used to reset uidata on each form
        setUIItemData : function( itemData ) {
          var id = jq('.menu-item-data-id', this).val();
          if( !id ) return this;
          if (typeof itemData == 'undefined') return this;
          jq('input[type="text"], textarea', this).each(function() {
            jq(this).val(itemData[jq(this).attr('name')]);
          });
          return this;
        },
        // setFinalData on item edit (close box)
        setFinalData: function(settings) {
          uidata = settings.data('menu-ui-item-data');
          for (var key in uidata) {
            jq('.final-data .menu-item-data-' + key, this).val(uidata[key]);
          }
          this.setLabel();
        },
        
        // store and display the new label on item edit
        setLabel : function() {
            var label  = jq('.menu-item-data-label', this);
            var label_original  = jq('.menu-item-data-label_original', this);
            var title  = jq('.menu-item-data-title', this);
            if (title.val()) label.val(title.val());
            // for target contents items retrieve the original label
            // when title is empty
            else label.val(label_original.val());
            jq('.item-title', this).text(label.val());
        }
      });
    },
    mainSubmit : function() {
      var form = tnmb.menuMainForm;
      jq('.menu-item-edit-active .item-edit', form).trigger('click');
      if (!jq('.ui-data .fieldWrapperWithError', form).length) {
          jq('.ui-data', form).remove();
          jq('.menu-item-data-label', form).remove();
          jq('.menu-item-data-label_original', form).remove();
          return true;
      }
      else return false;
    },
    initSortables : function() {
      var currentDepth = 0, originalDepth, minDepth, maxDepth,
        prev, next, prevBottom, nextThreshold, helperHeight, transport,
        menuEdge = tnmb.menuList.offset().left,
        body = jq('body'), maxChildDepth,
        menuMaxDepth = initialMenuMaxDepth();

      // Use the right edge if RTL.
      menuEdge += tnmb.isRTL ? tnmb.menuList.width() : 0;

      tnmb.menuList.sortable({
        handle: '.menu-item-handle',
        placeholder: 'sortable-placeholder',
        start: function(e, ui) {
          var height, width, parent, children, tempHolder;

          // handle placement for rtl orientation
          if ( tnmb.isRTL )
            ui.item[0].style.right = 'auto';

          transport = ui.item.children('.menu-item-transport');

          // Set depths. currentDepth must be set before children are located.
          originalDepth = ui.item.menuItemDepth();
          updateCurrentDepth(ui, originalDepth);

          // Attach child elements to parent
          // Skip the placeholder
          parent = ( ui.item.next()[0] == ui.placeholder[0] ) ? ui.item.next() : ui.item;
          children = parent.allChildItems();
          transport.append( children );

          // Update the height of the placeholder to match the moving item.
          height = transport.outerHeight();
          // If there are children, account for distance between top of children and parent
          height += ( height > 0 ) ? (ui.placeholder.css('margin-top').slice(0, -2) * 1) : 0;
          height += ui.helper.outerHeight();
          helperHeight = height;
          height -= 2; // Subtract 2 for borders
          ui.placeholder.height(height);

          // Update the width of the placeholder to match the moving item.
          maxChildDepth = originalDepth;
          children.each(function(){
            var depth = jq(this).menuItemDepth();
            maxChildDepth = (depth > maxChildDepth) ? depth : maxChildDepth;
          });
          width = ui.helper.find('.menu-item-handle').outerWidth(); // Get original width
          width += tnmb.depthToPx(maxChildDepth - originalDepth); // Account for children
          width -= 2; // Subtract 2 for borders
          ui.placeholder.width(width);

          // Update the list of menu items.
          tempHolder = ui.placeholder.next();
          tempHolder.css( 'margin-top', helperHeight + 'px' ); // Set the margin to absorb the placeholder
          ui.placeholder.detach(); // detach or jQuery UI will think the placeholder is a menu item
          jq(this).sortable( "refresh" ); // The children aren't sortable. We should let jQ UI know.
          ui.item.after( ui.placeholder ); // reattach the placeholder.
          tempHolder.css('margin-top', 0); // reset the margin

          // Now that the element is complete, we can update...
          updateSharedVars(ui);
        },
        stop: function(e, ui) {
          var children, depthChange = currentDepth - originalDepth;

          // Return child elements to the list
          children = transport.children().insertAfter(ui.item);

          // Update depth classes
          if( depthChange != 0 ) {
            ui.item.updateDepthClass( currentDepth );
            children.shiftDepthClass( depthChange );
            updateMenuMaxDepth( depthChange );
          }
          // Register a change
          tnmb.registerChange();
          // Update the item data.
          // XXX TODO : replace by a unik method refreshPosData
          tnmb.updateAllPositionsData();

          // address sortable's incorrectly-calculated top in opera
          ui.item[0].style.top = 0;

          // handle drop placement for rtl orientation
          if ( tnmb.isRTL ) {
            ui.item[0].style.left = 'auto';
            ui.item[0].style.right = 0;
          }

          // The width of the tab bar might have changed. Just in case.
          //tnmb.refreshMenuTabs( true );
        },
        change: function(e, ui) {
          // Make sure the placeholder is inside the menu.
          // Otherwise fix it, or we're in trouble.
          if( ! ui.placeholder.parent().hasClass('menu') )
            (prev.length) ? prev.after( ui.placeholder ) : tnmb.menuList.prepend( ui.placeholder );

          updateSharedVars(ui);
        },
        sort: function(e, ui) {
          var offset = ui.helper.offset(),
            edge = tnmb.isRTL ? offset.left + ui.helper.width() : offset.left,
            depth = tnmb.negateIfRTL * tnmb.pxToDepth( edge - menuEdge );
          // Check and correct if depth is not within range.
          // Also, if the dragged element is dragged upwards over
          // an item, shift the placeholder to a child position.
          if ( depth > maxDepth || offset.top < prevBottom ) depth = maxDepth;
          else if ( depth < minDepth ) depth = minDepth;

          if( depth != currentDepth )
            updateCurrentDepth(ui, depth);

          // If we overlap the next element, manually shift downwards
          if( nextThreshold && offset.top + helperHeight > nextThreshold ) {
            next.after( ui.placeholder );
            updateSharedVars( ui );
            jq(this).sortable( "refreshPositions" );
          }
        }
      });

      function updateSharedVars(ui) {
        var depth;

        prev = ui.placeholder.prev();
        next = ui.placeholder.next();

        // Make sure we don't select the moving item.
        if( prev[0] == ui.item[0] ) prev = prev.prev();
        if( next[0] == ui.item[0] ) next = next.next();

        prevBottom = (prev.length) ? prev.offset().top + prev.height() : 0;
        nextThreshold = (next.length) ? next.offset().top + next.height() / 3 : 0;
        minDepth = (next.length) ? next.menuItemDepth() : 0;

        if( prev.length )
          maxDepth = ( (depth = prev.menuItemDepth() + 1) > tnmb.options.globalMaxDepth ) ? tnmb.options.globalMaxDepth : depth;
        else
          maxDepth = 0;
      }

      function updateCurrentDepth(ui, depth) {
        ui.placeholder.updateDepthClass( depth, currentDepth );
        currentDepth = depth;
      }

      function initialMenuMaxDepth() {
        if( ! body[0].className ) return 0;
        var match = body[0].className.match(/menu-max-depth-(\d+)/);
        return match && match[1] ? parseInt(match[1]) : 0;
      }

      function updateMenuMaxDepth( depthChange ) {
        var depth, newDepth = menuMaxDepth;
        if ( depthChange === 0 ) {
          return;
        } else if ( depthChange > 0 ) {
          depth = maxChildDepth + depthChange;
          if( depth > menuMaxDepth )
            newDepth = depth;
        } else if ( depthChange < 0 && maxChildDepth == menuMaxDepth ) {
          while( ! jq('.menu-item-depth-' + newDepth, tnmb.menuList).length && newDepth > 0 )
            newDepth--;
        }
        // Update the depth class.
        body.removeClass( 'menu-max-depth-' + menuMaxDepth ).addClass( 'menu-max-depth-' + newDepth );
        menuMaxDepth = newDepth;
      }
    },

    generateTempId: function() {
      n = tnmb.tempIds.length+1;
      new_id = 'tempID' + n;
      tnmb.tempIds[n-1] = new_id;
      return new_id;
    },
    // inline validation for complete form or just a field
    validateInline: function(addBoxId, type, field) {
        var data = {};
        jq.ajaxSetup({
          async: false,
          beforeSend: function(xhr) {xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));}
        });
        if (typeof field=='undefined') {
          var form = jq('#'+ addBoxId);
          jq('input[type=text], input[type=hidden], textarea', form).each(
            function(){
              data[this.name] = jq(this).val();
            }
          );
          validate_url = home_url + 'menuitem/json/' + type + '/all/validate';
          jq.post(validate_url, data, function(result){
            jsondata = eval( "(" + result + ")" );
            success = jsondata.success;
            jq('.fieldWrapperWithError label .small', form).remove();
            jq('.fieldWrapper', form).removeClass('fieldWrapperWithError');
            if (!success) {
              errors = jsondata.errors;
              for (var i in errors) {
                field = jq("input[name=" + i + "], textarea[name=" + i + "]", form);
                fwrapper = field.parent();
                fwrapper.addClass('fieldWrapperWithError');
                jq('label', fwrapper).append('<span class="small">&nbsp;' + errors[i][0] + '</span>');
              }
            }
            else tnmb.addMenuItem(addBoxId, data, type);
          });
        }
        // single field validation
        else {
          fname = field.attr('name');
          data[fname] = field.val();
          validate_url = home_url + 'menuitem/json/' + type + '/' + fname + '/validate';
          jq.post(validate_url, data, function(result){
            jsondata = eval( "(" + result + ")" );
            success = jsondata.success;
            fwrapper = field.parent();
            jq('label .small', fwrapper).remove();
            fwrapper.removeClass('fieldWrapperWithError');
            if (!success) {
              errors = jsondata.errors;
              fwrapper.addClass('fieldWrapperWithError');
              jq('label', fwrapper).append('<span class="small">&nbsp;' + errors[fname][0] + '</span>');
            }
            // possible callback ...
          });
        }
    },
    
    newAddForm: function(form) {
        jq('input[type=text], textarea', form).val('');
        jq('input[name=link_url]', form).val('http://');
    },
    
    fillItemEditForm: function(data) {
        data['id'] = tnmb.generateTempId();
        data['position'] = 10000; //not important (updatePosition will set the good job)
        if ((typeof data['label']=='undefined' || ! data['label']) && data['title']) {
           data['label'] = data['title'];
           data['label_original'] = data['title'];
        }
        item_model = tnmb.menuItemModel.clone();
        menuitem = item_model.html();
        data_keys = ['id', 'label', 'label_original', 'title', 'description', 'link_url', 'target_id', 'view_path', 'position', 'type'];
        jq(data_keys).each(function(){
          if (typeof data[this]=='undefined') data[this]='';
        });
        for (var key in data) {
          var model_value = new RegExp("model-" + key, "g");
          menuitem = menuitem.replace(model_value, data[key]);
        }
        return menuitem;
    },
    
    addLinkItem: function() {
        // launch the validation and if success will add menu item
        tnmb.validateInline('add-custom-links', 'link');
    },
    addViewItem: function() {
        // launch the validation and if success will add menu item
        tnmb.validateInline('add-view', 'view');
    },
    addContentItem: function(cid) {
        // launch the validation and if success will add menu item
        tnmb.validateInline('content-target-'+cid, 'content');
    },
    // generic addMenuItem
    // each specific addItem method will insert a specific edit form cloned from add form
    addMenuItem: function(addBoxId, data, type) {
      box = jq('#' + addBoxId );
      uiform = jq('form', box).clone(true);
      jq('.postboxcontrol', uiform).remove();
      if (type=='content') {
        uicontentform = jq('#content-item-model-form', box.parents('.postbox')).clone(true);
        uiform.prepend(uicontentform.contents());
      }
      menuitem = jq(tnmb.fillItemEditForm(data));
      jq('.ui-data', menuitem).append(uiform.contents());
      jq('.final-data .menu-item-data-type', menuitem).val(type);
      // workaround a strange jquery bug on clone (text content of textarea are not copied - FF only bug)
      // http://bugs.jquery.com/ticket/3016
      jq('.ui-data textarea[name=description]', menuitem).val(data.description);
      menuitem.appendTo( tnmb.targetList );
      tnmb.validateOnChange(menuitem);
      tnmb.updateAllPositionsData();
      tnmb.registerChange();
      tnmb.newAddForm(jq('#' + addBoxId + ' form'));
    },

    registerChange : function() {
      tnmb.menusChanged = true;
      jq('#menu-id').trigger('change');
    },

    attachMenuEditListeners : function() {
      var that = this;
      tnmb.menuMainForm.bind('submit', function(e){
         if (!tnmb.mainSubmit()) return false;
      })
      jq('#menu-edit-form').bind('click', function(e) {
        if ( e.target && e.target.className ) {
          if ( -1 != e.target.className.indexOf('item-edit') ) {
            return that.eventOnClickEditLink(e, e.target);
          } else if ( -1 != e.target.className.indexOf('menu-delete') ) {
            return that.eventOnClickMenuDelete(e.target);
          } else if ( -1 != e.target.className.indexOf('item-delete') ) {
            return that.eventOnClickMenuItemDelete(e.target);
          } else if ( -1 != e.target.className.indexOf('item-cancel') ) {
            return that.eventOnClickCancelLink(e.target);
          }
        }
      });
      jq('#add-custom-links form').bind('submit', function(e){
          e.preventDefault();
          e.stopPropagation();
          tnmb.addLinkItem();
          return false;
      });
      jq('#add-view form').bind('submit', function(e){
          e.preventDefault();
          e.stopPropagation();
          tnmb.addViewItem();
          return false;
      });
      jq('.content-target a').bind('click', function(e){
          e.preventDefault();
          e.stopPropagation();
          cid = (jq(this).parent()).attr('id').replace('content-target-', '');
          tnmb.addContentItem(cid);
          return false;
      });
      jq('#menu-edit-form .menu-item').each(function(){
          tnmb.validateOnChange(this);
      });
    },

    eventOnClickEditLink : function(e, clickedEl) {
      e.preventDefault();
      var settings, item, matchedSection = clickedEl.id;
      eltid = matchedSection.replace('edit-', '');
      settings = jq('#menu-item-settings-'+ eltid);
      item = settings.parent();
      if( 0 != item.length ) {
        if( item.hasClass('menu-item-edit-inactive') ) {
          settings.data( 'menu-ui-item-data', settings.getUIItemData() );
          settings.slideDown('fast');
          item.removeClass('menu-item-edit-inactive')
            .addClass('menu-item-edit-active');
        } else {
            type = jq('.menu-item-data-type', settings).val();
            tnmb.editMenuItem(item);
        }
      }
      return false;
    },

    editMenuItem: function(item){
        jq('input[type=text], textarea', item).each(function(){this.blur()});
        if (!jq('.ui-data .fieldWrapperWithError', item).length) {
          settings = jq('.menu-item-settings', item);
          itemData = settings.getUIItemData();
          settings.data( 'menu-ui-item-data', itemData );
          item.setFinalData(settings);
          settings.hide();
          item.removeClass('menu-item-edit-active')
            .addClass('menu-item-edit-inactive');
        }
        else tnmb.onError();
        return false;
    },
    
    validateOnChange: function(item) {
        var type = jq('.menu-item-data-type', item).val();
        jq('input[type=text], textarea', item).change(function(){
            tnmb.validateInline('', type, jq(this));
        })
    },
    
    // improve
    onError: function() {
       alert('fix errors first');
    },

    eventOnClickCancelLink : function(clickedEl) {
      var settings = jq(clickedEl).closest('.menu-item-settings');
      settings.setUIItemData( settings.data('menu-ui-item-data') );
      jq('.fieldWrapperWithError label .small', settings).remove();
      jq('.fieldWrapper', settings).removeClass('fieldWrapperWithError');
      return false;
    },


    eventOnClickMenuDelete : function(clickedEl) {
      // Delete warning AYS
      if ( confirm( navMenuL10n.warnDeleteMenu ) ) {
        window.onbeforeunload = null;
        return true;
      }
      return false;
    },

    eventOnClickMenuItemDelete : function(clickedEl) {
      // XXX : TODO (JMG) use (improve) the twistranet confirm box
      var itemID = clickedEl.id.replace('delete-', '');
      tnmb.removeMenuItem( jq('#menu-item-' + itemID) );
      tnmb.registerChange();
      return false;
    },

    // if status == add (new item) just remove it
    // if status == edit (item exists in db) > change status && place elt in delete list
    removeMenuItem : function(el) {
      var state = jq('.menu-item-data-satus:first', el);
      var children = el.allChildItems();
      el.addClass('deleting').animate({
          opacity : 0,
          height: 0
        }, 350, function() {
          children.shiftDepthClass(-1);
          if (state.val()=='add') el.remove();
          else {
            state.val('delete');
            tnmb.deleteList.append(el);
          }
          tnmb.updateAllPositionsData();
        });
    },

    depthToPx : function(depth) {
      return depth * tnmb.options.menuItemDepthPerLevel;
    },

    pxToDepth : function(px) {
      return Math.floor(px / tnmb.options.menuItemDepthPerLevel);
    },

    updateAllPositionsData : function() {
        jq('.menu-item-depth-0', this.menuList).each(function(i) {
          jq(this).updatePositionData(i, tnmb.menuID);
        })
    }

};


jq(document).ready(function(){ tnMenuBuilder.__init__(); });

