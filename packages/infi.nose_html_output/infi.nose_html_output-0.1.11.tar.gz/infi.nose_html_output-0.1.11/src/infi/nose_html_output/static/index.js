function document_load() {
        var toggle_foreach = function(index, element) {
        var func = function() {
            $('div', $(element).parent().parent().parent()).next().next().toggle();
            $('div', $(element).parent().parent().parent()).next().toggle();
            var cur_class = $(element).attr('class')
            if (cur_class.search("down-arrow") == -1) {
                $(element).attr('class', cur_class.replace('right-arrow', 'down-arrow'))
            }
            else {
                $(element).attr('class', cur_class.replace('down-arrow', 'right-arrow'))
            }
            return false;
            
        }
        $(element).click(func);
    }
    
    var minitoggle_foreach = function(index, element) {
        var func = function() {
            $("div", $(element).parent().parent()).toggle();
            return false;
        }
        $(element).click(func);
    }
    $(".toggle").each(toggle_foreach);
    $(".minitoggle").each(minitoggle_foreach);
    
    // auto-toggle passed suites and modules
    $(".toggle", $(".suite_passed").parent()).click();
    $(".toggle", $(".module_passed").parent()).click();
}

$(document).ready(function() {
    document_load();
});