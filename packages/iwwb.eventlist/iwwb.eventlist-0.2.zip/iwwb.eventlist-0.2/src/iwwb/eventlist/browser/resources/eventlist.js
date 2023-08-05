/*
 * Wrapper around jquery.load to allow cross domain calls
 *
 * If the browser does not support cross domain AJAX calls
 * we'll use a proxy function on the local server. For
 * performance reasons we do this only when absolutely needed.
 *
 * @param {String} url: String with an url to load (and optionally
 a selector)
 * @param {String} params: Arguments as a dictionary like object, passed to remote call
 * @param {Object} callback: A callback function that is executed when the request completes.
 *
 */
/*global document, jQuery, portal_url, pb */
(function ($) {
    "use strict";

    $.fn.loadUrl = function (url, params, callback) {

        // Split the url to the base url part and the selector
        var selector = url.split(" ")[1] || "";
        url = url.split(" ")[0];

        // if 'params' is a function
        if ($.isFunction(params)) {
            // we assume that it's the callback
            callback = params;
            params = undefined;
        }

        // go to our proxy view on a local server
        // and pass the orignal URL as a parameter
        params = params || {};
        params.url = url;
        params.remoteCharset = "ISO-8859-1";  // encoding of iwwb.de
        url = portal_url + "/@@proxy";
        this.load(url + " " + selector, params, callback);
    };

    $(document).ready(function () {

        var transform_anchor_to_text = function (sValue, iColumn) {
            /* transform anchor links to text links for exporting to formats like csv */
            if (sValue.indexOf('<a') !== -1) {
                var jsValue = $(sValue);
                return jsValue.text() + ', ' + jsValue.attr('href');
            }

            return sValue;
        };

        $("#example").dataTable({
            oLanguage: {"sUrl": "/++resource++iwwb.eventlist/dataTables.german.txt"},
            sDom: '<"num-results"i><"pagination"p>t<"clear">lfrT', // where in DOM to inject TableTools controls
            oTableTools: {
                sSwfPath: portal_url + "/++resource++jquery.datatables/extras/TableTools/media/swf/copy_cvs_xls.swf",
                aButtons: [
                    {
                        sExtends: "copy",
                        fnCellRender: transform_anchor_to_text
                    },
                    {
                        sExtends: "csv",
                        fnCellRender: transform_anchor_to_text
                    },
                    {
                        sExtends: "xls",
                        fnCellRender: transform_anchor_to_text
                    }
                ]
            },
            sPaginationType: "full_numbers",
            iDisplayLength: 25
        });

        $("a.training-supplier").overlay({
            onBeforeLoad: function () {

                // show the loading image
                pb.spinner.show();

                // grab the content container
                var wrap = this.getOverlay().find(".content-wrap");

                // load the page specified in the trigger and hide the loading
                // image
                wrap.loadUrl(
                    this.getTrigger().attr("href") + ' #content',
                    function () {
                        var content = $(this).children("#content"),
                            children = content.children();

                        // remove everything except h3 and div.anbieterinfos
                        $.each(children, function (index, child) {
                            var $child = $(child);
                            if (!$child.is("h3")
                                    && $child.attr("class") !== "anbieterinfos") {
                                $child.remove();
                            }
                        });

                        // hide the loading image
                        pb.spinner.hide();
                    }
                );
            }
        });

    });
}(jQuery));


/* code for the overlay containing area code picker */
(function ($) {
    "use strict";

    var currCodes = [],   // list of currently selected area codes
        $txtCodes;        // textarea displaying currently selected area codes

    // If area code has already been selected, remove it from the list,
    // otherwise add it. Update textarea content at the end.
    function areaClicked(code) {
        var idx = $.inArray(code, currCodes);

        if (idx > -1) {
            currCodes.splice(idx, 1);
        } else {
            currCodes.push(code);
            currCodes = currCodes.sort();
        }

        $txtCodes.val(currCodes.join(", "));
    }

    $(document).ready(function () {
        $txtCodes = $("#txtCodes");

        // set onclick handlers for all area elements
        $("#germany_map area").each(function () {
            var code = $(this).attr("alt").split(" ")[1];

            $(this).click(function (event) {
                event.preventDefault();
                areaClicked(code);
            });
        });

        // init area code picker overlay
        $("#zipcode-trigger").overlay({
            top: 0,
            closeOnClick: false,
            close: "#btnCancel, #overlay-zipcode .close",

            onBeforeLoad: function () {
                // reset area codes list
                currCodes = [];
                $txtCodes.val(currCodes.join(", "));
            }
        });

        $("#btnDone").click(function () {
            $("#form-widgets-zipcity").val(currCodes.join(", "));
            $("#zipcode-trigger").data("overlay").close();
        });
    });

}(jQuery));
