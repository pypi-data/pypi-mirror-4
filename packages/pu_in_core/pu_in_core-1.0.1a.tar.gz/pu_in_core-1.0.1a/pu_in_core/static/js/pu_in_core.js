/**
 * pu.in core JS
 * =============
 *
 * As I said: core stuff. This JS lib provides bindings for
 * action-inline links, and submit-inline forms. In both cases the
 * action (action attr for forms, href for links) is handled by Ajax,
 * and the result is inserted in the current page.
 *
 * submit-inline 
 * ------------- 
 * Apply as class to a form, to enable inline submission. Result of
 * the action can be json, or html. In the first case, add a key
 * 'status' with the action result status (0 if ok), and resulting
 * html as 'html' key.  
 * Resulting html will be inserted in the target attribute of the form,
 * if that points to a valid id of an element within the current page.
 * Insert or replace depends on the pu_targetbehavior data attribute. 
 * Valid values are 'insert', 'replace', 'prepend' and 'append'. The default 
 * is to insert.
 *
 * action-inline
 * -------------
 * Class setting for inline actions. For result handling, see above. Specific 
 * case is where no target is given: default action is to replace the link 
 * itself. If pu_actionmethod is provided as attribute, the action will be 
 * requested through that method. Default is GET. If pu_actiondata is set, this
 * is regarded as a stringified number of parameter/value pairs to be sent as
 * data with the request.
 *
 * For both handlers: if pu_callback is provided as data attribute,
 * this JS function will be called on success. Any arguments to the
 * call may be provided by adding after a ':', for example
 * data-pu_callback="callMe:1". The originating element will always be
 * the first argument of the callback.
 *
 * modal-action-inline
 * -------------------
 * Handle action and show result in modal box.
 */

/* Some handy patches on JS */

// Add startsWith as method on String.
//
if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function(str) {
        return this.slice(0, str.length) == str;
    };
}


// Add endsWith as method on String.
//
if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function(str) {
        return this.slice(-str.length) == str;
    };
}

// pu_in namespace
if (pu_in == undefined) {
  var pu_in = {};
}


// Our own namespace
pu_in['core'] = {};

// Set to your modal and alert id if need be.
pu_in['settings'] = {modal_id: "#MyModal", alert_id: "#alerts"};


/**
 * Show message. Assumes a div with id 'status' in html.
 * @param mesg message
 * @param type type of alert. One of: success, error, info
 */
pu_in.core.showMessage = function(mesg, type) {

  $(pu_in.settings.alert_id).addClass("alert-" + type);
  $(pu_in.settings.alert_id).find(".alert-body").eq(0).html(mesg);
  $(pu_in.settings.alert_id).show("slow");

  setTimeout('pu_in.core.hideMessage()', 4000);
};


/**
 * Hide alert box.
 */
pu_in.core.hideMessage = function() {

  $(pu_in.settings.alert_id).hide("slow");
  $(pu_in.settings.alert_id).attr("class", "alert");  
  $(pu_in.settings.alert_id).find(".alert-body").html("");
}


/**
 * Show confirm window. If ok is clicked, call callback.
 * @param question Text to show
 * @param callback Callback to call when all is well...
 * @param callbackArgs List of callback arguments. These will be
 * provided to the callback function as arguments.
 */
pu_in.core.confirmMessage = function(question, callback, callbackArgs, okLabel, 
                                     cancelLabel) {
  
  $(pu_in.settings.modal_id + " .modal-body").html(
                                 question + 
                                 '<div class="btn-group"><a href="#" id="confirm_ok" class="btn btn-primary">' + (okLabel || "OK" ) + '</a>' +
                                 '<a href="#" class="btn" data-dismiss="modal">' + (cancelLabel || "Annuleren") + '</a></div>'
                                 );
  
  $(pu_in.settings.modal_id).find('#confirm_ok').click(function(event) {
      callback.apply({}, callbackArgs);
      $(pu_in.settings.modal_id).modal('hide');
    });
  
  $(pu_in.settings.modal_id).modal('show');     
};


pu_in.core.formatErrors = function(dict) {

  var errors = "<dl>";

  for (key in dict) {
    errors += "<dt>" + key + "</dt><dd>" + dict[key] + "</dd>";
  }

  return errors + "</dl>";
};


pu_in.core.detectContentType = function(xhr) {

  var ct = xhr.getResponseHeader("content-type") || "unknown";

  return ct;
};


/**
 * Determine the target for the given action. If it starts with '#',
 * it is supposed to be a local element, otherwise it it is not empty,
 * it is assumed to be a jquery selector that is evaluated on the
 * current element.
 * @param elt Element that triggered the action.
 */
