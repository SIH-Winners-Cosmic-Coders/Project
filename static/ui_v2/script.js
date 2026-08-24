// Add at the very start of app_shell.html / script.js
(function seedDefaultState() {
  if (!localStorage.getItem('annadata_user_profile')) {
    localStorage.setItem('annadata_user_profile', JSON.stringify({
      name: "Swayam Swastik Sahoo",
      location: "Bhubaneswar, Odisha",
      farm_size: "12.5 Acres",
      crop: "Paddy (Rice / Dhaan)"
    }));
  }
  if (!localStorage.getItem('annadata_global_lang')) {
    localStorage.setItem('annadata_global_lang', 'en');
  }
})();
// static/ui_v2/script.js
(function () {
  const routes = {
    login_signup_refined: 'login_signup_refined',
    home: 'home_dashboard',
    home_dashboard: 'home_dashboard',
    map: 'farm_map_simplified_footer',
    farm_map_simplified_footer: 'farm_map_simplified_footer',
    crop_history: 'crop_history',
    ai_assistant: 'ai_assistant',
    profile_settings: 'profile_settings',
    irrigation: 'irrigation',
    scan_leaf: 'scan_leaf',
    weather: 'weather',
    alerts: 'alerts',
    // Added Soil Route!
    soil_nutrients: 'soil_nutrients'
  };

  window.navigateTo = function(target) {
    if (routes[target]) show(routes[target]);
  };

  function show(folder, push = true) {
    const targetId = 'page_' + folder;
    const frame = document.getElementById(targetId);
    if (!frame) return;

    document.querySelectorAll('.stitch-page').forEach(f => f.style.display = 'none');
    frame.style.display = 'block';

    if (push) {
      const hash = folder === 'login_signup_refined' ? '#login' : '#' + folder;
      if (location.hash !== hash) history.pushState({ folder }, '', hash);
    }
  }

  window.addEventListener('message', e => {
    if (e.data && e.data.type === 'navigate' && e.data.target) {
      if (routes[e.data.target]) {
        show(routes[e.data.target]);
      }
    }
  });

  window.addEventListener('popstate', () => {
    const h = location.hash.replace(/^#/, '');
    const target = h === 'login' ? 'login_signup_refined' : h;
    if (document.getElementById('page_' + target)) show(target, false);
  });

  const initial = location.hash.replace(/^#/, '');
  if (initial && document.getElementById('page_' + (initial === 'login' ? 'login_signup_refined' : initial))) {
    show(initial === 'login' ? 'login_signup_refined' : initial, false);
  } else {
    show('login_signup_refined', false);
  }
})();