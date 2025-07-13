

// Enable side panel behavior
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error('Error setting side panel behavior:', error));


// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  console.log('Extension icon clicked for tab:', tab.id);
  
  try {
    // Open the side panel
    await chrome.sidePanel.open({ windowId: tab.windowId });
    console.log('Side panel opened successfully');
  } catch (error) {
    console.error('Error opening side panel:', error);
  }
});



// Background script to handle tab communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageInfo') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        sendResponse({
          title: tabs[0].title,
          url: tabs[0].url
        });
      }
    });
    return true; // Keep the message channel open for async response
  }
});

