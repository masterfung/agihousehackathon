// Content script to get page information
function getPageInfo() {
  return {
    title: document.title,
    url: window.location.href
  };
}

// Listen for messages from the extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageInfo') {
    sendResponse(getPageInfo());
  }
});

// Send page info when the script loads
chrome.runtime.sendMessage({
  action: 'pageInfo',
  data: getPageInfo()
}); 