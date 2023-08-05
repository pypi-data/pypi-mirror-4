/**
 * Javascript code for the reordering support
 */

jQuery.alternative_orderui = {
    messages: {
        en: "Fill the new position for the content thats now is at position ",
        it: "Inserisci la nuova posizione per l'elemento alla posizione "
    }
};

jq(document).ready(function () {
	var js_baseurl = jq("head base").attr('href');
	var lang = jq("html").attr('lang') || 'en';
	var querystring = window.location.search;
	var qspos = querystring.indexOf("pagenumber");
	var qsn = '';
	
	// read the pagenumber argument 
	var pageNumber = 1;
	if (qspos > -1) {
		pageNumber = parseInt(querystring.substr(qspos + 11, qspos + 12), 10);
		qsn = "&pagenumber=" + pageNumber;
	}

	var previous = jq("#folderlisting-main-table .previous a").text();
	var pageSize = 20;
	if (previous) {
		var pageSizeRegExp = /\d+/;
		pageSize = parseInt(previous.match(pageSizeRegExp), 10);
	}

	jq("#listing-table tbody tr").each(function (i) {
		// Defining index
		var index = 0;
		if (pageNumber > 1) {
			index = i + (pageNumber - 1) * pageSize;
		}
		else {
			index = i;
		}
		
		var row = jq(this);
		row.find("td.notDraggable input:first").after('&nbsp;<span class="discreet order-index">' + (index + 1) + '</span>');			
		var controlCell = row.find("td.draggable", row);
		var elId = row.children("td.notDraggable").find(":checkbox").attr("id").replace("cb_", "");
		var title = jq.trim(row.children("td.notDraggable").next(":first").find("a").text());
		controlCell.empty().append('&nbsp;<a href="javascript:;" class="reorder-cmd">'
		                  + '<img alt="" src="++resource++move_16x16.gif" />'
				          + '</a>');
		jq(".reorder-cmd", controlCell).click(function (event) {
			//event.preventDefault();
			var choosen = prompt(jq.alternative_orderui.messages[lang] + (index + 1) + " (" + title + ")", "");
			if (choosen !== null) {
				var v = parseInt(choosen, 10) - 1;
				var upOrDown = (v < index ? 'up' : 'down');
				var delta = (v < index ? -(v - index) : (v - index));
				var show_all = "";
				if (querystring.indexOf("show_all=true") > -1) {
					show_all = "&show_all=true";
				}
				window.location.href = js_baseurl + "folder_position?position=" + upOrDown + "&amp;id=" + elId + "&delta=" + delta + show_all + qsn;
			}
		});
	});
});

/*
kukit.actionsGlobalRegistry.register("plone-initDragAndDrop",
    function(oper) {
		// NOP!
});
*/

// Disable KSS - This is the best way I found
if (window.kukit && window.kukit.actionsGlobalRegistry && window.kukit.actionsGlobalRegistry.content) {
	kukit.actionsGlobalRegistry.content['plone-initDragAndDrop'] = function () {};
}
