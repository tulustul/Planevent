'use strict';

planevent.run(function(editableOptions, editableThemes) {
	editableOptions.theme = 'bs3';
	editableThemes.bs3.cancelTpl =
		'<pebutton icon="times" ng-click="$form.$cancel()" />';
	editableThemes.bs3.submitTpl =
		'<pebutton icon="check" ng-click="$form.$submit()" class="submit" />';
});
