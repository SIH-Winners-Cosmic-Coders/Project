// ==========================================
// 0. UI Translation Engine
// ==========================================
const uiTranslations = {
  en: {
    title: "🌾 AnnaDATA Edge Twin", subtitle: "Map Fusion • Live Climate • Offline Voice",
    simulate: "Simulate Edge/Offline Mode", fieldLoc: "📍 Farm Field Location",
    mapSub: "Tap anywhere on the map to inspect farm coordinates.", weatherTwin: "📊 Live Soil & Weather Twin",
    dialect: "Farmer Dialect:", tapMic: "Tap Mic to Speak or Cam to Scan",
    feedback: "Was this advice helpful?", yes: "👍 Yes", no: "👎 No",
    lblTemp: "Air Temp / Humidity", lblMoist: "Soil Moisture (0-7cm)", lblRain: "Precipitation / Rain", lblNdvi: "Estimated NDVI Health"
  },
  hi: {
    title: "🌾 अन्नडेटा (AnnaDATA) एज ट्विन", subtitle: "मैप फ्यूजन • लाइव मौसम • ऑफलाइन वॉयस",
    simulate: "एज/ऑफलाइन मोड सिमुलेट करें", fieldLoc: "📍 खेत का स्थान",
    mapSub: "खेत के निर्देशांक देखने के लिए मैप पर टैप करें।", weatherTwin: "📊 लाइव मिट्टी और मौसम",
    dialect: "किसान की भाषा:", tapMic: "बोलने के लिए माइक या स्कैन के लिए कैमरा टैप करें",
    feedback: "क्या यह सलाह मददगार थी?", yes: "👍 हाँ", no: "👎 नहीं",
    lblTemp: "वायु तापमान / नमी", lblMoist: "मिट्टी की नमी (0-7cm)", lblRain: "वर्षा / बारिश", lblNdvi: "अनुमानित NDVI स्वास्थ्य"
  },
  od: {
    title: "🌾 ଅନ୍ନଡାଟା (AnnaDATA) ଏଜ୍ ଟ୍ୱିନ୍", subtitle: "ମ୍ୟାପ୍ ଫ୍ୟୁଜନ୍ • ଲାଇଭ୍ ପାଣିପାଗ • ଅଫଲାଇନ୍ ଭଏସ୍",
    simulate: "ଏଜ୍/ଅଫଲାଇନ୍ ମୋଡ୍ ସିମୁଲେଟ୍ କରନ୍ତୁ", fieldLoc: "📍 କ୍ଷେତର ସ୍ଥାନ",
    mapSub: "ସ୍ଥାନାଙ୍କ ଦେଖିବା ପାଇଁ ମ୍ୟାପ୍‌ରେ ଟ୍ୟାପ୍ କରନ୍ତୁ |", weatherTwin: "📊 ଲାଇଭ୍ ମାଟି ଏବଂ ପାଣିପାଗ",
    dialect: "କୃଷକ ଭାଷା:", tapMic: "କହିବାକୁ ମାଇକ୍ କିମ୍ବା ସ୍କାନ୍ କରିବାକୁ କ୍ୟାମେରା ଟ୍ୟାପ୍ କରନ୍ତୁ",
    feedback: "ଏହି ପରାମର୍ଶ ଲାଭଦାୟକ ଥିଲା କି?", yes: "👍 ହଁ", no: "👎 ନା",
    lblTemp: "ବାୟୁ ତାପମାତ୍ରା / ଆର୍ଦ୍ରତା", lblMoist: "ମୃତ୍ତିକା ଆର୍ଦ୍ରତା (0-7cm)", lblRain: "ବୃଷ୍ଟିପାତ / ବର୍ଷା", lblNdvi: "ଆନୁମାନିକ NDVI ସ୍ୱାସ୍ଥ୍ୟ"
  },
  bn: {
    title: "🌾 অন্নডেটা (AnnaDATA) এজ টুইন", subtitle: "ম্যাপ ফিউশন • লাইভ আবহাওয়া • অফলাইন ভয়েস",
    simulate: "এজ/অফলাইন মোড সিমুলেট করুন", fieldLoc: "📍 খামারের অবস্থান",
    mapSub: "স্থানাঙ্ক দেখতে ম্যাপের যেকোনো জায়গায় ট্যাপ করুন।", weatherTwin: "📊 লাইভ মাটি ও আবহাওয়া",
    dialect: "কৃষকের ভাষা:", tapMic: "কথা বলতে মাইক বা স্ক্যান করতে ক্যামেরা ট্যাপ করুন",
    feedback: "এই পরামর্শ কি সহায়ক ছিল?", yes: "👍 হ্যাঁ", no: "👎 না",
    lblTemp: "বায়ু তাপমাত্রা / আর্দ্রতা", lblMoist: "মাটির আর্দ্রতা (0-7cm)", lblRain: "বৃষ্টিপাত / বৃষ্টি", lblNdvi: "আনুমানিক NDVI স্বাস্থ্য"
  },
  te: {
    title: "🌾 అన్నడేటా (AnnaDATA) ఎడ్జ్ ట్విన్", subtitle: "మ్యాప్ ఫ్యూజన్ • లైవ్ వాతావరణం • ఆఫ్‌లైన్ వాయిస్",
    simulate: "ఎడ్జ్/ఆఫ్‌లైన్ మోడ్‌ను అనుకరించండి", fieldLoc: "📍 పొలం స్థానం",
    mapSub: "కోఆర్డినేట్‌లను తనిఖీ చేయడానికి మ్యాప్‌లో ఎక్కడైనా నొక్కండి.", weatherTwin: "📊 లైవ్ మట్టి మరియు వాతావరణం",
    dialect: "రైతు భాష:", tapMic: "మాట్లాడటానికి మైక్ లేదా స్కాన్ చేయడానికి కెమెరాపై నొక్కండి",
    feedback: "ఈ సలహా ఉపయోగపడిందా?", yes: "👍 అవును", no: "👎 లేదు",
    lblTemp: "గాలి ఉష్ణోగ్రత / తేమ", lblMoist: "మట్టి తేమ (0-7cm)", lblRain: "అవపాతం / వర్షం", lblNdvi: "అంచనా వేసిన NDVI ఆరోగ్యం"
  },
  mr: {
    title: "🌾 अन्नडेटा (AnnaDATA) एज ट्विन", subtitle: "मॅप फ्युजन • लाईव्ह हवामान • ऑफलाइन व्हॉइस",
    simulate: "एज/ऑफलाइन मोड सिमुलेट करा", fieldLoc: "📍 शेताचे स्थान",
    mapSub: "कोऑर्डिनेट्स तपासण्यासाठी नकाशावर कुठेही टॅप करा.", weatherTwin: "📊 लाईव्ह माती आणि हवामान",
    dialect: "शेतकऱ्याची भाषा:", tapMic: "बोलण्यासाठी माइक किंवा स्कॅन करण्यासाठी कॅमेरा टॅप करा",
    feedback: "हा सल्ला उपयुक्त ठरला का?", yes: "👍 होय", no: "👎 नाही",
    lblTemp: "हवेचे तापमान / आर्द्रता", lblMoist: "मातीची आर्द्रता (0-7cm)", lblRain: "पाऊस / पर्जन्यमान", lblNdvi: "अंदाजित NDVI आरोग्य"
  },
  ta: {
    title: "🌾 அன்னா டேட்டா எட்ஜ் ட்வின்", subtitle: "வரைபட ஒருங்கிணைப்பு • நேரலை வானிலை • ஆஃப்லைன் குரல்",
    simulate: "ஆஃப்லைன் பயன்முறையை உருவகப்படுத்து", fieldLoc: "📍 பண்ணை இருப்பிடம்",
    mapSub: "ஆயத்தொலைவுகளைச் சரிபார்க்க வரைபடத்தில் தட்டவும்.", weatherTwin: "📊 நேரலை மண் & வானிலை",
    dialect: "விவசாயி மொழி:", tapMic: "பேச மைக்கை அழுத்தவும் அல்லது கேமராவை ஸ்கேன் செய்யவும்",
    feedback: "இந்த ஆலோசனை பயனுள்ளதாக இருந்ததா?", yes: "👍 ஆம்", no: "👎 இல்லை",
    lblTemp: "காற்று வெப்பநிலை / ஈரப்பதம்", lblMoist: "மண் ஈரப்பதம் (0-7cm)", lblRain: "மழைப்பொழிவு", lblNdvi: "மதிப்பிடப்பட்ட NDVI"
  }
};

