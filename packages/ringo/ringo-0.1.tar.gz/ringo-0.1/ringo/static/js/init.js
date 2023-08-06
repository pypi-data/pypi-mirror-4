$(document).ready(function() {
    $('.jsoverview').dataTable({
        "bJQueryUI": true,
        "sPaginationType": "full_numbers"
    });

    $('.jsoverview_bootstrap').dataTable({
	"sDom": "<'row-fluid'<'span6'f><'span6'l>r>t<'row-fluid'<'span6'i><'span6'p>>",
	"bPaginate": false,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false
    });

    /* Setup dialogs */
    $('#dialog-erase').addClass('fade hide');
    $('#dialog-erase').modal('show');
    $('#dialog-delete').addClass('fade hide');
    $('#dialog-delete').modal('show');
    $('#dialog-restore').addClass('fade hide');
    $('#dialog-restore').modal('show');

    /* Generic Jquery UI dialog. Are hidden by default and opened when
     * clicking the and element with the .dialog-generic-trigger. Note that
     * this element needs the "rel" attribute which has the id of the dialog
     * to open. */
    $(".dialog-generic").dialog({ autoOpen: false });
    $(".dialog-generic-trigger").click(function(e) {
	e.preventDefault();
	var target = $(this).attr('rel');
	$(target).dialog('option','position',[e.clientX,e.clientY]);
	$(target).dialog('open');
    });

    $("a[rel=popover]").popover(options={html:true});
    $(".popover-trigger").click(function(e) {
	e.preventDefault();
    });

    /* datepicker */
    $('.datepicker').datepicker( {dateFormat: "yy-mm-dd"} );
    $('.datetimepicker').datetimepicker({ dateFormat: 'yy-mm-dd', timeFormat: 'hh:mm' });

    /* Sortables */
    $('.sortable').sortable();
    $('.sortable').disableSelection();
    $('.tooltip-top').tooltip();

    $('.nav li a').click(function(e) {
	//e.preventDefault();
	//var targeturl = $(this).attr('href');
    	//$.get(targeturl, function(data){
	//	$('#main').replaceWith($(data).find('#main').parent().html());
    	//});
    });
});
