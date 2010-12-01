$(document).ready(function () {
	$("form").live("submit", function () {
		$.mobile.pageLoading();
	});
});

$("div").live('pagecreate', function (event) {
	var pageWidth = $(event.target).width() - 30;
	if (pageWidth > 1000) pageWidth = 1000;
	$("span.results-chart", event.target).each(function (index, element) {
		var chart = $('<img src="' + $(element).attr("chart-url") + '&chs=' + pageWidth + 'x100">');
		$(element).replaceWith(chart);
	});
});