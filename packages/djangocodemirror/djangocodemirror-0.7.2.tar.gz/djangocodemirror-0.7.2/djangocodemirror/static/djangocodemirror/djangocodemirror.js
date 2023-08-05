/*
* Django-CodeMirror jQuery plugin
*/
(function($){


/*
 * Plugin methods calling logic
 */
$.fn.djangocodemirror = function(method) {
    if ( methods[method] ) {
        return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
        return methods.init.apply( this, arguments );
    } else {
        $.error( 'Method ' +  method + ' does not exist on jQuery.djangocodemirror' );
    }
};


/*
 * Plugin methods
 */
var methods = {
    /*
     * Initialize plugin, must be called first
     */
    init : function(options) {
        // Default editor settings
        var settings = $.extend( {
            // Default settings to edit without any tab character and allways use 4 
            // spaces instead
            "indentUnit": 4,
            "tabSize": 4,
            "indentWithTabs": false,
            // To enable the automatic line wrapping
            "lineWrapping": false,
            // To display line numbers
            "lineNumbers": false,
            // For DjangoCodeMirror only
            "fullscreen": true,
            "help_link": '',
            "enable_active_line": true,
            "display_cursor_position": true,
            "undo_buttons": true,
            // Used by some features
            "csrf": false,
            // For the preview feature
            "preview_url": false,
            // For the quicksave feature
            "quicksave_url": '',
            "quicksave_datas": {},
            // For the editor settings feature
            "settings_cookie": '',
            "settings_url": '',
            // Deprecated?
            "preview_padding": 10,
            "preview_borders": 0
        }, options);
        // Default button settings
        var default_button_settings = {
            "name" : '',
            "funcname" : 'common',
            "method" : 'syntax',
            "classname" : '',
            "key" : false,
            "char" : false,
            "url" : false,
            "placeholder" : '',
            "begin_with" : false,
            "close_with" : false,
            "move_cursor_char" : 0,
            "separator" : false
        };
        
        // Build DjangoTribune for each selected element
        return this.each(function() {
            // Update settings from these saved in cookie, if any
            if(settings.settings_cookie) {
                var cookie = $.cookies.get("djangocodemirror_user_settings");
                if(cookie){
                    settings = $.extend(settings, cookie);
                }
            }
            
            var input_source = $(this), // allway the input source from where is created djangocodemirror
                djangocodemirror_key = "djangocodemirror-id-" + (input_source.attr('id')||'default'), // djangocodemirror instance ID
                container = $("<div class=\"DjangoCodeMirror\"></div>"),
                header = $("<div class=\"DjangoCodeMirror_menu\"><ul></ul><div class=\"cale\"></div></div>"),
                footer = $("<div class=\"DjangoCodeMirror_tabs\"><ul></ul><div class=\"cale\"></div></div>"),
                tab_preview_on = $("<li class=\"tab preview\"><a>"+safegettext("Preview")+"</a></li>"),
                tab_preview_off = $("<li class=\"tab editor tabactive\"><a>"+safegettext("Edit")+"</a></li>"),
                cursorpos_element = "<div class=\"cursor_pos\">"+safegettext("Line")+"&nbsp;:&nbsp;<span class=\"line\">1</span> &nbsp;&nbsp; "+safegettext("Col")+"&nbsp;:&nbsp;<span class=\"ch\">1</span></div>";
            
            // Append container, append its menu header, move the input in the container
            $(this).before(container);
            header.appendTo(container);
            $(this).appendTo(container);
            
            // Build tabs and status bar
            if(settings.preview_url || settings.display_cursor_position) {
                footer.appendTo(container);
                if(settings.preview_url) {
                    tab_preview_off.appendTo(".DjangoCodeMirror_tabs ul", container);
                    tab_preview_on.appendTo(".DjangoCodeMirror_tabs ul", container);
                }
                if(settings.display_cursor_position) {
                    $(".DjangoCodeMirror_tabs .cale", container).before(cursorpos_element);
                }
            }
            
            // Update settings to append the cursor activy function
            settings["onCursorActivity"] = function() { events.cursor_activity(input_source) };
            
            // Build CodeMirror
            var codemirror_instance = CodeMirror.fromTextArea(this, settings);
            // Force options in codemirror that it doesn't know of
            codemirror_instance.setOption('extraKeys', {
                "Tab": "indentMore", 
                "Shift-Tab": "indentLess",
                // WARNING: Ctrl/Cmd prefix should be determined from the enabled default 
                //       keymap (because on MacOS it should be Cmd and not Ctrl)
                "Ctrl-S": function(cm){ cm.save(); $('.buttonQuickSave').trigger('click'); }
                // NOTE: Here should be defined syntax button keybinding from there key attribute
            });
            
            // Attach element's data
            input_source.data("djangocodemirror", {
                "key" : djangocodemirror_key,
                "container" : container,
                "codemirror" : codemirror_instance,
                "settings": settings
            });
            
            // Build buttons bar
            var buttons = coreutils.buttons_preprocessing(settings, DCM_Buttons_settings);
            $.each(buttons, function(item_index, item_value) {
                if(item_value) {
                    var button_settings = $.extend({}, default_button_settings, item_value);
                    if(button_settings.separator) {
                        input_source.djangocodemirror('add_bar_separator', container)
                    } else {
                        input_source.djangocodemirror('add_bar_button', button_settings)
                    }
                }
            });
            
            // Bind events
            if(settings.preview_url) {
                tab_preview_on.on("click", { "input_source": input_source }, events.show_preview);
                tab_preview_off.on("click", { "input_source": input_source }, events.hide_preview);
            }
            
            // Default active line
            if(settings.enable_active_line){
                input_source.data("codemirror_hlLine", codemirror_instance.setLineClass(0, "activeline"));
            }
            
            // Refresh update of CodeMirror
            codemirror_instance.refresh();
        });
    },
 
 
    /*
    * Add separator in buttons bar 
    */
    add_bar_separator: function(direction) {
        return this.each(function(){
            var input_source = $(this),
                instance_data = input_source.data("djangocodemirror");
            
            if(!direction || direction=='horizontal') {
                $('<li class="separator horizontal">-----</li>').appendTo(".DjangoCodeMirror_menu ul", instance_data.container);
            } else {
                $('<li class="separator vertical">-----</li>').appendTo(".DjangoCodeMirror_menu ul", instance_data.container);
            }
        });
    },
 
 
    /*
    * Add button to the bar
    */
    add_bar_button: function(button_settings) {
        return this.each(function(){
            var input_source = $(this),
                instance_data = input_source.data("djangocodemirror"),
                accesskey = (button_settings.key) ? ' accesskey="'+button_settings.key+'"' : '',
                button = $('<li class="button '+button_settings.classname+'"><a'+accesskey+' title="'+safegettext(button_settings.name)+'">'+safegettext(button_settings.name)+'</a></li>');
            
            button.appendTo('.DjangoCodeMirror_menu ul', instance_data.container);
            if(button_settings.method == 'internal') {
                button.on("click", { "input_source":input_source, "button_element":button, "button_settings":button_settings }, events[button_settings.funcname]);
            } else {
                button.on("click", { "input_source":input_source, "button_element":button, "button_settings":button_settings }, events.button_click);
            }
        });
    }
};


/*
 * Plugin event methods
 */
var events = {
    /*
     * Set some marks and do some computing for each cursor activity
     * NOTE: this is heavily called because the cursor activity is constantly used,
     *       so there should be improvements in this code to speed up things
     */
    cursor_activity: function(input_source) {
        var instance_data = input_source.data("djangocodemirror"),
            cur = instance_data.codemirror.getCursor();
        // Reset previous highlighted lines
        if(instance_data.settings.enable_active_line){
            var hlLine = input_source.data("codemirror_hlLine");
            instance_data.codemirror.setLineClass(hlLine, null);
        }
        // Update column and row counters
        $(".DjangoCodeMirror_tabs .cursor_pos span.line", instance_data.container).html((cur.line+1));
        $(".DjangoCodeMirror_tabs .cursor_pos span.ch", instance_data.container).html((cur.ch+1));
        // Update the undo/redo buttons class from history items
        var histo = instance_data.codemirror.historySize();
        if(histo.undo>0) {
            $(".DjangoCodeMirror_menu .buttonUndo", instance_data.container).addClass("active").removeClass("inactive");
        } else {
            $(".DjangoCodeMirror_menu .buttonUndo", instance_data.container).addClass("inactive").removeClass("active");
        }
        if(histo.redo>0) {
            $(".DjangoCodeMirror_menu .buttonRedo", instance_data.container).addClass("active").removeClass("inactive");
        } else {
            $(".DjangoCodeMirror_menu .buttonRedo", instance_data.container).addClass("inactive").removeClass("active");
        }
        // Update the highlight
        if(instance_data.settings.enable_active_line){
            input_source.data("codemirror_hlLine", instance_data.codemirror.setLineClass(cur.line, "activeline"));
        }
    },
    /*
     * Handle click on common button (aka using the public syntax methods)
     */
    button_click: function(event) {
        var input_source = $(event.data.input_source),
            button_settings = event.data.button_settings,
            instance_data = input_source.data("djangocodemirror");
        
        if(button_settings.placeholder) {
            button_settings.placeholder = safegettext(button_settings.placeholder);
        }
        // Get the content value if not empty, else use the placeholder value
        var value = instance_data.codemirror.getSelection()||button_settings.placeholder;
        // Evaluate method
        // TODO: should not use a constant for methods object container
        eval("DCM_Syntax_Methods."+button_settings.funcname)(value, instance_data.codemirror, button_settings);
        // Put the cursor after the updated content
        instance_data.codemirror.setCursor(instance_data.codemirror.getCursor());
        // Restore focus after action
        instance_data.codemirror.focus();
        
        return false;
    },
    
    /*
     * Send a quick save request to the dedicated view
     */
    content_quicksave: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
        
        // If it's a string, assume that this is the variable name where there is the 
        // object {} to use
        if( jQuery.type(instance_data.settings.quicksave_datas)=='string' ){
            try {
                instance_data.settings.quicksave_datas = eval(instance_data.settings.quicksave_datas);
            } catch (e) {
                instance_data.settings.quicksave_datas = {};
            }
        }
        // Do Ajax POST request to quicksave view
        $.ajax({
            type: 'POST',
            dataType: "json",
            global: false,
            url: instance_data.settings.quicksave_url,
            data: $.extend({}, instance_data.settings.quicksave_datas, {
                "nocache": (new Date()).getTime(),
                "content": instance_data.codemirror.getValue()
            }),
            beforeSend: function(xhr, settings) {
                if(instance_data.settings.csrf) {
                    eval(instance_data.settings.csrf)(xhr, settings);
                }
            },
            success: function(data) {
                $(".DjangoCodeMirror_menu .buttonQuickSave", instance_data.container).removeClass("ready");
                $(".DjangoCodeMirror_menu .buttonQuickSave", instance_data.container).removeClass("error");
                if(data['status']=='form_invalid') {
                    $(".DjangoCodeMirror_menu .buttonQuickSave", instance_data.container).addClass("error");
                    createGrowl(instance_data.container, "warning", safegettext("Validation error"), data["errors"]["content"].join("<br/>"), false);
                } else {
                    createGrowl(instance_data.container, "success", safegettext("Success"), safegettext("Successful save"), false);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $(".DjangoCodeMirror_menu .buttonQuickSave", instance_data.container).removeClass("ready");
                $(".DjangoCodeMirror_menu .buttonQuickSave", instance_data.container).addClass("error");
                createGrowl(instance_data.container, "warning", textStatus, errorThrown, false);
            }
        });
        return false;
    },
 
    /*
     * Maximize editor size
     */
    maximize_editor: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
        
        $("body","html").css({'height':"100%", 'width':"100%"});
        $("html").css('overflow',"hidden");
        
        instance_data.container.addClass("fullScreen");
        // Build new scene where will be moved the editor in maximized size and add a 
        // empty container to mark the initial editor position
        var scene = $('<div>').attr('id', "DjangoCodeMirror_fullscreen_scene");
        var old_place_scene = $('<div>').attr('id', "DjangoCodeMirror_old_place");
        
        // Save initial editor size to restore after exiting the maximized mode
        $(".CodeMirror-scroll", instance_data.container).data('original_size', $(".CodeMirror-scroll", instance_data.container).height());
        
        // Catch and use the ESC key to exit from the maximized mode
        $(scene).keydown( function(e){
            if(e.keyCode == '27'){
                events.normalize_editor(event);
                //events.hide_preview(event);
                return false;
            }
            return true;
        });
        
        // Ajoute de la nouvelle scène dans le html à la fin du <body/> et déplace 
        // l'éditeur dedans
        instance_data.container.after(old_place_scene);
        instance_data.container.appendTo(scene);
        $("body").append(scene);
        
        // Calcul et applique les nouvelles dimensions
        var elems_css = coreutils.get_fullscreen_sizes(input_source);
        scene.css(elems_css[0]).attr('id', "DjangoCodeMirror_fullscreen_scene");
        instance_data.container.css("width", "100%");
        // Met la hauteur de CodeMirror à la dimension qui lui est disponible
        $(".CodeMirror-scroll", instance_data.container).css(elems_css[1]);
        events.hide_preview(event);
        // Recalcul auto de CodeMirror
        instance_data.codemirror.refresh();
        // Resize
        $(window).bind("resize.djc_maximize", { "input_source": input_source }, events.resize_editor);
    },
    /*
     * Exit maximized mode
     */
    normalize_editor: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
        
        // Don't try to re-init all the thing if there are no displayed maximized editor
        if ($("#DjangoCodeMirror_fullscreen_scene").length==0){
            return;
        }
        instance_data.container.removeClass("fullScreen");
        
        // Replace l'éditeur à son ancienne position (juste avant la balise dédiée à 
        // cet effet)
        $("#DjangoCodeMirror_old_place").before(instance_data.container)
        $("#DjangoCodeMirror_old_place").remove();
        
        // Retire le hack anti-scroll et vire la scène fullscreen
        $("body","html").css({"height":'', "width":''});
        $("html").css("overflow", 'auto');
        $("#DjangoCodeMirror_fullscreen_scene").remove();
        
        // Restitue les dimensions originals
        instance_data.container.css("width", '');
        $(".CodeMirror-scroll", instance_data.container).css(
            "height",
            $(".CodeMirror-scroll", instance_data.container).data('original_size') + "px"
        );
        events.hide_preview(event);
        $(window).unbind("resize.djc_maximize");
        instance_data.codemirror.refresh();
    },
    resize_editor: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror"),
            elems_css = coreutils.get_fullscreen_sizes(input_source);
        $("#DjangoCodeMirror_fullscreen_scene").css(elems_css[0]);
        $(".CodeMirror-scroll", instance_data.container).css(elems_css[1]);
        instance_data.codemirror.refresh();
    },
    
    /*
     * undo/redo management
     */
    do_undo: function(event) {
        var input_source = $(event.data.input_source),
            button_element = event.data.button_element,
            instance_data = input_source.data("djangocodemirror");
        
        if(button_element.hasClass("active")) {
            instance_data.codemirror.undo();
        }
    },
    do_redo: function(event) {
        var input_source = $(event.data.input_source),
            button_element = event.data.button_element,
            instance_data = input_source.data("djangocodemirror");
        
        if(button_element.hasClass("active")){
            instance_data.codemirror.redo();
        }
    },
    
    /*
     * Send a preview request and display the rendered content
     */
    show_preview: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
        
        // Don't add a new preview it if another one is allready displayed
        if (instance_data.container.data("DCM_preview_markid")){
            return;
        }
        // Clean previous error markers
        $(".DjangoCodeMirror_tabs li.preview a .error", instance_data.container).remove();
        // Do Ajax POST request to preview view
        $.ajax({
            type: 'POST',
            dataType: "html",
            global: false,
            url: instance_data.settings.preview_url,
            data: {
                "nocache": (new Date()).getTime(),
                "content": instance_data.codemirror.getValue()
            },
            beforeSend: function(xhr, settings) {
                if(instance_data.settings.csrf) {
                    eval(instance_data.settings.csrf)(xhr, settings);
                }
            },
            success: function(data) {
                var elems_css = coreutils.get_preview_sizes(input_source);
                // ID unique du conteneur de la preview à lier au conteneur de SPM
                var preview_id = "DCM_preview_id_"+$.now();
                instance_data.container.data("DCM_preview_markid", preview_id);
                
                // Scène principal par dessus l'éditeur
                var scene = $("<div>").css(elems_css[0]);
                scene.addClass("DjangoCodeMirrorPreviewScene")
                scene.attr("id", preview_id);
                $("body").append(scene);
                
                // Conteneur de la preview renvoyée par le parser
                var content = $("<div>").css(elems_css[1]);
                content.addClass("PreviewContent")
                content.addClass("restructuredtext_container")
                scene.append(content);
                
                $(".DjangoCodeMirror_tabs li.editor", instance_data.container).removeClass("tabactive");
                $(".DjangoCodeMirror_tabs li.preview", instance_data.container).addClass("tabactive");
                // Ajout du contenu renvoyé par le parser
                content.append(data);
                // Contrôle du clic dans la preview, ouvre les liens dans une nouvelle 
                // fenêtre et bloque les ancres
                $("a", content).click(function () {
                    var url = $(this).attr('href');
                    var is_anchor = (url && url.indexOf('#')==0) ? true : false;
                    if(url && !is_anchor) {
                        window.open( url );
                    }
                    return false;
                });
                // Resize
                $(window).bind("resize.djc_preview", { "input_source": input_source }, events.resize_preview);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $(".DjangoCodeMirror_tabs li.preview a", instance_data.container).append('<span class="error"> (!)</span>');
            }
        });
        return false;
    },
    /*
     * Close preview display and get back to editor
     */
    hide_preview: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
        
        // Don't add a new preview it if another one is allready displayed
        if (!instance_data.container.data("DCM_preview_markid")){
            return;
        }
        $(".DjangoCodeMirror_tabs li.editor", instance_data.container).addClass("tabactive");
        $(".DjangoCodeMirror_tabs li.preview", instance_data.container).removeClass("tabactive");
        var preview_id = instance_data.container.data("DCM_preview_markid");
        $("#"+preview_id).remove();
        $(window).unbind("resize.djc_preview");
        instance_data.container.removeData("DCM_preview_markid");
        instance_data.codemirror.focus();
    },
    resize_preview: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror"),
            preview_id = instance_data.container.data("DCM_preview_markid"),
            elems_css = coreutils.get_preview_sizes(input_source),
            editor_container = $(".CodeMirror-scroll", instance_data.container);
        $("#"+preview_id).css(elems_css[0]);
        $("#"+preview_id+" .PreviewContent").css(elems_css[1]);
        instance_data.codemirror.refresh();
    },

    /*
     * Settings panel
     */
    show_settings: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
        
        var border = instance_data.container.outerWidth(false) - instance_data.container.innerWidth();
        var panel = $('<div>').addClass("DjangoCodeMirror_settings_panel").css({
            "position": "absolute",
            "z-index": 5000,
            "width": (instance_data.container.outerWidth()-border)+"px",
            "height": (instance_data.container.outerHeight()-border)+"px"
        });
        
        var close_link = $('<a/>').attr("href", "#").addClass("close").html("Close");
        close_link.appendTo(panel);
        $("<h2>"+safegettext("Settings")+"</h2>").appendTo(panel);
        
        $.ajax({
            type: 'GET',
            dataType: "html",
            global: false,
            cache: false,
            url: instance_data.settings.settings_url,
            success: function(data) {
                instance_data.container.prepend(panel);
                $(".DjangoCodeMirror_menu .buttonSettings", instance_data.container).removeClass("error");
                panel.append(data);
                $("form", panel).css({
                   "overflow": "auto",
                    "height": (panel.innerHeight()-$("h2", panel).outerHeight())+"px"
                });
                close_link.click({ "panel": panel }, function (e) {
                    $(window).unbind("resize.djc_settings");
                    $(e.data.panel).remove();
                    return false;
                });
                $("form", panel).submit({ "input_source": input_source, "panel": panel }, events.submit_settings);
                $(window).bind("resize.djc_settings", { "input_source": input_source, "panel": panel }, events.resize_settings);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $(".DjangoCodeMirror_menu .buttonSettings", instance_data.container).addClass("error");
                createGrowl(instance_data.container, "warning", textStatus, errorThrown, false);
            }
        });
        return false;
    },
    submit_settings: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
            panel = $(event.data.panel);
        // Serialize the form fields and submit them
        $.ajax({
            type: 'POST',
            dataType: "json",
            global: false,
            cache: false,
            data: $("form", panel).serialize(),
            url: $("form", panel).attr("action"),
            success: function(data) {
                // Update codemirror settings
                $.each(data.setting_options, function(key, value) {
                    instance_data.codemirror.setOption(key, value)
                });
                // Close panel
                $(window).unbind("resize.djc_settings");
                panel.remove();
                createGrowl(instance_data.container, "success", safegettext("Success"), safegettext("Successful save"), false);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                createGrowl(instance_data.container, "warning", textStatus, errorThrown, false);
            }
        });
        return false;
    },
    resize_settings: function(event) {
        var input_source = $(event.data.input_source),
            instance_data = input_source.data("djangocodemirror");
            panel = $(event.data.panel),
            borders = 0;
        panel.css({
            "width": (instance_data.container.outerWidth()-borders)+"px",
            "height": (instance_data.container.outerHeight()-borders)+"px"
        });
        $("form", panel).css({"height": (panel.innerHeight()-$("h2", panel).outerHeight())+"px"});
    }
};


