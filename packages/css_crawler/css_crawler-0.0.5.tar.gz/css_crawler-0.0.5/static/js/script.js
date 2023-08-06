YAHOO.namespace('nagare');

YAHOO.namespace("nagare.css_crawler");

YAHOO.nagare.css_crawler = function () {
    return {
        init_selectors: function(){
            var elements = YAHOO.util.Dom.getElementsByClassName('toggle-selectors');
            for (var i = 0; i < elements.length; i++)
            {
                YAHOO.util.Event.addListener(elements[i], "click", YAHOO.nagare.css_crawler.toggle_selector_callback);
            }

            var global_toggle = YAHOO.util.Dom.get('toggle@selectors');
            YAHOO.util.Event.addListener(global_toggle, "click", YAHOO.nagare.css_crawler.global_toggle_callback);
        },
        toggle_selector_callback: function(evt){
            var target = YAHOO.util.Event.getTarget(evt);
            YAHOO.nagare.css_crawler.toggle_selector(target);
            YAHOO.util.Event.preventDefault(evt);
        },
        toggle_selector: function(element){
            var selectors = YAHOO.util.Dom.getNextSibling(element);
            if (YAHOO.util.Dom.hasClass(selectors, 'hidden')) {
                YAHOO.util.Dom.removeClass(selectors, 'hidden');
                YAHOO.util.Dom.removeClass(element, 'collapse');
            }
            else {
                YAHOO.util.Dom.addClass(selectors, 'hidden');
                YAHOO.util.Dom.addClass(element, 'collapse');
            }
        },
        global_toggle_callback: function(evt){
            var target = YAHOO.util.Event.getTarget(evt);
            YAHOO.nagare.css_crawler.global_toggle(target);
            YAHOO.util.Event.preventDefault(evt);
        },
        global_toggle: function(element){
            var parent = YAHOO.util.Dom.getAncestorByClassName(element, 'result')
            if (YAHOO.util.Dom.hasClass(parent, 'expand')) {
                YAHOO.util.Dom.removeClass(parent, 'expand');
            }
            else {
                YAHOO.util.Dom.addClass(parent, 'expand');
            }
        },
        give_focus: function(){
            YAHOO.util.Dom.get('url').focus();

        }
    }
}();

YAHOO.util.Event.onDOMReady(YAHOO.nagare.css_crawler.init_selectors);
YAHOO.util.Event.onDOMReady(YAHOO.nagare.css_crawler.give_focus);
