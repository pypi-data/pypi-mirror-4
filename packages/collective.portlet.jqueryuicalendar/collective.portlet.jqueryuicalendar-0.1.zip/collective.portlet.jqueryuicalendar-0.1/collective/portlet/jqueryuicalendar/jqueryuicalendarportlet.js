jQuery(function($){
  jQuery.timeago.settings.allowFuture = true;
  $.ajax("@@jqueryuicalendar.json").done(function(data, textStatus, jqXHR){

    function getEventText(event, notfirst){
        var tpl = $("#eventtemplate").clone();
        tpl.find("a").attr("href", event.url);
        tpl.find(".description").text(event.description);
    	tpl.find(".eventtitle").text(event.title);
        if (notfirst) {
        	tpl.find(".timeago").remove();
        }else{
	        tpl.find(".timeago").attr("datetime", event.dtstart);
	        tpl.find(".timeago").text(event.start);
	        tpl.find(".timeago").timeago();
        }
        tpl.show();
        return tpl.html();
    }
    function showManyEventsDialog(events){
		var eventText = "";
		for (var i=0,len=events.length; i<len; i++){
			eventText += getEventText(events[i], i);
    	}
        $('#eventdialog').html(eventText);
        $('#eventdialog').dialog({title: events[0].title,
                                  resizable: false,
                                  position: { of: "#datepicker"},
                                  show: "slow"
                                  });

    }
    function hasEventsIn(date){
      var key = $.datepicker.formatDate('yy-mm-dd', date);
      if (key in data){
        return [true, '', '' + data[key].length +' events'];
      }
      return [false];
    }
    function showEvents( dateText, inst){
      var dateObj = $.datepicker.parseDate('dd/mm/yy', dateText);
      var dateStr = $.datepicker.formatDate('yy-mm-dd', dateObj);
      var events = data[dateStr];
      showManyEventsDialog(events);
    }
    $('#datepicker').datepicker({
      inline: true,
      beforeShowDay: hasEventsIn,
      onSelect: showEvents
    });
  });
});