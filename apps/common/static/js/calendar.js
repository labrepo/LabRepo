$(function() {

    /* initialize the calendar
     -----------------------------------------------------------------*/
    var calendar = $('#calendar'),
        changeDate = function(e) {
            if(e.editable) {
                $.post(e.edit_url, {start: e.start, end: e.end})
                    .done(function (responce) {
                        $('#all').prepend(responce.data);
                    }).fail(function (xhr) {
                        if (xhr.status === 403) {
                            console.log('Permission Denied');
                        }
                    });
            }
            return false;
        };

    calendar.fullCalendar({
        allDayText: gettext('all-day'),
        timeFormat: { // for event elements
            '': 'hh:(mm)' // default
        },
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        height: 638,
        monthNames: [gettext('January'), gettext('February'), gettext('March'), gettext('April'), gettext('May'), gettext('June'), gettext('July'), gettext('August'), gettext('September'), gettext('October'), gettext('November'), gettext('December')],
        monthNamesShort: [gettext('Jan'), gettext('Feb'), gettext('Mar'), gettext('Apr'), gettext('May'), gettext('Jun'), gettext('Jul'), gettext('Aug'), gettext('Sep'), gettext('Oct'), gettext('Nov'), gettext('Dec')],
	    dayNames: [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')],
	    dayNamesShort: [gettext('Sun'), gettext('Mon'), gettext('Tue'), gettext('Wed'), gettext('Thu'), gettext('Fri'), gettext('Sat')],
        buttonText: {//This is to add icons to the visible buttons
            prev: "<span class='fa fa-caret-left'></span>",
            next: "<span class='fa fa-caret-right'></span>",
            today: gettext('today'),
            month: gettext('month'),
            week: gettext('week'),
            day: gettext('day')
        },
        events: calendar.data('events'),
        editable: true,
        droppable: true, // this allows things to be dropped onto the calendar !!!
        eventDrop: function(e) {changeDate(e)},
        eventResize: function(e) {changeDate(e)}

    })

});

