'use strict';

angular.module('planevent').controller('ContactsEditController',
		function($scope) {

	$scope.contactTypes = [
		{
			label: 'telephone',
			icon: 'phone',
		}, {
			label: 'email',
			icon: 'envelope',
		}, {
			label: 'fax',
			icon: 'fax',
		}, {
			label: 'facebook',
			icon: 'facebook',
		}, {
			label: 'www',
			icon: 'globe',
		},
	];

	$scope.contactIcons = {
		tel: 'phone',
		www: 'globe',
		email: 'envelope',
		fax: 'fax',
		facebook: 'facebook',
	};

	$scope.getContactIcon = function(contactType) {
		var icon = $scope.contactIcons[contactType];
		if (icon === undefined) {
			return 'share';
		} else {
			return icon;
		}
	};

	$scope.removeContact = function(index) {
		$scope.offer.contacts.splice(index, 1);
	};

	$scope.addContact = function() {
		$scope.offer.contacts[$scope.offer.contacts.length] = {};
	};
});