function updateUI() {
  const lang = document.getElementById('langSelect').value;
  const t = uiTranslations[lang] || uiTranslations['en'];
  
  if (document.getElementById('ui-title')) document.getElementById('ui-title').innerText = t.title;
  if (document.getElementById('ui-subtitle')) document.getElementById('ui-subtitle').innerText = t.subtitle;
  if (document.getElementById('ui-simulate')) document.getElementById('ui-simulate').innerText = t.simulate;
  if (document.getElementById('ui-field-loc')) document.getElementById('ui-field-loc').innerText = t.fieldLoc;
  if (document.getElementById('ui-map-sub')) document.getElementById('ui-map-sub').innerText = t.mapSub;
  if (document.getElementById('ui-weather-twin')) document.getElementById('ui-weather-twin').innerText = t.weatherTwin;
  if (document.getElementById('ui-dialect')) document.getElementById('ui-dialect').innerText = t.dialect;
  if (document.getElementById('voice-text')) document.getElementById('voice-text').innerText = t.tapMic;
  if (document.getElementById('ui-feedback-text')) document.getElementById('ui-feedback-text').innerText = t.feedback;
  if (document.getElementById('ui-btn-yes')) document.getElementById('ui-btn-yes').innerText = t.yes;
  if (document.getElementById('ui-btn-no')) document.getElementById('ui-btn-no').innerText = t.no;
  
  if (document.getElementById('ui-lbl-temp')) document.getElementById('ui-lbl-temp').innerText = t.lblTemp;
  if (document.getElementById('ui-lbl-moist')) document.getElementById('ui-lbl-moist').innerText = t.lblMoist;
  if (document.getElementById('ui-lbl-rain')) document.getElementById('ui-lbl-rain').innerText = t.lblRain;
  if (document.getElementById('ui-lbl-ndvi')) document.getElementById('ui-lbl-ndvi').innerText = t.lblNdvi;
}