/*
* Various utilities
*/
var coreutils = {
    /*
    * Pre-processing on avalaible buttons
    * 
    * This is where buttons should be deleted or modified from defined settings
    */
    buttons_preprocessing: function(settings, buttons) {
        // Available buttons indexation on classname
        var button_indexes = {};
        $.each(buttons, function(item_index, item_value) {
            if(!item_value.separator){
                button_indexes[item_value.classname] = item_index;
            }
        });
        // Delete button from registry if option is disabled
        // Assume that there are two buttons followed by a separator
        if( button_indexes['buttonFullscreenEnter'] != undefined && button_indexes['buttonFullscreenEnter'] != null){
            if(!settings.fullscreen){
                var pos_enter = button_indexes['buttonFullscreenEnter'];
                var pos_exit = button_indexes['buttonFullscreenExit'];
                delete buttons[pos_enter];
                delete buttons[pos_exit];
                if(buttons[pos_exit+1].separator) {
                    delete buttons[pos_exit+1];
                }
            }
        }
        // Quicksave button
        if( button_indexes['buttonQuickSave'] != undefined && button_indexes['buttonQuickSave'] != null){
            var pos = button_indexes['buttonQuickSave'];
            if(settings.quicksave_url){
                buttons[pos].quicksave_url = settings.quicksave_url;
                buttons[pos].quicksave_datas = settings.quicksave_datas;
                buttons[pos].csrf = settings.csrf;
            } else {
                delete buttons[pos];
                if(buttons[pos+1].separator) {
                    delete buttons[pos+1];
                }
            }
        }
        // Undo/Redo buttons
        // Assume that there are two buttons followed by a separator
        if( button_indexes['buttonUndo'] != undefined && button_indexes['buttonUndo'] != null){
            var pos_undo = button_indexes['buttonUndo'];
            var pos_redo = button_indexes['buttonRedo'];
            if(!settings.undo_buttons){
                delete buttons[pos_undo];
                delete buttons[pos_redo];
                if(buttons[pos_redo+1].separator) {
                    delete buttons[pos_redo+1];
                }
            }
        }
        // Help link if setted
        if( button_indexes['buttonHelp'] != undefined && button_indexes['buttonHelp'] != null){
            var pos = button_indexes['buttonHelp'];
            if( settings.help_link ){
                buttons[pos].url = settings.help_link;
            } else {
                delete buttons[pos];
            }
        }
        // Help link if setted
        if( button_indexes['buttonSettings'] != undefined && button_indexes['buttonSettings'] != null){
            var pos = button_indexes['buttonSettings'];
            if(!settings.settings_url){
                delete buttons[pos];
            }
        }
        
        return buttons;
    },
    /*
    // Getters to calculate CSS size of elements
    */
    get_preview_sizes: function(input_source) {
        var instance_data = input_source.data("djangocodemirror"),
            editor_container = $(".CodeMirror-scroll", instance_data.container),
            editor_scrollbar = $(".CodeMirror-scrollbar", instance_data.container),
            menu_height = $(".DjangoCodeMirror_menu", instance_data.container).outerHeight(true),
            scrollbar_plus = (editor_scrollbar.css('display') == 'block') ? editor_scrollbar.outerWidth() : 0;
        
        var scene_css = {
            'position': "absolute",
            'z-index': 3000,
            'left': editor_container.offset().left,
            'top': editor_container.offset().top-menu_height,
            'width': (editor_container.outerWidth()+scrollbar_plus)-(instance_data.settings.preview_padding*2)-(instance_data.settings.preview_borders*2),
            'height': editor_container.outerHeight()-(instance_data.settings.preview_padding*2)+menu_height-(instance_data.settings.preview_borders*2),
            'overflow': 'auto',
            'padding': instance_data.settings.preview_padding
        };
        var content_css = {
            'width': editor_container.width()-(instance_data.settings.preview_padding*4),
            'height': editor_container.height()-(instance_data.settings.preview_padding*4),
            'border-size': 1
        };
        return [scene_css, content_css];
    },
    get_fullscreen_sizes: function(input_source) {
        var instance_data = input_source.data("djangocodemirror"),
            window_elem = $(window),
            computed_margins = instance_data.container.outerHeight(true) - $(".CodeMirror", instance_data.container).outerHeight(true);
        var scene_css = {
            'position': "absolute",
            'z-index': 2000,
            'left': 0,
            'top': window_elem.scrollTop(),
            'width': window_elem.width(),
            'height': window_elem.height()
        };
        var content_css = {'height':(window_elem.height() - computed_margins) + "px"};
        return [scene_css, content_css];
    }
};


})( jQuery );