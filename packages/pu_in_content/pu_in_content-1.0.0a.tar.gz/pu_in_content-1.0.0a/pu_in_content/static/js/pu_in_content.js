/**
 * pu.in content library. This library takes care of frontend content
 * editing.
 * This JS enables inline add, remove and edit.
 *
 * Inline add
 * ----------
 * Add class 'add-inline' to your link tag.
 *
 */

// pu_in namespace
if (pu_in == undefined) {
  var pu_in = {};
}

// Our own namespace
pu_in['content'] = {};


/**
 * Remove the element that is the '.editable' parent of the event's
 * target.
 */
pu_in.content.remove_inline = function(tgt) {

  var callback = null;

  if (tgt.data("pu_callback")) {
    callback = eval(tgt.data("pu_callback"));
  }

  $.post(tgt.attr("href"),
{},
         function(data) {           
           if (data['status'] != 0) {
             pu_in.core.showMessage(data['errors'], "error");
           } else {
             tgt.parents(".editable").eq(0).remove();
             try {
               callback();
             } catch (e) {
               // handle errors please!
             }
           }
         });
};


/**
 * Edit inline. If the href is a link to an id, show that id (assuming
 * it is the edit form), else fetch the link and show that in the
 * modal box.
 * @param tgt Target link.
 */
pu_in.content.edit_inline = function(tgt) {

  var target = null;
  var defaults = {};

  if (tgt.attr("target")) {
    target = $(tgt.attr("target"));
  } else {
    target = tgt.parents(".editable").eq(0);
    defaults['pu_targetbehavior'] = 'replace';
  }

  if (tgt.attr("href").startsWith("#")) {
    $(tgt.attr("href")).show();
  } else {
    $.get(tgt.attr("href"), function(data, status, xhr) {

        var contentType = pu_in.core.detectContentType(xhr);

        if (contentType.indexOf("json") > -1) {          
          $(pu_in.settings.modal_id + " .modal-body").html(data['html']);
        } else {
          $(pu_in.settings.modal_id + " .modal-body").html(data);
        }
        
        // Bind submit
        $(pu_in.settings.modal_id).on("submit.pu_in_content", "form", function(e) {

            var form = $(e.target);

            $.post(form.attr("action"),
                   form.serialize(),
                   function(data, status, xhr) {
                     if (data['status'] != 0) {
                       $(pu_in.settings.modal_id + " .modal-body").html(data['html']);
                     } else {
                       pu_in.core.handleResult(tgt, target, data, status, xhr, 
                                               defaults);
                       $(pu_in.settings.modal_id).modal('hide'); 
                     }
                   });

            e.preventDefault();
            e.stopPropagation();
          });

        $(pu_in.settings.modal_id).modal();
      });
  }
};


/**
 * Add inline. This involves either showing an existing add form, or
 * fetching it from remote.
 * @param tgt Target link.
 */
pu_in.content.add_inline = function(tgt) {

  var target = tgt.attr("target") ? $(tgt.attr("target")) : null;
  var defaults = {'pu_targetbehavior': 'append'};

  if (tgt.attr("href").startsWith("#")) {
    $(tgt.attr("href")).show();
  } else {
    $.get(tgt.attr("href"), function(data) {

        // todo : propert content type check
        
        $(pu_in.settings.modal_id + " .modal-body").html(data['html']);

        $(pu_in.settings.modal_id).on("submit.pu_in_content", "form", function(e) {

            var form = $(e.target);

            $.post(form.attr("action"),
                   form.serialize(),
                   function(data, status, xhr) {
                     if (data['status'] != 0) {
                       $(pu_in.settings.modal_id + " .modal-body").html(data['html']);
                     } else {
                       pu_in.core.handleResult(tgt, target, data, status, xhr, 
                                               defaults);
                       $(pu_in.settings.modal_id).modal('hide');
                     }
                   });

            e.preventDefault();
            e.stopPropagation();

          });
        $(pu_in.settings.modal_id).modal('show');        
      });
  }
}


/**
 * Handle submission of the add form. Rebind submit to self.
 * @param form Form to submit
 * @param add_to Element to add result to
 */
pu_in.content._handle_add_submit = function(link, form, add_to) {

  return false;
};


// Initialize pu_in.content
//
$(document).ready(function() {

    $(document).on("click", ".rm-inline", function(event) {

        var tgt = $(event.target);

        if (!tgt.hasClass("rm-inline")) {
          tgt = tgt.parents(".rm-inline");
        }

        if (!tgt.hasClass("disabled")) {
          if (tgt.data("pu_confirmdelete")) {
            pu_in.core.confirmMessage("Weet je zeker dat je dit item wilt verwijderen?",
                                      
                                      pu_in.content.remove_inline, [tgt]);
          } else {
            pu_in.content.remove_inline(tgt);
          }
        }

        event.preventDefault();        
      });

    $(document).on("click", ".edit-inline", function(event) {

        var tgt = $(event.target);

        if (!tgt.hasClass("edit-inline")) {
          tgt = tgt.parents(".edit-inline");
        }

        if (!tgt.hasClass("disabled")) {
          pu_in.content.edit_inline(tgt);
        }

        event.preventDefault();
      });

    $(document).on("click", ".add-inline", function(event) {

        var tgt = $(event.target);

        if (!tgt.hasClass("add-inline")) {
          tgt = tgt.parents(".add-inline");
        }

        if (!tgt.hasClass("disabled")) {
          pu_in.content.add_inline(tgt);
        }

        event.preventDefault();
      });

    // Clean up bind after use
    $(pu_in.settings.modal_id).on('hide', function () {
        $(pu_in.settings.modal_id).off("submit.pu_in_content");
      });
  });