// ==========================================
// 1. PWA & Offline Database
// ==========================================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => console.log('Service Worker registered with scope:', reg.scope))
      .catch(err => console.error('Service Worker registration failed:', err));
  });
}

const db = new Dexie('AgriCareDB');
db.version(2).stores({
  outbox: '++id, queryId, rating, status, timestamp',
});

// ==========================================
// 2. UI Elements & State
// ==========================================
const netBadge = document.getElementById('net-badge');
const netStatusText = document.getElementById('net-status-text');
const netIndicatorDot = document.getElementById('net-indicator-dot');
const simulateOfflineToggle = document.getElementById('simulate-offline');

const chatContainer = document.getElementById('chat-container');
const voiceBtn = document.getElementById('voice-btn');
const voiceText = document.getElementById('voice-text');
const langSelect = document.getElementById('langSelect');
const coordsText = document.getElementById('coords-text');
const feedbackSection = document.getElementById('feedback-section');

const metricTemp = document.getElementById('metric-temp');
const metricHumidity = document.getElementById('metric-humidity');
const metricSoilMoist = document.getElementById('metric-soil-moist');
const metricSoilStatus = document.getElementById('metric-soil-status');
const metricRain = document.getElementById('metric-rain');
const metricNdvi = document.getElementById('metric-ndvi');
const metricNdviStatus = document.getElementById('metric-ndvi-status');

