jQuery.fn.j01Select = function(p) {
    p = jQuery.extend({
        widgetName: null,
        closeAfterAddToken: true,
        prependCloser: false,
        evenCSS: null,
        oddCSS: null
    }, p);
    if (!p.widgetName) {
        alert('j01Select widgetName is missing');
    }
    
    // elements
    var j01SelectWidget = null;
    var j01SelectOptions = null;
    var multiple = false;

    function removeToken(token) {
        $('#' + token.id).remove();
        j01SelectOptions.hide();
    }

    function addToken(id, value, title) {
        tid = 'j01SelectToken-' + id;
        if (multiple) {
            $('#' + tid, j01SelectWidget).remove();
        }else {
            // remove all existing tokens
            $('.j01SelectToken', j01SelectWidget).remove();
        }
        var li = $('<li id="'+tid+'" class="j01SelectToken"></li>').get(0);
        var span = $('<span class="j01SelectTokenLabel">'+title+'</span>').get(0);
        var closer = $('<span class="j01SelectTokenCloser">&nbsp;</span>').get(0);
        var input = $("<input type='hidden' name='"+p.widgetName+":list' value='"+value+"' />").get(0);
        if (p.prependCloser) {
            $(li).append(closer);
            $(li).append(span);
        } else {
            $(li).append(span);
            $(li).append(closer);
        }
        $(li).append(input);
        $(closer).click(function(e) {
            closer = (e.target || e.srcElement);
            token = closer.parentNode
            removeToken(token);
            e.preventDefault();
            return false;
        });
        j01SelectWidget.append(li);
        if (p.closeAfterAddToken){
            j01SelectOptions.hide();
        }
    }

    function renderOption(id, value, title) {
        var div = $('<div id="'+id+'">'+title+'</div>').get(0);
        $(div).click(function() {
            addToken($(this).attr('id'), value, title);
        }).hover(
                function() {$(this).addClass("tokenHover");},
                function () {$(this).removeClass("tokenHover");}
        );
        return div;
    }

    function getOptions(select) {
        // serialize the original select options
        var options = [];
        select.children().each( function() {
            var id = $(this).attr('id');
            var html = $(this).html();
            var val = $(this).val();
            var sel = null;
            var grp = null;
            if(this.tagName.toUpperCase() == 'OPTGROUP') {
                grp = $(this).attr('label');
            }else{
                sel = $(this).prop('selected');
            }
            if (val && val !== '--NOVALUE--') {
                options.push({id: id, text: html, value: val, selected: sel, group: grp});
            }
        });
        return options;
    }

    function renderOptions(select) {
        // get select option items
        var items = getOptions(select);
        var odd = true;
        for (var i=0;i<items.length;i++) {
            var item = items[i];
            var option = null;
            if (item.groupName){
                option = $('<div class="group">'+item.groupName+'</div>').get(0);
                j01SelectOptions.append(option);
            }else if (item.selected){
                // render selected option as token
                addToken(item.id, item.value, item.text);
            }else{
                // render any not selected option in j01SelectOptions
                option = renderOption(item.id, item.value, item.text);
                j01SelectOptions.append(option);
            }
            if (option) {
                if (option && odd && p.oddCSS) {
                    $(option).addClass(p.oddCSS);
                }else if (!odd && p.evenCSS) {
                    $(option).addClass(p.evenCSS);
                }
                // switch even/odd independent if we have even or odd classes
                if (odd) {
                    odd = false;
                }else{
                    odd = true;
                }
            }
        }
    }

    return this.each(function(){
        // get select widget and hide
        var select = $(this);
        // set nultiple value based on select property
        multiple = select.prop('multiple');
        var html = ''
        html += '<div class="j01Select">';
        html += '  <ul class="j01SelectWidget">';
        html += '    <li class="j01SelectTokenPlaceHolder"></li>';
        html += '  </ul>';
        html += '  <div class="j01SelectOptions" style="display: none;"></div>';
        html += '</div>';
        select.after(html);
        var j01Select = select.next('.j01Select');
        j01SelectWidget = $('.j01SelectWidget', j01Select);
        j01SelectOptions = $('.j01SelectOptions', j01Select);
        j01SelectOptions.hide();

        // setup widget focuse handler
        j01SelectWidget.click(function(e) {
            j01SelectOptions.toggle();
        });
        // remove original select
        renderOptions(select);
        select.remove();
    });
};

