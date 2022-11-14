chrome.runtime.onMessage.addListener( data => {
	if ( data.type === 'RestaurantFinder' ) {
		notify( data.message );
	}
});

chrome.runtime.onInstalled.addListener( () => {
	chrome.contextMenus.create({
		id: 'RestaurantFinder',
		title: "Find a great restaurant: %s", 
		contexts:[ "selection" ]
	});
});

chrome.contextMenus.onClicked.addListener( ( info, tab ) => {
	if ( 'notify' === info.menuItemId ) {
		notify( info.selectionText );
	}
} );

const notify = message => {
	chrome.storage.local.get( ['RestaurantFinderCount'], data => {
		let value = data.notifyCount || 0;
		chrome.storage.local.set({ 'RestaurantFinderCount': Number( value ) + 1 });
	} );

	return chrome.notifications.create(
		'',
		{
			type: 'basic',
			title: 'RestaurantFinder',
			message: message || 'RestaurantFinder',
			iconUrl: './assets/icons/128.png',
		}
	);
};