pu_in.core.determineTarget = function(elt) {

  var tgt = elt.attr("target") || "";

  if (tgt.startsWith("#")) {
    tgt = $(tgt);
  } else if (tgt) {
    tgt = eval("elt." + tgt);
  }

  return tgt;
};


/**
 * Handle callback, if that attribute is set.
 * @param elt Element that triggered the action.
 */
pu_in.core.handleCallback = function(elt) {

  var callback = elt.data("pu_callback") || "";

  if (callback) {

    var callback_parts = callback.split(":");
    var callback_args = [elt];

    if (callback_parts.length > 1) {
      callback_args = callback_parts[1].split(",");
    }

    try {
      var callback = eval(callback_parts[0]);
      callback.apply(null, callback_args);
    } catch (e) {
      // handle errors please!
    }
  }                 
};


/**
 * Handle action result.
 * @param elt Element that triggered the action
 * @param data Result data
 * @param status Response status
 * @param xhr Result XHR
 */
pu_in.core.handleResult = function(elt, tgt, data, status, xhr, defaults) {

  defaults = defaults || {};

  var contentType = pu_in.core.detectContentType(xhr);
  var behavior = elt.data("pu_targetbehavior") || defaults.pu_targetbehavior;
  var html = data;

  if (contentType.indexOf("json") > -1) {

    html = data['html'];

    if (data['status'] != 0) {
      pu_in.core.showMessage(data['errors'], "error");
      return;
    }
  } else {
    html = data;
  }

  if (tgt) {
    if (behavior == "replace") {
      tgt.replaceWith(html);
    } else if (behavior == "append") {
      tgt.append(html);
    } else if (behavior == "prepend") {
      tgt.prepend(html);
    } else {
      tgt.html(html);
    }
  }

  if (data['message']) {

    pu_in.core.showMessage(data['message'], "success");
  }  
  
  if (elt.data("pu_protect")) {
    elt.removeClass("disabled");
  }

  pu_in.core.handleCallback(elt);
};


$(document).ready(function() {

    $(document).on("submit", ".submit-inline", function(e) {

        var form = $(e.target);
        var tgt = pu_in.core.determineTarget(form);
        
        if (form.data("pu_presubmit")) {
          try {
            check = eval(form.data("pu_presubmit"));
            if (!check(form)) {
              pu_in.core.showMessage("Kon data niet versturen", "error");
              return false;
            }
          } catch (e) {
            pu_in.core.showMessage("Kon data niet versturen: " + e, "error");
          }
        }

        $.ajax(form.attr("action"),
               {type: form.attr("method") || "POST",
                data: form.serialize(),
                success: function(data, status, xhr) {
                   pu_in.core.handleResult(form, tgt, data, status, xhr);
                 }
               });
        
        e.preventDefault();
      });

    $(document).on("click", ".action-inline", function(e) {
        
        var link = $(e.target);

        if (!link.hasClass("action-inline")) {
          link = link.parents(".action-inline");
        }

        if (!link.hasClass("disabled")) {

          if (link.data("pu_protect")) {
            link.addClass("disabled");
          }

          var tgt = pu_in.core.determineTarget(link) || link;

          $.ajax(link.attr("href"),
                 {type: link.data("pu_actionmethod") || "GET",
                     data: link.data("pu_actiondata") || "",
                     success: function(data, status, xhr) {
                     pu_in.core.handleResult(link, tgt, data, status, xhr, 
                                             {'pu_targetbehavior': 'replace'});
                   }
                 });
        }

        e.preventDefault();
      });

    $(document).on("click", ".modal-action-inline", function(e) {
        
        var link = $(e.target);

        if (!link.hasClass("modal-action-inline")) {
          link = link.parents(".modal-action-inline");
        }
      
        $.ajax(link.attr("href"), 
               {type: link.data("pu_actionmethod") || "GET",
                data: link.data("pu_actiondata") || "",
                   success: function(data, status, xhr) {

                     var contentType = pu_in.core.detectContentType(xhr);

                     if (contentType.indexOf("json") > -1) {          
                       $(pu_in.settings.modal_id + " .modal-body").html(data['html']);
                     } else {
                       $(pu_in.settings.modal_id + " .modal-body").html(data);
                     }
                     $(pu_in.settings.modal_id).modal();
                 }
               });
        e.preventDefault();
      });

    // hide modal on submit. If other handlers need to keep the modal,
    // make sure that the event is handled earlier in the 'bubble-up'
    // and stop propagation is called.
    //
    $(document).on("submit", pu_in.settings.modal_id, function(e) {

        $(pu_in.settings.modal_id).modal('hide');
      });
  });
  