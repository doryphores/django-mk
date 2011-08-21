$(document).ready(function () {
	$("form").live("submit", function () {
		$.mobile.pageLoading();
	});
});

$("div").live('pagecreate', function (event) {
	$(".latest-stats", event.target).tablesorter({
		textExtraction: function(node) {
			return node.innerHTML.replace(/<small>.*<\/small>/, '');
		}
	});
});