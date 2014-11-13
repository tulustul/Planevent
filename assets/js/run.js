'use strict';

planevent.run(function(editableOptions, editableThemes) {
	editableOptions.theme = 'bs3';
	editableThemes.bs3.cancelTpl =
		'<md-button class="fa fa-times small-button" ' +
		'ng-click="$form.$cancel()"></md-button>';

	editableThemes.bs3.submitTpl =
		'<md-button class="fa fa-check small-button submit-button" ' +
		'ng-click="$form.$submit()" class="submit"></md-button>';
});
