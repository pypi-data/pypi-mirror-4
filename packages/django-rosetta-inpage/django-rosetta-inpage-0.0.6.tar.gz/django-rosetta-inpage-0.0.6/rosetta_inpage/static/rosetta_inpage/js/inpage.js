/***
 * Le JavaScript for Rosetta Inpage app.
 * Depends on jQuery.
 * https://github.com/citylive/django-rosetta-inpage
 *
 * Everything is wrapped in a closure to encapsulate all functionality. Public functionality is exposed in the end
 * of this file by assigning the Inpage object to the window object and expose it as RosettaInpage.
 *
 *
 * Ensure that jQuery and jQuery.form is loaded. If they're not loaded yet will do a document.write,
 * this is a blocking statement and will assure that both libraries are loaded before we include this javascript file.
 *
 * <script>!window.jQuery && document.write('<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"><' + '/script>');</script>
 * <script>!window.jQuery().ajaxForm && document.write('<script src="//cdnjs.cloudflare.com/ajax/libs/jquery.form/3.24/jquery.form.js"><' + '/script>');</script>
 */
(function(window, document){
    'use strict';

    // Define some constants
    var ROOT = '/rosetta_inpage',
        PREFIX = 'rosetta-inpage',
        ID_SIDEBAR = PREFIX + '-sidebar',
        ID_FORM = PREFIX + '-form'
    ;


    /**
     * Some internal references to DOM elements to have quick access
     */
    var $form, $alert, $sidebar, $loading, $notify;


    /**
     * Define the namespace. All functions in this namespace are public.
     */
    var Inpage = {};
    var Form = {};
    var Sidebar = {};


    function initDomElements(){
        $sidebar = $('#' + ID_SIDEBAR);
        $loading = $('#' + PREFIX + '-loading');

        $form = $('#' + ID_FORM);
        $alert = $form.find('.' + PREFIX + '-alert');
        $notify = $('#' + PREFIX + '-notify');
    }

    /**
     * Initialize all links in the sidebar.  When the user clicks on it the form to translate will appear
     */
    function initLinks(){
        var eventHandler = function(e){
            var pos = $(this).position();
            var width = $(this).outerWidth();

            var input = $form.find('input[name="source"]');
            var textarea = $form.find('textarea');

            var source = $(this).parent().find('code[type=source]').html();
            var msg = $(this).parent().find('code[type=msg]').html();

            var source_stripped = source.substring(4, source.length-3);
            var msg_stripped = msg.substring(4, msg.length-3);

            var current = $(this).parent();
            var next = current.next();
            $form.find('input[name=current]').val(current.attr('id'));
            $form.find('input[name=next]').val(next.attr('id'));

            Form.show();
            $form.css({
                'top': pos['top'],
                'left': pos['left'] + width
            });

            input.val(source_stripped);
            textarea.focus();
            textarea.val(msg_stripped);
            moveCursorToEnd(textarea);


            $sidebar.find('a').removeClass("active");
            $(this).addClass("active");
            e.stopPropagation();
        };

        $sidebar.find('.' + PREFIX + '-content  a').click(eventHandler);
    }


    /**
     * Attach ajax functionality to the translation form.
     * Depends on http://cdnjs.cloudflare.com/ajax/libs/jquery.form/3.24/jquery.form.js
     */
    function initForm(){
        var _onBeforeSubmit = function(data, jqForm, options){
            var source = $(jqForm).find('input[name="source"]').val();
            var msg = $(jqForm).find('textarea[name="msg"]').val();
            var valid_code = validateVariables(source, msg);


            if(valid_code == 200){
                $form.find('textarea').attr('disabled', 'disabled');
                $form.find('input[type=submit]')
                    .attr('value', 'Saving ...')
                    .attr('disabled', 'disabled');
                showLoading();
                return true;
            } else {
                if(404 === valid_code){
                    Form.showAlert('<strong>Major oopsie!</strong> The message can\'t be empty');
                } else {
                    Form.showAlert('<strong>Oh snap!</strong> Unmatched variables');
                }
                return false;
            }
        };

        var _onSuccess = function(responseText, statusText, xhr, jqForm){
            $form.find('textarea').removeAttr('disabled');
            $form.find('input[type="submit"]').attr('value', 'Save').removeAttr('disabled');

            $sidebar.find('.active').parent().removeClass('rosetta-inpage-todo');
            var currentId = $form.find('input[name=current]').val();
            var nextId = $(jqForm).find('input[name=next]').val();

            try{
                $('#' + nextId + ' a').trigger('click');
            }catch(e){
                //Its the last one
                $sidebar.find('a').removeClass("active");
                Form.hide();
            }
            $('#' + currentId + ' code[type=msg]').html('<!--' + responseText['msg'] + '-->');
            hideLoading();
        };

        var _onError = function(){
            Form.thaw();
            Form.showAlert('<strong>Oh No, George!</strong> Something terrible happened, contact a techie');
        };


        $form.find('textarea[name="msg"]').focus(Form.hideAlert);
        $form.find("form").ajaxForm({
            beforeSubmit: _onBeforeSubmit,
            success: _onSuccess,
            error: _onError
        });
    }


    /**
     * Configure general events and controls
     */
    function initPage(){
        $form.click(function(e){
            e.stopPropagation();
        });

        $sidebar.scroll(Form.hide);
        $(document).click(Form.hide);
        $(document).click(Sidebar.hide);
    }


    /**
     * Add hover in & out handlers for the sidebar
     */
    function initSidebar(){
        var origWidth = $sidebar.width();
        $sidebar._origWidth = origWidth;
        //$('#rosetta-inpage-sidebar').hover(Sidebar.show, Sidebar.hide);
        $('#rosetta-inpage-sidebar').hover(Sidebar.show);
    }


    /**
     * This is a nifty trick to place the cursor at the end of the text when the onfocus event is triggered
     * onfocus="var val=this.value; this.value=''; this.value= val;"
     * http://stackoverflow.com/questions/511088/use-javascript-to-place-cursor-at-end-of-text-in-text-input-element
     *
     * @param obj
     */
    function moveCursorToEnd(obj){
        var value = obj.val(); //store the value of the element
        $(obj).focus().val(value);
    }


    function showLoading(){
        //$('#' + PREFIX + '-loading').fadeIn('slow');
        //$('#' + PREFIX + '-loading').fadeIn();
        $loading.show();
    }


    function hideLoading(){
        //$('#' + PREFIX + '-loading').fadeOut('slow');
        //$('#' + PREFIX + '-loading').fadeOut();
        $loading.hide();
    }


    var PATTERN = /%(?:\([^\s\)]*\))?[sdf]/g;

    function validateVariables(source, newbie){
        if(!source || !newbie){
            return 404;
        }

        var matches_source = source.match(PATTERN);
        var matches_newbie = newbie.match(PATTERN);

        if(matches_source && matches_newbie && matches_source.length != matches_newbie.length){
            return 406;
        } else if((matches_source && !matches_newbie) || (!matches_source && matches_newbie)){
            return 406;
        }

        return 200;
    }

    function notify(message, type, disableHide){
        $notify.html(message);
        $notify.attr('class', PREFIX + '-notify ' + PREFIX + '-alert-' + type);
        $notify.fadeIn();
        $notify.unbind('click');

        if(!disableHide){
            var fadeOut = function(){$notify.fadeOut();};
            setTimeout(fadeOut, 6000);
            $notify.click(fadeOut);
        }
    }

    function isClickIn(e, parent){
        if(e.type !== "click"){
            return false;
        }

        var target = e.target ? e.target : e.srcElement;
        var result = false;

        while(target !== null && target !== parent){
            target = target.parentNode;
        }

        if(target === parent){
            result = true;
        }

        //console.log("Target " + target + ", " + e.type);
        //console.log("Parent " + parent + ", " + e.type);
        return result;
    }


    Form.show = function(){
        $form.show();
        $sidebar._freeze = true;
    };


    Form.hide = function(e){
        $form.hide();
        $sidebar.find('a').removeClass("active");
        $sidebar._freeze = false;
    };


    Form.freeze = function(){
        $form.find('textarea').attr('disabled', 'disabled');
        $form.find('input[type=submit]')
            .attr('value', 'Saving ...')
            .attr('disabled', 'disabled');
        showLoading();
    };


    Form.thaw = function(){
        $form.find('textarea').removeAttr('disabled');
        $form.find('input[type="submit"]').attr('value', 'Save').removeAttr('disabled');
        hideLoading();
    };


    Form.showAlert = function(message){
        $alert.html(message);
        $alert.show();
    };


    Form.hideAlert = function(){
        $alert.fadeOut('slow');
    };


    Sidebar.show = function(e){
        //$sidebar.stop(true).animate({width: origWidth + 'px'});
        $sidebar.css({width: $sidebar._origWidth + 'px'});
        $sidebar.find('>div').show();
        $sidebar.removeClass('wegermee');
    };


    Sidebar.hide = function(e){
        //console.log("D " + $sidebar._freeze);
        //console.log("E " + isClickIn(e, $sidebar[0]));
        //console.log($sidebar._freeze !== true );

        if($sidebar._freeze !== true && !isClickIn(e, $sidebar[0])){
            //console.log("patat");
            //$sidebar.stop(true).animate({width: '40px'});
            $sidebar.css({width: '0px'});
            $sidebar.find('>div').hide();
            $sidebar.addClass('wegermee');
        }
    };





    /**
     *
     */
    Inpage.init = function(){
        initDomElements();
        initLinks();
        initForm();
        initPage();
        initSidebar();
    };

    Inpage.reload = function(){
        showLoading();
        //window.location.reload();
        window.location.href = window.location.href;
        return false;
    };

    Inpage.view = function(locale){
        showLoading();
        var encoded = encodeURIComponent(window.location.href);
        if(!locale){
            locale = '';
        }
        window.location.href = ROOT + '/change-locale?page=' + encoded + '&locale=' + locale;
        return false;
    };

    Inpage.github = function(){
        showLoading();
        $.post(ROOT + "/ajax/github", function(data){
            hideLoading();
            //console.log(JSON.stringify(data));
            //alert(JSON.stringify(data));
            if(200 === data['status']){
                notify(data['message'], 'success');
            }else if(500 === data['status']){
                notify(data['message'], 'error', true);
            }else{
                notify(data['message'], 'info');
            }
        });
    };

    /**
     * Exposing functionality
     * Remapping Inpage to RosettaInpage
     */
    if(!window.RosettaInpage){
        window.RosettaInpage = Inpage;
    }
})(window, document);







//Deprecated
/*
$("span[contenteditable]").click(function(e){
    var text = $(this).html();
    var pos = $(this).position();
    var id = $(this).attr('id');

    console.log("Pos = " + JSON.stringify(pos) + ", " + id);
    $('#s-' + id).trigger('click');
    //$('#s-4a6a59aa75d28c79e8e9485d5019ddd9').trigger('click');
});

$("a").click(function(e){
    var id = $(this).attr('id');
    console.log("DDD = " + id);
    e.preventDefault();
});
*/

