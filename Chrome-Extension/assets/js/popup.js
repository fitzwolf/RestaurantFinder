const text = document.getElementById( 'RestaurantFinder-text' );
const RestaurantFinder = document.getElementById( 'RestaurantFinder-button' );
const reset = document.getElementById( 'RestaurantFinder-reset' );
const counter = document.getElementById( 'RestaurantFinder-count' );

chrome.storage.local.get( ['RestaurantFinderCount'], data => {
	let value = data.RestaurantFinderCount || 0;
	counter.innerHTML = value;
} );

chrome.storage.onChanged.addListener( ( changes, namespace ) => {
	if ( changes.RestaurantFinderCount ) {
		let value = changes.RestaurantFinderCount.newValue || 0;
		counter.innerHTML = value;
	}
});

reset.addEventListener( 'click', () => {
	chrome.storage.local.clear();
	text.value = '';
} );

RestaurantFinder.addEventListener( 'click', () => {
	chrome.runtime.sendMessage( '', {
		type: 'RestaurantFinder',
		message: text.value
	});
} );
