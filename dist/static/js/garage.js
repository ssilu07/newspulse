/**
 * NewsSeconds Interactive Garage Engine
 * - 1/4-Mile Head-to-Head Drag Race Simulator
 * - EV vs Gas Fuel Savings Calculator
 * 100% AdSense Compliant, Zero-dependency, Lightweight Vanilla JS.
 */
(function() {
  'use strict';

  // --- CAR DATABASE (Accurate official specs & 1/4 mile test telemetry) ---
  const CARS = {
    'tesla-plaid': {
      name: 'Tesla Model S Plaid',
      type: 'AWD Tri-Motor EV',
      hp: 1020,
      zeroToSixty: 1.99,
      quarterMile: 9.23,
      trapSpeed: 155,
      topSpeed: 200,
      color: '#06b6d4',
      badge: '⚡ EV'
    },
    'porsche-911-turbo-s': {
      name: 'Porsche 911 Turbo S',
      type: '3.7L Twin-Turbo Flat-6 Gas',
      hp: 640,
      zeroToSixty: 2.60,
      quarterMile: 10.10,
      trapSpeed: 137,
      topSpeed: 205,
      color: '#f59e0b',
      badge: '⛽ Gas'
    },
    'lucid-sapphire': {
      name: 'Lucid Air Sapphire',
      type: 'AWD Tri-Motor EV',
      hp: 1234,
      zeroToSixty: 1.89,
      quarterMile: 8.95,
      trapSpeed: 158,
      topSpeed: 205,
      color: '#8b5cf6',
      badge: '⚡ EV'
    },
    'ferrari-sf90': {
      name: 'Ferrari SF90 Stradale',
      type: '4.0L Twin-Turbo V8 Hybrid',
      hp: 986,
      zeroToSixty: 2.10,
      quarterMile: 9.60,
      trapSpeed: 148,
      topSpeed: 211,
      color: '#ef4444',
      badge: '🔋 Hybrid'
    },
    'lambo-revuelto': {
      name: 'Lamborghini Revuelto',
      type: '6.5L V12 Hybrid AWD',
      hp: 1001,
      zeroToSixty: 2.40,
      quarterMile: 9.70,
      trapSpeed: 149,
      topSpeed: 217,
      color: '#10b981',
      badge: '🔋 Hybrid'
    },
    'rimac-nevera': {
      name: 'Rimac Nevera',
      type: 'Quad-Motor All-Electric',
      hp: 1914,
      zeroToSixty: 1.74,
      quarterMile: 8.25,
      trapSpeed: 175,
      topSpeed: 258,
      color: '#38bdf8',
      badge: '⚡ Hyper EV'
    },
    'corvette-z06': {
      name: 'Chevrolet Corvette Z06 (C8)',
      type: '5.5L Flat-Plane V8 NA Gas',
      hp: 670,
      zeroToSixty: 2.60,
      quarterMile: 10.50,
      trapSpeed: 131,
      topSpeed: 195,
      color: '#fbbf24',
      badge: '⛽ Gas'
    },
    'bmw-m5': {
      name: 'BMW M5 (G90)',
      type: '4.4L Twin-Turbo V8 PHEV',
      hp: 717,
      zeroToSixty: 3.40,
      quarterMile: 10.90,
      trapSpeed: 130,
      topSpeed: 190,
      color: '#3b82f6',
      badge: '🔋 Hybrid'
    },
    'byd-u9': {
      name: 'BYD Yangwang U9',
      type: 'Quad-Motor Super EV',
      hp: 1287,
      zeroToSixty: 2.36,
      quarterMile: 9.78,
      trapSpeed: 150,
      topSpeed: 243,
      color: '#ec4899',
      badge: '⚡ EV'
    },
    'dodge-demon-170': {
      name: 'Dodge Challenger SRT Demon 170',
      type: '6.2L Supercharged HEMI V8',
      hp: 1025,
      zeroToSixty: 1.66,
      quarterMile: 8.91,
      trapSpeed: 151,
      topSpeed: 215,
      color: '#f97316',
      badge: '⛽ Gas'
    }
  };

  // --- AUDIO SYNTHESIZER (Web Audio API - 0 downloads, 100% Policy Safe) ---
  let audioCtx = null;
  let isSoundEnabled = false;

  function initAudio() {
    if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playTone(freq, duration, type, startVol) {
    if (!isSoundEnabled || !audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type || 'sine';
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(startVol || 0.15, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch(e) {}
  }

  function playEngineRoar(startPitch, endPitch, duration) {
    if (!isSoundEnabled || !audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(startPitch, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(endPitch, audioCtx.currentTime + duration);
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch(e) {}
  }

  // --- CONFETTI SYSTEM ---
  function launchConfetti(canvas) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    
    const colors = ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#ffffff'];
    const particles = [];
    for (let i = 0; i < 60; i++) {
      particles.push({
        x: canvas.width / 2,
        y: canvas.height / 2,
        vx: (Math.random() - 0.5) * 12,
        vy: (Math.random() - 0.7) * 12,
        size: Math.random() * 6 + 4,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        vr: (Math.random() - 0.5) * 10,
        alpha: 1
      });
    }

    let frame = 0;
    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let alive = false;
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.25; // gravity
        p.rotation += p.vr;
        p.alpha -= 0.015;
        if (p.alpha > 0) {
          alive = true;
          ctx.save();
          ctx.globalAlpha = p.alpha;
          ctx.translate(p.x, p.y);
          ctx.rotate((p.rotation * Math.PI) / 180);
          ctx.fillStyle = p.color;
          ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
          ctx.restore();
        }
      });
      if (alive && frame < 90) {
        frame++;
        requestAnimationFrame(render);
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
    render();
  }

  // --- INITIALIZE GARAGE MODULE ---
  function initGarage() {
    const section = document.getElementById('interactiveGarage');
    if (!section) return;

    // Tabs Switcher
    const tabBtns = section.querySelectorAll('.garage-tab-btn');
    const tabPanels = section.querySelectorAll('.garage-tab-panel');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const activePanel = document.getElementById(target);
        if (activePanel) activePanel.classList.add('active');
      });
    });

    // Sound Toggle Button
    const soundBtn = document.getElementById('soundToggleBtn');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        initAudio();
        isSoundEnabled = !isSoundEnabled;
        soundBtn.classList.toggle('sound-on', isSoundEnabled);
        soundBtn.innerHTML = isSoundEnabled ? '🔊 Sound: ON' : '🔇 Sound: OFF';
        if (isSoundEnabled) {
          playTone(440, 0.1, 'sine', 0.1);
        }
      });
    }

    // --- SETUP DRAG RACE SIMULATOR ---
    initDragRace(section);

    // --- SETUP EV SAVINGS CALCULATOR ---
    initEvCalculator(section);
  }

  function initDragRace(section) {
    const carASelect = document.getElementById('carASelect');
    const carBSelect = document.getElementById('carBSelect');
    const launchBtn = document.getElementById('launchRaceBtn');
    const carAElement = document.getElementById('carATrack');
    const carBElement = document.getElementById('carBTrack');
    const telemetryA = document.getElementById('telemetryA');
    const telemetryB = document.getElementById('telemetryB');
    const resultBox = document.getElementById('raceResultBox');
    const treeLights = section.querySelectorAll('.tree-light');
    const confettiCanvas = document.getElementById('raceConfettiCanvas');
    const shareBtn = document.getElementById('shareRaceBtn');

    if (!carASelect || !carBSelect || !launchBtn) return;

    // Populate car options
    function populateDropdowns() {
      const keys = Object.keys(CARS);
      carASelect.innerHTML = '';
      carBSelect.innerHTML = '';

      keys.forEach((k, idx) => {
        const car = CARS[k];
        const optA = document.createElement('option');
        optA.value = k;
        optA.textContent = `${car.name} (${car.hp} HP)`;
        if (idx === 0) optA.selected = true; // Tesla Model S Plaid
        carASelect.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = k;
        optB.textContent = `${car.name} (${car.hp} HP)`;
        if (idx === 1) optB.selected = true; // Porsche 911 Turbo S
        carBSelect.appendChild(optB);
      });
    }

    function updateSpecsCards() {
      const carA = CARS[carASelect.value];
      const carB = CARS[carBSelect.value];
      if (!carA || !carB) return;

      // Update name labels
      document.getElementById('carAName').textContent = carA.name;
      document.getElementById('carBName').textContent = carB.name;
      document.getElementById('carAType').textContent = carA.type;
      document.getElementById('carBType').textContent = carB.type;

      // Update Specs table
      document.getElementById('specHpA').textContent = `${carA.hp} HP`;
      document.getElementById('specHpB').textContent = `${carB.hp} HP`;
      document.getElementById('spec060A').textContent = `${carA.zeroToSixty}s`;
      document.getElementById('spec060B').textContent = `${carB.zeroToSixty}s`;
      document.getElementById('specQtrA').textContent = `${carA.quarterMile}s`;
      document.getElementById('specQtrB').textContent = `${carB.quarterMile}s`;
      document.getElementById('specTopA').textContent = `${carA.topSpeed} MPH`;
      document.getElementById('specTopB').textContent = `${carB.topSpeed} MPH`;

      // Highlight best in category
      highlightWinner('specHpA', 'specHpB', carA.hp, carB.hp, true);
      highlightWinner('spec060A', 'spec060B', carA.zeroToSixty, carB.zeroToSixty, false);
      highlightWinner('specQtrA', 'specQtrB', carA.quarterMile, carB.quarterMile, false);
      highlightWinner('specTopA', 'specTopB', carA.topSpeed, carB.topSpeed, true);

      // Reset positions & telemetry
      resetTrack();
    }

    function highlightWinner(idA, idB, valA, valB, higherIsBetter) {
      const elA = document.getElementById(idA);
      const elB = document.getElementById(idB);
      if (!elA || !elB) return;
      elA.classList.remove('spec-winner');
      elB.classList.remove('spec-winner');
      if (valA === valB) return;
      const isAWinner = higherIsBetter ? (valA > valB) : (valA < valB);
      if (isAWinner) elA.classList.add('spec-winner');
      else elB.classList.add('spec-winner');
    }

    function resetTrack() {
      if (carAElement) carAElement.style.transform = 'translateX(0%)';
      if (carBElement) carBElement.style.transform = 'translateX(0%)';
      if (telemetryA) telemetryA.textContent = 'Ready (0.0s)';
      if (telemetryB) telemetryB.textContent = 'Ready (0.0s)';
      if (resultBox) resultBox.style.display = 'none';
      treeLights.forEach(l => l.classList.remove('active'));
    }

    let isRacing = false;

    function runRace() {
      if (isRacing) return;
      isRacing = true;
      initAudio();
      resetTrack();
      launchBtn.disabled = true;
      launchBtn.textContent = 'Staging...';

      const carA = CARS[carASelect.value];
      const carB = CARS[carBSelect.value];

      try {
        if (typeof window.gtag === 'function') {
          window.gtag('event', 'drag_race_launch', {
            car_a: carA.name,
            car_b: carB.name
          });
        }
      } catch (e) {}

      // Christmas tree lights countdown
      // Light 1: Amber 1 (400ms)
      setTimeout(() => {
        treeLights[0]?.classList.add('active');
        playTone(350, 0.08, 'sine', 0.15);
      }, 400);

      // Light 2: Amber 2 (800ms)
      setTimeout(() => {
        treeLights[1]?.classList.add('active');
        playTone(350, 0.08, 'sine', 0.15);
      }, 800);

      // Light 3: Amber 3 (1200ms)
      setTimeout(() => {
        treeLights[2]?.classList.add('active');
        playTone(350, 0.08, 'sine', 0.15);
      }, 1200);

      // Light 4: GREEN! GO! (1600ms)
      setTimeout(() => {
        treeLights[3]?.classList.add('active');
        playTone(700, 0.25, 'triangle', 0.25);
        launchBtn.textContent = 'LAUNCHED! ⚡';
        
        // Sound engine roars
        playEngineRoar(120, 480, 2.5);

        // Calculate realistic visual transition duration (scaled: 8s quarter mile ~ 2.4s animation)
        const scale = 0.27; // animation time scaler
        const timeA = carA.quarterMile * scale;
        const timeB = carB.quarterMile * scale;

        // Animate cars across track
        carAElement.style.transition = `transform ${timeA}s cubic-bezier(0.2, 0.8, 0.4, 1)`;
        carBElement.style.transition = `transform ${timeB}s cubic-bezier(0.2, 0.8, 0.4, 1)`;
        carAElement.style.transform = 'translateX(calc(100% - 70px))';
        carBElement.style.transform = 'translateX(calc(100% - 70px))';

        // Telemetry counter
        const startTimestamp = performance.now();
        const durationMax = Math.max(timeA, timeB) * 1000;

        const timer = setInterval(() => {
          const elapsed = (performance.now() - startTimestamp) / 1000;
          const simTimeA = Math.min(carA.quarterMile, (elapsed / scale)).toFixed(2);
          const simTimeB = Math.min(carB.quarterMile, (elapsed / scale)).toFixed(2);
          
          if (telemetryA) telemetryA.textContent = `${simTimeA}s @ ${(carA.trapSpeed * (elapsed / (timeA || 1))).toFixed(0)} mph`;
          if (telemetryB) telemetryB.textContent = `${simTimeB}s @ ${(carB.trapSpeed * (elapsed / (timeB || 1))).toFixed(0)} mph`;

          if (elapsed * 1000 >= durationMax + 100) {
            clearInterval(timer);
            finishRace(carA, carB);
          }
        }, 50);

      }, 1600);
    }

    function finishRace(carA, carB) {
      isRacing = false;
      launchBtn.disabled = false;
      launchBtn.textContent = '🚀 Race Again';

      // Determine Winner
      const diff = Math.abs(carA.quarterMile - carB.quarterMile).toFixed(2);
      let winnerText = '';
      let winnerName = '';

      if (carA.quarterMile < carB.quarterMile) {
        winnerName = carA.name;
        winnerText = `🏆 ${carA.name} WINS by ${diff}s! (1/4 Mile: ${carA.quarterMile}s @ ${carA.trapSpeed} mph)`;
      } else if (carB.quarterMile < carA.quarterMile) {
        winnerName = carB.name;
        winnerText = `🏆 ${carB.name} WINS by ${diff}s! (1/4 Mile: ${carB.quarterMile}s @ ${carB.trapSpeed} mph)`;
      } else {
        winnerText = `🔥 DEAD HEAT TIE! Both finished in ${carA.quarterMile}s!`;
      }

      if (resultBox) {
        resultBox.style.display = 'block';
        document.getElementById('raceResultText').textContent = winnerText;
      }

      // Victory chime & confetti
      playTone(523.25, 0.2, 'sine', 0.2);
      setTimeout(() => playTone(659.25, 0.3, 'sine', 0.25), 150);
      launchConfetti(confettiCanvas);
    }

    // Share button handler
    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        const carA = CARS[carASelect.value];
        const carB = CARS[carBSelect.value];
        const text = `🏎️ I just raced the ${carA.name} against the ${carB.name} on NewsSeconds 1/4-Mile Drag Simulator! Check out who won: https://newsseconds.com/#interactiveGarage`;
        if (navigator.share) {
          navigator.share({ title: 'NewsSeconds Drag Race', text: text, url: 'https://newsseconds.com/#interactiveGarage' }).catch(() => {});
        } else {
          navigator.clipboard.writeText(text).then(() => {
            alert('Race result link copied to clipboard!');
          }).catch(() => {});
        }
      });
    }

    populateDropdowns();
    carASelect.addEventListener('change', updateSpecsCards);
    carBSelect.addEventListener('change', updateSpecsCards);
    launchBtn.addEventListener('click', runRace);
    updateSpecsCards();
  }

  // --- SETUP EV VS GAS CALCULATOR ---
  function initEvCalculator(section) {
    const dailyCommuteInput = document.getElementById('calcCommute');
    const commuteValueDisplay = document.getElementById('commuteVal');
    const gasMpgInput = document.getElementById('calcMpg');
    const mpgValueDisplay = document.getElementById('mpgVal');
    const gasPriceInput = document.getElementById('calcGasPrice');
    const gasPriceValueDisplay = document.getElementById('gasPriceVal');
    const electPriceInput = document.getElementById('calcElectPrice');
    const electPriceValueDisplay = document.getElementById('electPriceVal');
    const evPresetSelect = document.getElementById('evModelPreset');

    if (!dailyCommuteInput || !gasMpgInput) return;

    // EV Model Presets (kWh per 100 miles)
    const EV_PRESETS = {
      'tesla-3': 25,     // Tesla Model 3 RWD / Long Range (High efficiency)
      'tesla-y': 28,     // Tesla Model Y
      'byd-seal': 26,    // BYD Seal
      'hyundai-ioniq5': 29, // Hyundai Ioniq 5
      'rivian-r1t': 45,  // Rivian R1T (Heavy truck)
      'porsche-taycan': 38 // Porsche Taycan
    };

    function recalculate() {
      const commute = parseFloat(dailyCommuteInput.value) || 35;
      const mpg = parseFloat(gasMpgInput.value) || 25;
      const gasPrice = parseFloat(gasPriceInput.value) || 3.60;
      const electPrice = parseFloat(electPriceInput.value) || 0.15;
      const evKwhPer100 = EV_PRESETS[evPresetSelect.value] || 27;

      // Update slider badges
      if (commuteValueDisplay) commuteValueDisplay.textContent = `${commute} miles`;
      if (mpgValueDisplay) mpgValueDisplay.textContent = `${mpg} MPG`;
      if (gasPriceValueDisplay) gasPriceValueDisplay.textContent = `$${gasPrice.toFixed(2)}/gal`;
      if (electPriceValueDisplay) electPriceValueDisplay.textContent = `$${electPrice.toFixed(2)}/kWh`;

      // Monthly distance (30.4 days avg)
      const monthlyMiles = commute * 30.4;
      const yearlyMiles = commute * 365;

      // Gas Cost
      const monthlyGasGallons = monthlyMiles / mpg;
      const monthlyGasCost = monthlyGasGallons * gasPrice;
      const yearlyGasCost = (yearlyMiles / mpg) * gasPrice;

      // EV Cost
      const monthlyKwh = (monthlyMiles / 100) * evKwhPer100;
      const monthlyEvCost = monthlyKwh * electPrice;
      const yearlyEvCost = ((yearlyMiles / 100) * evKwhPer100) * electPrice;

      // Savings
      const monthlySavings = Math.max(0, monthlyGasCost - monthlyEvCost);
      const fiveYearSavings = monthlySavings * 60;

      // CO2 reduction (approx 19.6 lbs CO2 per gallon of gasoline burned minus EV grid mix)
      const annualGasCo2 = (yearlyMiles / mpg) * 19.6;
      const annualEvCo2 = (yearlyMiles / 100) * evKwhPer100 * 0.85; // avg US grid lbs CO2/kWh
      const annualCo2SavedLbs = Math.max(0, annualGasCo2 - annualEvCo2);
      const treesEquivalent = Math.round(annualCo2SavedLbs / 48); // ~48 lbs CO2 absorbed per tree/yr

      // Home Charging Time (7.7 kW Level 2 wallbox)
      const dailyKwh = (commute / 100) * evKwhPer100;
      const chargingHours = (dailyKwh / 7.7).toFixed(1);

      // Render outputs
      document.getElementById('calcMonthlySavings').textContent = `$${Math.round(monthlySavings).toLocaleString()}`;
      document.getElementById('calc5YearSavings').textContent = `$${Math.round(fiveYearSavings).toLocaleString()}`;
      document.getElementById('calcCo2Saved').textContent = `${Math.round(annualCo2SavedLbs).toLocaleString()} lbs`;
      document.getElementById('calcTreesSaved').textContent = `~${treesEquivalent} trees planted`;
      document.getElementById('calcChargeTime').textContent = `${chargingHours} hrs / night`;
    }

    [dailyCommuteInput, gasMpgInput, gasPriceInput, electPriceInput, evPresetSelect].forEach(el => {
      if (el) el.addEventListener('input', recalculate);
    });

    recalculate();
  }

  // Self-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGarage);
  } else {
    initGarage();
  }
})();
