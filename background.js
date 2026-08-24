// Background Service Worker for AnnaDATA Extension 
chrome.action.onClicked.addListener(async (tab) => {   
  const targetUrl = "http://127.0.0.1:8000";   
  // Check if an AnnaDATA tab is already open   
  const tabs = await chrome.tabs.query({ url: targetUrl + "/*" });   
  if (tabs.length > 0) {     
    // Focus existing tab     
    chrome.tabs.update(tabs[0].id, { active: true });     
    chrome.windows.update(tabs[0].windowId, { focused: true });   
  } else {     
    // Create new dedicated tab     
    chrome.tabs.create({ url: targetUrl }); 
  } // <--- This bracket was missing
});