let lastQueryId = ""; 
let isSimulatingOffline = false;

// Audio Playback Manager (No Auto-Play)
let currentAudio = null;
let currentPlayingBtn = null;

function stopAllAudio() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  if (currentPlayingBtn) {
    currentPlayingBtn.innerHTML = '🔊 Play';
    currentPlayingBtn.classList.remove('bg-amber-600');
    currentPlayingBtn.classList.add('bg-emerald-700');
    currentPlayingBtn = null;
  }
}

function toggleAudioPlayback(btn, audioUrl, fallbackText) {
  if (currentPlayingBtn === btn) {
    stopAllAudio();
    return;
  }

  stopAllAudio();

  currentPlayingBtn = btn;
  btn.innerHTML = '⏸️ Pause';
  btn.classList.remove('bg-emerald-700');
  btn.classList.add('bg-amber-600');

  if (audioUrl) {
    currentAudio = new Audio(audioUrl);
    currentAudio.play().catch(() => playSpeechSynthesis(fallbackText, btn));
    currentAudio.onended = () => stopAllAudio();
  } else {
    playSpeechSynthesis(fallbackText, btn);
  }
}

function playSpeechSynthesis(text, btn) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'hi-IN';
  utterance.rate = 0.95;

  utterance.onend = () => stopAllAudio();
  utterance.onerror = () => stopAllAudio();

  window.speechSynthesis.speak(utterance);
}

// Trigger UI Translation Binding
langSelect.addEventListener('change', updateUI);
window.addEventListener('DOMContentLoaded', updateUI);

let currentFieldData = {
  lat: 20.2961, lng: 85.8245, temp: 28.5, humidity: 75, soilMoisture: 0.32, rain: 0.0, ndvi: 0.72
};

// ==========================================
// 3. Map Initialization
// ==========================================
const map = L.map('map').setView([currentFieldData.lat, currentFieldData.lng], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18, attribution: '© OpenStreetMap'
}).addTo(map);

let marker = L.marker([currentFieldData.lat, currentFieldData.lng]).addTo(map);

setTimeout(() => { map.invalidateSize(); }, 200);

map.on('click', (e) => {
  const { lat, lng } = e.latlng;
  currentFieldData.lat = parseFloat(lat.toFixed(4));
  currentFieldData.lng = parseFloat(lng.toFixed(4));
  
  marker.setLatLng([lat, lng]);
  coordsText.innerText = `${currentFieldData.lat}° N, ${currentFieldData.lng}° E`;
  fetchLiveFieldMetrics(currentFieldData.lat, currentFieldData.lng);
});

