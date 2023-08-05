/**
 * Scripts for collective.sortmyfolder
 */

/*global jq: false, document: false*/

jq(document).ready(function() {
	var $page = jq('#sortingUI');
	var $customCommand = jq(':radio:last', $page);
	var $customCommandData = jq('#choice_custom_data');
	
	$customCommand.removeAttr('disabled');
	
	var refresh = function() {
		if ($customCommand.is(':checked')) {
			$customCommandData.removeAttr('disabled');
		} else {
			$customCommandData.attr('disabled', 'disabled');
		}
	};

	jq(':radio').click(refresh);
	
	$customCommandData.blur(function() {
		$customCommand.val($customCommandData.val());
	});
	
	refresh();
});