// ==========================================
// 4. Open-Meteo Integration
// ==========================================
async function fetchLiveFieldMetrics(lat, lng) {
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=temperature_2m,relative_humidity_2m,precipitation,soil_moisture_0_to_7cm&timezone=auto`;
    const res = await fetch(url);
    const data = await res.json();

    if (data.current) {
      currentFieldData.temp = data.current.temperature_2m;
      currentFieldData.humidity = data.current.relative_humidity_2m;
      currentFieldData.rain = data.current.precipitation;
      currentFieldData.soilMoisture = data.current.soil_moisture_0_to_7cm;

      const ndviEstimate = (0.55 + (currentFieldData.soilMoisture * 0.5) - (currentFieldData.temp > 35 ? 0.1 : 0.0)).toFixed(2);
      currentFieldData.ndvi = Math.min(0.88, Math.max(0.2, parseFloat(ndviEstimate)));
      updateMetricsUI();
    }
  } catch (err) {
    console.warn('Offline mode: Using cached telemetry');
    updateMetricsUI();
  }
}

function updateMetricsUI() {
  metricTemp.innerText = `${currentFieldData.temp} °C`;
  metricHumidity.innerText = `RH: ${currentFieldData.humidity}%`;
  metricSoilMoist.innerText = `${currentFieldData.soilMoisture} m³/m³`;
  metricSoilStatus.innerText = currentFieldData.soilMoisture < 0.2 ? '⚠️ Dry Soil' : 'Optimal Moisture';
  metricSoilStatus.className = currentFieldData.soilMoisture < 0.2 ? 'text-amber-400 text-[11px] block' : 'text-emerald-400 text-[11px] block';
  
  metricRain.innerText = `${currentFieldData.rain} mm`;
  metricNdvi.innerText = currentFieldData.ndvi;
  metricNdviStatus.innerText = currentFieldData.ndvi > 0.6 ? 'Healthy Biomass' : 'Stressed Vegetation';
}

fetchLiveFieldMetrics(currentFieldData.lat, currentFieldData.lng);

// ==========================================
// 5. Network & Edge Tracker
// ==========================================
if (simulateOfflineToggle) {
  simulateOfflineToggle.addEventListener('change', (e) => {
    isSimulatingOffline = e.target.checked;
    if (isSimulatingOffline) {
      netStatusText.innerText = 'Edge Mode (Offline)';
      netBadge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1.5 transition-colors';
      if (netIndicatorDot) netIndicatorDot.className = 'w-2 h-2 rounded-full bg-rose-400';
    } else {
      updateNetworkStatus();
    }
  });
}

function updateNetworkStatus() {
  if (isSimulatingOffline) return; 
  const isOnline = navigator.onLine;
  netStatusText.innerText = isOnline ? 'Online' : 'Offline';
  netBadge.className = isOnline 
    ? 'px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5 transition-colors'
    : 'px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1.5 transition-colors';
  if (netIndicatorDot) {
    netIndicatorDot.className = isOnline ? 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse' : 'w-2 h-2 rounded-full bg-rose-400';
  }
  if (isOnline) triggerOutboxSync();
}
window.addEventListener('online', updateNetworkStatus);
window.addEventListener('offline', updateNetworkStatus);
updateNetworkStatus();

// ==========================================
// 6. Audio Recording Engine
// ==========================================
let audioContext, mediaStream, inputNode, processorNode;
let audioData = [];
let isRecording = false;

voiceBtn.addEventListener('click', async () => {
  if (!isRecording) startRecording();
  else stopRecording();
});

async function startRecording() {
  try {
    stopAllAudio();
    audioData = [];
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    audioContext = new AudioCtx({ sampleRate: 16000 });
    
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    inputNode = audioContext.createMediaStreamSource(mediaStream);
    processorNode = audioContext.createScriptProcessor(4096, 1, 1);
    
    processorNode.onaudioprocess = (e) => {
      if (!isRecording) return;
      audioData.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };
    
    inputNode.connect(processorNode);
    processorNode.connect(audioContext.destination);
    
    isRecording = true;
    feedbackSection.classList.add('hidden');
    voiceBtn.classList.replace('bg-emerald-600', 'bg-rose-600');
    voiceBtn.classList.add('animate-pulse');
    voiceText.innerText = 'Listening... Tap to Stop';
  } catch (err) {
    alert('Microphone access denied: ' + err.message);
  }
}

async function stopRecording() {
  isRecording = false;
  if (processorNode) processorNode.disconnect();
  if (inputNode) inputNode.disconnect();
  if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
  
  voiceBtn.classList.replace('bg-rose-600', 'bg-emerald-600');
  voiceBtn.classList.remove('animate-pulse');
  voiceText.innerText = 'Processing...';

  const wavBlob = encodeWAV(audioData, 16000);
  await sendAudioToServer(wavBlob);
}

function encodeWAV(samplesArrays, sampleRate) {
  let totalLength = samplesArrays.reduce((acc, curr) => acc + curr.length, 0);
  let samples = new Float32Array(totalLength);
  let offset = 0;
  for (let arr of samplesArrays) {
    samples.set(arr, offset);
    offset += arr.length;
  }
  let buffer = new ArrayBuffer(44 + samples.length * 2);
  let view = new DataView(buffer);
  
  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i));
  }
  
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, 'data');
  view.setUint32(40, samples.length * 2, true);
  
  let index = 44;
  for (let i = 0; i < samples.length; i++) {
    let s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(index, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    index += 2;
  }
  return new Blob([view], { type: 'audio/wav' });
}

// ==========================================
// 7. Server Communication (Voice)
// ==========================================
async function sendAudioToServer(blob) {
  const formData = new FormData();
  formData.append('file', blob, 'farmer_voice.wav');
  
  const queryParams = new URLSearchParams({
    lang: langSelect.value,
    temp: currentFieldData.temp,
    moisture: currentFieldData.soilMoisture,
    ndvi: currentFieldData.ndvi,
    edge_mode: isSimulatingOffline
  });

  try {
    const res = await fetch(`/api/v1/voice/hybrid-consult?${queryParams.toString()}`, {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    
    if (data.status === 'success') {
      lastQueryId = "query_" + Date.now();
      appendMessage('user', `"${data.farmer_query}"`);
      
      const botResponse = `[${data.asr_engine} • ${data.llm_engine}]\n\n${data.advisory_regional}`;
      const audioUrl = data.audio_file 
        ? `/api/v1/voice/audio-stream?file=${encodeURIComponent(data.audio_file)}&t=${Date.now()}` 
        : null;

      appendMessage('bot', botResponse, audioUrl);
      feedbackSection.classList.remove('hidden');
    } else {
      alert("Error: " + data.detail);
    }
  } catch (err) {
    appendMessage('bot', "Connection failed. Advisory generated from offline rules.");
  } finally {
    updateUI();
  }
}

function appendMessage(sender, text, audioUrl = null) {
  const msgDiv = document.createElement('div');
  
  if (sender === 'user') {
    msgDiv.className = 'self-end bg-emerald-600 text-white p-3 rounded-xl rounded-tr-none text-xs max-w-[85%] shadow-sm';
    msgDiv.innerText = text;
  } else {
    msgDiv.className = 'self-start bg-slate-800 text-slate-100 border border-slate-700/80 p-3.5 rounded-xl rounded-tl-none text-xs max-w-[85%] whitespace-pre-line shadow-sm space-y-2.5';
    
    const textNode = document.createElement('div');
    textNode.innerText = text;
    msgDiv.appendChild(textNode);

    const actionContainer = document.createElement('div');
    actionContainer.className = 'flex items-center gap-2 pt-1 border-t border-slate-700/60';

    const audioBtn = document.createElement('button');
    audioBtn.className = 'px-2.5 py-1 rounded-md bg-emerald-700 hover:bg-emerald-600 text-white text-[11px] font-medium transition cursor-pointer flex items-center gap-1';
    audioBtn.innerHTML = '🔊 Play';

    audioBtn.addEventListener('click', () => {
      toggleAudioPlayback(audioBtn, audioUrl, text);
    });

    actionContainer.appendChild(audioBtn);
    msgDiv.appendChild(actionContainer);
  }

  chatContainer.appendChild(msgDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ==========================================
// 8. Offline RLHF Sync Logic
// ==========================================
window.submitFeedback = async function(rating) {
  feedbackSection.classList.add('hidden'); 
  
  const feedbackData = {
    queryId: lastQueryId,
    rating: rating,
    status: 'PENDING',
    timestamp: Date.now()
  };

  await db.outbox.add(feedbackData);
  triggerOutboxSync();
};

async function triggerOutboxSync() {
  if (!navigator.onLine && !isSimulatingOffline) return; 

  const pendingItems = await db.outbox.where({ status: 'PENDING' }).toArray();
  if (pendingItems.length === 0) return;

  for (const item of pendingItems) {
    try {
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item)
      });
      await db.outbox.update(item.id, { status: 'SYNCED' });
    } catch (err) {
      break;
    }
  }
}

// ==========================================
// 9. Vision AI (Camera)
// ==========================================
const cameraBtn = document.getElementById('camera-btn');
const cameraInput = document.getElementById('camera-input');

if (cameraBtn && cameraInput) {
  cameraBtn.addEventListener('click', () => {
    cameraInput.click();
  });

  cameraInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    voiceText.innerText = 'Analyzing Image...';
    const objectUrl = URL.createObjectURL(file);
    appendImageMessage('user', objectUrl);

    try {
      const compressedBlob = await compressImage(file, 800, 0.7);
      await sendImageToServer(compressedBlob);
    } catch (err) {
      alert("Image processing failed.");
      updateUI();
    }
  });
}

function compressImage(file, maxWidth, quality) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob((blob) => resolve(blob), 'image/jpeg', quality);
      };
    };
  });
}

async function sendImageToServer(blob) {
  const formData = new FormData();
  formData.append('image', blob, 'crop_scan.jpg');
  formData.append('lang', langSelect.value);
  formData.append('context', JSON.stringify({
    location: "Bhubaneswar",
    landSize: "2 Acres",
    crops: "Paddy",
    irrigation: "Canal",
    soilType: "Alluvial"
  }));

  try {
    const res = await fetch(`/api/chat`, {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    
    if (data.status === 'success') {
      lastQueryId = "img_" + Date.now();
      const botResponse = `[Qwen2.5-VL Edge Vision]\n\n${data.reply}`;
      appendMessage('bot', botResponse, null);
      feedbackSection.classList.remove('hidden');
    }
  } catch (err) {
    appendMessage('bot', "Vision AI connection failed. Please check network.");
  } finally {
    updateUI(); 
  }
}

function appendImageMessage(sender, imageUrl) {
  const msgDiv = document.createElement('div');
  msgDiv.className = sender === 'user'
    ? 'self-end bg-emerald-600 p-2 rounded-xl rounded-tr-none max-w-[70%] shadow-sm'
    : 'self-start bg-slate-800 p-2 rounded-xl rounded-tl-none max-w-[70%] shadow-sm';
  
  const img = document.createElement('img');
  img.src = imageUrl;
  img.className = 'rounded-lg w-full object-cover max-h-48';
  
  msgDiv.appendChild(img);
  chatContainer.appendChild(msgDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
// ==========================================
// 10. Market Predictor Graph (Chart.js)
// ==========================================
let marketChartInstance = null;

document.getElementById('predict-btn').addEventListener('click', async () => {
  const commodity = document.getElementById('market-commodity').value;
  const btn = document.getElementById('predict-btn');
  const resultText = document.getElementById('pred-result');
  
  btn.innerText = "Loading...";
  
  try {
    const res = await fetch(`/api/v1/market/predict?commodity=${commodity}`);
    const json = await res.json();
    
    if (json.status === 'success') {
      const data = json.data;
      resultText.innerText = `Target Modal Rate: ₹${data.predicted_price_qtl} / Quintal`;
      
      // Destroy old graph if it exists
      if (marketChartInstance) {
        marketChartInstance.destroy();
      }

      // Draw new Graph
      const ctx = document.getElementById('marketChart').getContext('2d');
      marketChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.trend_dates,
          datasets: [{
            label: `${commodity} Price Trend (₹)`,
            data: data.trend_prices,
            borderColor: '#6366f1', // Indigo color
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointRadius: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94a3b8', font: { size: 9 } }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8', font: { size: 9 } }, grid: { color: '#334155' } }
          }
        }
      });
    }
  } catch (err) {
    resultText.innerText = "Failed to fetch prediction.";
  } finally {
    btn.innerText = "Predict 30-Day Trend";
  }
});
// --- AUTO-CLEAR CACHE ON RELOAD (DEVELOPMENT) ---
(async function clearDevCache() {
  if ('caches' in window) {
    const cacheNames = await caches.keys();
    for (const name of cacheNames) {
      if (name.includes('annadata') || name.includes('edge')) {
        await caches.delete(name);
      }
    }
  }
})();