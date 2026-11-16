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
    'mahindra-thar-roxx': {
      name: 'Mahindra Thar Roxx 4x4',
      type: '2.0L mStallion Turbo-Petrol',
      hp: 177,
      zeroToSixty: 9.80,
      quarterMile: 16.90,
      trapSpeed: 82,
      topSpeed: 160,
      color: '#ea580c',
      badge: '🚙 4x4'
    },
    'mahindra-scorpio-n': {
      name: 'Mahindra Scorpio-N',
      type: '2.2L mHawk CRDe Diesel',
      hp: 175,
      zeroToSixty: 10.10,
      quarterMile: 17.20,
      trapSpeed: 80,
      topSpeed: 165,
      color: '#f59e0b',
      badge: '🚙 SUV'
    },
    'tata-safari': {
      name: 'Tata Safari Dark Edition',
      type: '2.0L Kryotec Diesel',
      hp: 170,
      zeroToSixty: 10.40,
      quarterMile: 17.40,
      trapSpeed: 79,
      topSpeed: 175,
      color: '#38bdf8',
      badge: '🚙 7-Seater'
    },
    'mahindra-xuv700': {
      name: 'Mahindra XUV 7XO / 700',
      type: '2.0L mStallion Turbo-Petrol',
      hp: 200,
      zeroToSixty: 8.80,
      quarterMile: 16.20,
      trapSpeed: 87,
      topSpeed: 195,
      color: '#10b981',
      badge: '🚙 Flagship'
    },
    'toyota-fortuner': {
      name: 'Toyota Fortuner GR-Sport 4x4',
      type: '2.8L Turbo Diesel 4WD',
      hp: 204,
      zeroToSixty: 10.20,
      quarterMile: 17.10,
      trapSpeed: 81,
      topSpeed: 180,
      color: '#ef4444',
      badge: '🚙 4WD'
    },
    'tata-nexon-ev': {
      name: 'Tata Nexon.ev Long Range',
      type: 'Permanent Magnet AC EV',
      hp: 143,
      zeroToSixty: 8.90,
      quarterMile: 16.50,
      trapSpeed: 85,
      topSpeed: 150,
      color: '#06b6d4',
      badge: '⚡ Electric'
    },
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

    // --- SETUP RTO CHALLAN WIZARD ---
    initChallanWizard(section);

    // --- SETUP NGT EXPIRY & NOC ALERT ---
    initNgtAlert(section);

    // --- SETUP TRIP FUEL & TOLL CALCULATOR ---
    initTripCalculator(section);

    // --- SETUP DAILY DRIVER QUIZ ---
    initQuizWidget(section);

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

  // --- SETUP EV VS GAS CALCULATOR (Indian Market INR Metrics) ---
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

    // EV Model Presets (kWh per 100 km on Indian road conditions)
    const EV_PRESETS = {
      'tata-nexon': 13.5,     // Tata Nexon.ev (Best Seller)
      'tata-punch': 12.8,     // Tata Punch.ev (Compact City EV)
      'mg-zs': 15.2,          // MG ZS EV (Premium Crossover)
      'byd-seal': 15.5,       // BYD Seal (AWD Sedan)
      'mahindra-xuv400': 14.8 // Mahindra XUV400
    };

    function recalculate() {
      const commuteKm = parseFloat(dailyCommuteInput.value) || 35;
      const kmpl = parseFloat(gasMpgInput.value) || 14;
      const fuelPricePerLitre = parseFloat(gasPriceInput.value) || 96.50;
      const electricityPricePerKwh = parseFloat(electPriceInput.value) || 7.50;
      const evKwhPer100Km = EV_PRESETS[evPresetSelect ? evPresetSelect.value : 'tata-nexon'] || 13.5;

      // Update slider badges
      if (commuteValueDisplay) commuteValueDisplay.textContent = `${commuteKm} km`;
      if (mpgValueDisplay) mpgValueDisplay.textContent = `${kmpl} kmpl`;
      if (gasPriceValueDisplay) gasPriceValueDisplay.textContent = `₹${fuelPricePerLitre.toFixed(2)}/L`;
      if (electPriceValueDisplay) electPriceValueDisplay.textContent = `₹${electricityPricePerKwh.toFixed(2)}/unit`;

      // Monthly distance (30.4 days avg)
      const monthlyKm = commuteKm * 30.4;
      const yearlyKm = commuteKm * 365;

      // Fuel Cost in Rupees (Petrol / Diesel)
      const monthlyFuelLitres = monthlyKm / kmpl;
      const monthlyGasCost = monthlyFuelLitres * fuelPricePerLitre;
      const yearlyGasCost = (yearlyKm / kmpl) * fuelPricePerLitre;

      // EV Charging Cost in Rupees
      const monthlyKwh = (monthlyKm / 100) * evKwhPer100Km;
      const monthlyEvCost = monthlyKwh * electricityPricePerKwh;
      const yearlyEvCost = ((yearlyKm / 100) * evKwhPer100Km) * electricityPricePerKwh;

      // Direct Rupee Savings
      const monthlySavings = Math.max(0, monthlyGasCost - monthlyEvCost);
      const fiveYearSavings = monthlySavings * 60;
      const fiveYearLakhs = (fiveYearSavings / 100000).toFixed(2);

      // CO2 reduction (approx 2.31 kg CO2 per litre of petrol burned minus clean grid factor)
      const annualGasCo2Kg = (yearlyKm / kmpl) * 2.31;
      const annualEvCo2Kg = ((yearlyKm / 100) * evKwhPer100Km) * 0.72; // India grid average kg CO2/kWh
      const annualCo2SavedKg = Math.max(0, annualGasCo2Kg - annualEvCo2Kg);
      const treesEquivalent = Math.round(annualCo2SavedKg / 22); // ~22 kg CO2 absorbed per mature tree/yr

      // Home Charging Time (assuming standard 3.3 kW home wall socket / 7.2 kW AC box)
      const dailyKwh = (commuteKm / 100) * evKwhPer100Km;
      const chargingHours = (dailyKwh / 3.3).toFixed(1);

      // Render outputs in Indian Rupees (₹)
      const monthlyEl = document.getElementById('calcMonthlySavings');
      const fiveYearEl = document.getElementById('calc5YearSavings');
      const co2El = document.getElementById('calcCo2Saved');
      const treesEl = document.getElementById('calcTreesSaved');
      const chargeEl = document.getElementById('calcChargeTime');

      if (monthlyEl) monthlyEl.textContent = `₹${Math.round(monthlySavings).toLocaleString('en-IN')}`;
      if (fiveYearEl) fiveYearEl.textContent = `₹${fiveYearLakhs} Lakh`;
      if (co2El) co2El.textContent = `${Math.round(annualCo2SavedKg).toLocaleString('en-IN')} kg`;
      if (treesEl) treesEl.textContent = `~${treesEquivalent} trees planted`;
      if (chargeEl) chargeEl.textContent = `${chargingHours} hrs / night`;
    }

    [dailyCommuteInput, gasMpgInput, gasPriceInput, electPriceInput, evPresetSelect].forEach(el => {
      if (el) el.addEventListener('input', recalculate);
    });

    recalculate();
  }


  // ==============================================================================
  // 1. RTO CHALLAN & TRAFFIC FINE DIRECTORY WIZARD
  // ==============================================================================
  const CHALLANS = {
    'sunfilm': {
      section: 'Section 190(2) & CMVR Rule 100',
      court: 'Compoundable / Police & Virtual Court',
      fine1: '₹10,000',
      fine2: '₹10,000 + Strip Film on Spot',
      licenseRisk: '⚠️ License suspension: Up to 3 months in repeat cases',
      step1: 'Light Meter Requirement: Delhi High Court & Supreme Court guidelines mandate that traffic police must use an approved VLT Lux Meter. Any visual naked-eye assumption can be challenged.',
      step2: 'Permissible Limits: Front/Rear windscreens must have minimum 70% visual light transmission (VLT); side door glasses require minimum 50% VLT.',
      step3: 'Virtual Court Appeal: If challan is issued for company-fitted dark green tinted glass (complying with Rule 100), upload ARAI certificate copy on vcourts.gov.in.'
    },
    'exhaust': {
      section: 'Section 190(2) & Section 182A(4)',
      court: 'Non-Compoundable / Court & Vehicle Seizure',
      fine1: '₹10,000',
      fine2: '₹10,000 + Vehicle Impounded',
      licenseRisk: '🚨 High Risk: RC cancellation notice sent to registering RTO',
      step1: 'Decibel Limits: CMVR Rule 120 permits maximum 80-85 dB noise for passenger cars and two-wheelers. Cops must use a calibrated decibel (dB) meter at 0.5m distance.',
      step2: 'Manufacturer Certification: Retain original stock exhaust invoice if running an ARAI-homologated aftermarket unit (with DB killer intact).',
      step3: 'Court Disposal: Aftermarket straight-pipe exhausts must be replaced with stock muffler before presenting the vehicle before the Metropolitan Magistrate.'
    },
    'overspeed': {
      section: 'Section 183(1) & (2) MV Act',
      court: 'Online e-Challan / Virtual Court',
      fine1: '₹1,000 - ₹2,000 (LMV Car)',
      fine2: '₹2,000 - ₹4,000 (Repeat Offense)',
      licenseRisk: '⚠️ 2nd offense in Delhi/NCR: Mandatory driving refresher course',
      step1: 'Check Radar Speed Calibration: Interceptor speed guns must possess valid annual calibration certificates. Check photo angle on echallan.parivahan.gov.in.',
      step2: 'Signage Verification: Speed cameras without clear speed-limit signboards within 500 meters are legally contestable under Section 116 MV Act.',
      step3: 'Virtual Court Settlement: Log into vcourts.gov.in with challan number and OTP to plead guilty with 50% reduced fine or contest before the Virtual Judge.'
    },
    'redlight': {
      section: 'Section 184(c) Dangerous Driving',
      court: 'Virtual Court / Traffic Hearing',
      fine1: '₹1,000 - ₹5,000',
      fine2: '₹10,000 + Court Hearing',
      licenseRisk: '🚨 License Suspended: 3 Months mandatory under Supreme Court Committee on Road Safety',
      step1: 'Stop Line Review: If yellow light transition was under 3 seconds or stop-line camera triggered while clearing intersection, request CCTV footage review.',
      step2: 'Emergency Yield Exemption: If you moved past the stop line to give way to an Ambulance or Fire Engine, file grievance with dashcam clip for zero-fine dismissal.',
      step3: 'DL Impound Notice: Ensure you appear within 30 days before the Virtual Court or your driving licence status will be flagged as "Suspended" on Sarathi.'
    },
    'hsrp': {
      section: 'Section 192 & Rule 50 CMVR',
      court: 'Compoundable on Spot / Online',
      fine1: '₹5,000',
      fine2: '₹10,000',
      licenseRisk: '⚠️ Fitness Certificate & Pollution certificate blocked',
      step1: 'Proof of Booking: If your HSRP is ordered on bookmyhsrp.com or makemyhsrp.com, show the active booking receipt and appointment slip to claim exemption.',
      step2: 'Color-Coded Fuel Sticker: Diesel (Orange), Petrol/CNG (Light Blue), EV (Green) stickers on front windshield are mandatory along with high-security plates.',
      step3: 'Third-Party Replacement: If HSRP is broken or stolen, register a lost property e-FIR online before applying for replacement to prevent unauthorized misuse.'
    },
    'seatbelt': {
      section: 'Section 194B MV Act (Front & Rear)',
      court: 'Compoundable on Spot / e-Challan',
      fine1: '₹1,000 per passenger',
      fine2: '₹1,000 per passenger',
      licenseRisk: 'ℹ️ No direct license suspension, but recorded in Sarathi driver record',
      step1: 'Rear Seatbelt Mandate: All passengers in rear seats must wear three-point seatbelts on national highways and expressways as per MoRTH notification.',
      step2: 'Child Restraint System (CRS): Children below 14 years must be secured with child booster seat or seatbelt harness.',
      step3: 'Camera Verification: AI cameras with seatbelt detection look for black/grey diagonal straps; ensure jacket/clothing does not obstruct visibility of belt.'
    },
    'drunk': {
      section: 'Section 185 Motor Vehicles Act',
      court: 'NON-COMPOUNDABLE / Magistrate Court & Jail',
      fine1: '₹10,000 or up to 6 months Jail',
      fine2: '₹15,000 or up to 2 years Jail',
      licenseRisk: '🚨 MANDATORY 6 to 12 Months Driving License Suspension',
      step1: 'Breath Analyzer Breath Test: Legally actionable only when blood alcohol content (BAC) exceeds 30 mg per 100 ml blood. Ask for a clean disposable straw.',
      step2: 'Hospital Blood Test: You have the constitutional right to demand a medical blood test at a registered government hospital within 2 hours of arrest.',
      step3: 'Court Appearance: Vehicle is immediately seized; release can only be ordered by the Duty Magistrate after posting bail and fine.'
    },
    'mobile': {
      section: 'Section 184(c) Hazardous Use of Mobile',
      court: 'Virtual Court / Traffic Police',
      fine1: '₹1,000 - ₹5,000',
      fine2: '₹10,000',
      licenseRisk: '⚠️ License suspension: 3 Months for dangerous driving',
      step1: 'Dashboard Mount Permitted: MoRTH guidelines clarify that navigation-only mobile usage on a secure dashboard/windscreen phone mount is NOT illegal.',
      step2: 'Handheld vs Handsfree: Holding phone in hand while vehicle is stopped at a traffic signal is still treated as driving under the Act.',
      step3: 'Contesting in Court: If AI camera flagged touching your ear or scratching face as phone use, submit dashcam/cabin-cam recording on vcourts.gov.in.'
    },
    'pucc': {
      section: 'Section 190(2) Environmental Violation',
      court: 'Virtual Court / Transport Dept',
      fine1: '₹10,000',
      fine2: '₹10,000 + 3 Months License Suspension',
      licenseRisk: '🚨 3 Months driving license suspension mandatory',
      step1: '7-Day Grace Period: In several states, producing a valid PUCC obtained within 7 days of notice allows reduction of fine before the Virtual Court.',
      step2: 'Central Parivahan Linking: Always ensure the testing center successfully uploads the PUCC to the Parivahan national portal; paper slip alone is insufficient.',
      step3: 'Insurance Claim Block: Without a valid PUCC at the time of accident, insurance companies may repudiate own-damage (OD) claims.'
    },
    'highbeam': {
      section: 'Section 177 / CMVR Rule 106',
      court: 'Compoundable on Spot',
      fine1: '₹500',
      fine2: '₹1,500',
      licenseRisk: 'ℹ️ Warning points on driving license',
      step1: 'City Limits Ban: Using high-beam headlights on illuminated municipal roads is illegal and endangers oncoming drivers.',
      step2: 'Roof Lightbars Seizure: Any auxiliary lights mounted above bonnet level must be kept covered with opaque caps while plying on public roads.',
      step3: 'Wattage Restriction: Maximum allowed bulb wattage is 55/60W (Halogen); LED bulbs exceeding original headlight lumen specifications are illegal.'
    },
    'helmet': {
      section: 'Section 194D MV Act (Rider & Pillion)',
      court: 'Compoundable on Spot / e-Challan',
      fine1: '₹1,000',
      fine2: '₹1,000 + 3 Months License Suspension',
      licenseRisk: '🚨 3 Months Driving License Suspension for repeat or no-ISI helmet',
      step1: 'ISI Mark Requirement: Under BIS standard IS 4151:2015, wearing non-ISI construction/industrial or half-face open helmets invites the same ₹1,000 fine.',
      step2: 'Strap Chinstrap Fastened: If the helmet strap is unbuckled, it is treated as riding without a helmet under Section 194D.',
      step3: 'Pillion Rider Exemption Myth: Both rider and pillion (above 4 years old) are equally required by law to wear helmets across all Indian states.'
    },
    'insurance': {
      section: 'Section 196 Motor Vehicles Act',
      court: 'Non-Compoundable / Court & Vehicle Seizure',
      fine1: '₹2,000 or up to 3 months Jail',
      fine2: '₹4,000 or up to 3 months Jail',
      licenseRisk: '🚨 Vehicle impounded on spot until insurance is produced',
      step1: 'Third-Party Mandatory: Comprehensive own-damage is optional, but Third-Party (TP) insurance is mandatory under law for all motorized vehicles.',
      step2: 'Instant Online Renewal: You can renew policy on your phone through IIB/mParivahan and show valid digital policy copy to the officer to release vehicle.',
      step3: 'Court Fine Payment: Once impounded, take original policy copy to the Traffic ACP/Metropolitan Court to get vehicle release memo.'
    }
  };

  function initChallanWizard(section) {
    const select = document.getElementById('challanOffenseSelect');
    const secEl = document.getElementById('challanSection');
    const courtEl = document.getElementById('challanCourtStatus');
    const fine1El = document.getElementById('challanFirstFine');
    const fine2El = document.getElementById('challanRepeatFine');
    const riskEl = document.getElementById('challanLicenseRisk');
    const s1Title = document.getElementById('step1Title');
    const s1Desc = document.getElementById('step1Desc');
    const s2Title = document.getElementById('step2Title');
    const s2Desc = document.getElementById('step2Desc');
    const s3Title = document.getElementById('step3Title');
    const s3Desc = document.getElementById('step3Desc');
    const shareBtn = document.getElementById('challanShareBtn');

    if (!select) return;

    function update() {
      const off = CHALLANS[select.value] || CHALLANS['sunfilm'];
      if (secEl) secEl.textContent = off.section;
      if (courtEl) courtEl.textContent = off.court;
      if (fine1El) fine1El.textContent = off.fine1;
      if (fine2El) fine2El.textContent = off.fine2;
      if (riskEl) riskEl.textContent = off.licenseRisk;
      
      const s1Parts = off.step1.split(': ');
      if (s1Title) s1Title.textContent = s1Parts[0] + ': ';
      if (s1Desc) s1Desc.textContent = s1Parts[1] || '';

      const s2Parts = off.step2.split(': ');
      if (s2Title) s2Title.textContent = s2Parts[0] + ': ';
      if (s2Desc) s2Desc.textContent = s2Parts[1] || '';

      const s3Parts = off.step3.split(': ');
      if (s3Title) s3Title.textContent = s3Parts[0] + ': ';
      if (s3Desc) s3Desc.textContent = s3Parts[1] || '';
    }

    select.addEventListener('change', update);
    update();

    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        const off = CHALLANS[select.value] || CHALLANS['sunfilm'];
        const text = `🚨 *Traffic Police Alert (${off.section})*\nFine: ${off.fine1} (1st Offense) | ${off.fine2} (Repeat)\n${off.licenseRisk}\n\nCheck official defense rights & dispute guide here:\nhttps://newsseconds.com/#interactiveGarage`;
        const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
        window.open(waUrl, '_blank');
      });
    }
  }

  // ==============================================================================
  // 2. NGT 10-YEAR DIESEL / 15-YEAR PETROL EXPIRY ALERT & NOC WIZARD
  // ==============================================================================
  function initNgtAlert(section) {
    const fuelBtns = section.querySelectorAll('.fuel-toggle-btn');
    const monthSelect = document.getElementById('regMonth');
    const yearSelect = document.getElementById('regYear');
    const badgeEl = document.getElementById('ngtStatusBadge');
    const daysEl = document.getElementById('ngtDaysLeft');
    const expiryEl = document.getElementById('ngtExpiryDate');
    const shareBtn = document.getElementById('ngtShareBtn');

    if (!monthSelect || !yearSelect) return;

    let selectedFuel = 'diesel';

    // Populate registration years (2005 - 2026)
    yearSelect.innerHTML = '';
    const currentYear = new Date().getFullYear();
    for (let y = currentYear; y >= 2005; y--) {
      const opt = document.createElement('option');
      opt.value = y;
      opt.textContent = y;
      if (y === currentYear - 7) opt.selected = true; // default ~7 yrs old
      yearSelect.appendChild(opt);
    }

    fuelBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        fuelBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedFuel = btn.getAttribute('data-fuel');
        calculate();
      });
    });

    function calculate() {
      const m = parseInt(monthSelect.value, 10) - 1;
      const y = parseInt(yearSelect.value, 10);
      const regDate = new Date(y, m, 1);
      
      const maxYears = (selectedFuel === 'diesel') ? 10 : 15;
      const expiryDate = new Date(y + maxYears, m, 1);
      const now = new Date();

      const diffMs = expiryDate - now;
      const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

      const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
      const expiryStr = `Expiry Deadline: ${monthNames[m]} ${y + maxYears}`;

      if (expiryEl) expiryEl.textContent = expiryStr;

      if (diffDays <= 0) {
        if (badgeEl) {
          badgeEl.textContent = '🚨 IMPOUND RISK (EXPIRED - NGT BANNED)';
          badgeEl.className = 'ngt-status-badge expired';
        }
        if (daysEl) daysEl.textContent = '0';
      } else if (diffDays <= 180) {
        if (badgeEl) {
          badgeEl.textContent = '⚠️ EXPIRING IN < 6 MONTHS (APPLY NOC NOW)';
          badgeEl.className = 'ngt-status-badge warning';
        }
        if (daysEl) daysEl.textContent = diffDays.toLocaleString('en-IN');
      } else {
        if (badgeEl) {
          badgeEl.textContent = '✅ ACTIVE & ROAD LEGAL IN NCR';
          badgeEl.className = 'ngt-status-badge';
        }
        if (daysEl) daysEl.textContent = diffDays.toLocaleString('en-IN');
      }
    }

    monthSelect.addEventListener('change', calculate);
    yearSelect.addEventListener('change', calculate);
    calculate();

    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        const days = daysEl ? daysEl.textContent : '0';
        const fuel = selectedFuel.toUpperCase();
        const text = `⏳ *Delhi-NCR NGT Alert*: My ${fuel} vehicle has *${days} days left* before mandatory deregistration.\n\nCheck your car expiry and 4-step NOC transfer protocol:\nhttps://newsseconds.com/#interactiveGarage`;
        const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
        window.open(waUrl, '_blank');
      });
    }
  }

  // ==============================================================================
  // 3. HIGHWAY TRIP FUEL & FASTAG TOLL COST CALCULATOR
  // ==============================================================================
  function initTripCalculator(section) {
    const routeChips = section.querySelectorAll('.route-chip');
    const distSlider = document.getElementById('tripDistance');
    const distVal = document.getElementById('tripDistVal');
    const vehicleSelect = document.getElementById('tripVehicleType');
    const tollInput = document.getElementById('tripTollInput');
    const totalCostEl = document.getElementById('tripTotalCost');
    const perKmEl = document.getElementById('tripCostPerKm');
    const fuelExpEl = document.getElementById('tripFuelExpense');
    const tollExpEl = document.getElementById('tripTollExpense');
    const unitsEl = document.getElementById('tripFuelUnits');
    const evCostEl = document.getElementById('tripEvCost');
    const shareBtn = document.getElementById('tripShareBtn');

    if (!distSlider || !vehicleSelect) return;

    const VEHICLE_SPECS = {
      'petrol-compact': { efficiency: 15.0, price: 96.50, unit: 'Litres', name: 'Petrol Car' },
      'diesel-suv': { efficiency: 12.0, price: 89.50, unit: 'Litres', name: 'Diesel SUV' },
      'strong-hybrid': { efficiency: 22.0, price: 96.50, unit: 'Litres', name: 'Hybrid Car' },
      'cng-car': { efficiency: 23.0, price: 76.00, unit: 'kg', name: 'CNG Vehicle' },
      'electric-suv': { efficiency: 6.67, price: 7.50, unit: 'kWh', name: 'Electric SUV' } // ~15 kWh/100km = 6.67 km/kWh
    };

    function recalculate() {
      const distance = parseFloat(distSlider.value) || 280;
      const toll = parseFloat(tollInput ? tollInput.value : 0) || 0;
      const vKey = vehicleSelect.value;
      const spec = VEHICLE_SPECS[vKey] || VEHICLE_SPECS['diesel-suv'];

      if (distVal) distVal.textContent = `${distance} km`;

      let fuelUnits = distance / spec.efficiency;
      let fuelCost = fuelUnits * spec.price;
      let totalTrip = fuelCost + toll;
      let costPerKm = totalTrip / distance;

      // Electric equivalent for comparison
      const evUnits = (distance / 100) * 15;
      const evCost = (evUnits * 7.50) + toll;
      const evSaved = Math.max(0, totalTrip - evCost);

      if (totalCostEl) totalCostEl.textContent = `₹${Math.round(totalTrip).toLocaleString('en-IN')}`;
      if (perKmEl) perKmEl.textContent = `₹${costPerKm.toFixed(2)} / km`;
      if (fuelExpEl) fuelExpEl.textContent = `₹${Math.round(fuelCost).toLocaleString('en-IN')}`;
      if (tollExpEl) tollExpEl.textContent = `₹${Math.round(toll).toLocaleString('en-IN')}`;
      if (unitsEl) unitsEl.textContent = `${fuelUnits.toFixed(1)} ${spec.unit}`;
      if (evCostEl) evCostEl.textContent = `₹${Math.round(evCost).toLocaleString('en-IN')} (Save ₹${Math.round(evSaved).toLocaleString('en-IN')})`;
    }

    routeChips.forEach(chip => {
      chip.addEventListener('click', () => {
        routeChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const km = chip.getAttribute('data-km');
        const toll = chip.getAttribute('data-toll');
        if (km && distSlider) distSlider.value = km;
        if (toll && tollInput) tollInput.value = toll;
        recalculate();
      });
    });

    distSlider.addEventListener('input', recalculate);
    if (tollInput) tollInput.addEventListener('input', recalculate);
    vehicleSelect.addEventListener('change', recalculate);
    recalculate();

    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        const dist = distSlider.value;
        const total = totalCostEl ? totalCostEl.textContent : '';
        const perKm = perKmEl ? perKmEl.textContent : '';
        const text = `🛣️ *Highway Trip Cost Estimate*: ${dist} km highway drive costs *${total}* (${perKm}) including FASTag tolls.\n\nCalculate fuel & tolls for your exact car:\nhttps://newsseconds.com/#interactiveGarage`;
        const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
        window.open(waUrl, '_blank');
      });
    }
  }

  // ==============================================================================
  // 4. DAILY INDIAN DRIVER & RTO QUIZ WIDGET WITH CONFETTI
  // ==============================================================================
  function initQuizWidget(section) {
    const qText = document.getElementById('quizQuestionText');
    const optList = document.getElementById('quizOptionsList');
    const fbBox = document.getElementById('quizFeedbackBox');
    const fbTitle = document.getElementById('feedbackTitle');
    const fbDesc = document.getElementById('feedbackDesc');
    const nextBtn = document.getElementById('quizNextBtn');
    const progressFill = document.getElementById('quizProgressFill');
    const qNumEl = document.getElementById('quizQNum');
    const scoreBadge = document.getElementById('quizScoreBadge');
    const completeBox = document.getElementById('quizCompleteBox');
    const compTitle = document.getElementById('completeTitle');
    const compDesc = document.getElementById('completeDesc');
    const retryBtn = document.getElementById('quizRetryBtn');
    const shareBtn = document.getElementById('quizShareBtn');
    const canvas = document.getElementById('confettiCanvas');

    if (!qText || !optList) return;

    const QUIZ_QUESTIONS = [
      {
        q: 'Under CMVR Rule 100, what is the minimum legal Visual Light Transmission (VLT) required for car side window glasses in India?',
        opts: ['25% Transparency', '50% Transparency', '70% Transparency', '85% Transparency'],
        ans: 1,
        exp: 'Correct! Side window glasses must maintain at least 50% transparency, whereas front and rear windscreens require minimum 70% transparency.'
      },
      {
        q: 'What is the maximum permissible speed limit for passenger cars (M1) on 8-lane Access-Controlled Expressways like Delhi-Mumbai NE4?',
        opts: ['100 km/h', '120 km/h', '130 km/h', '140 km/h'],
        ans: 1,
        exp: 'Correct! MoRTH sets the maximum speed limit at 120 km/h for passenger cars on national expressways and 100 km/h on 4-lane highways.'
      },
      {
        q: 'In Delhi-NCR, what is the maximum age limit for Diesel passenger cars under National Green Tribunal (NGT) directives?',
        opts: ['8 Years', '10 Years', '12 Years', '15 Years'],
        ans: 1,
        exp: 'Correct! Under NGT and Supreme Court orders, Diesel vehicles older than 10 years and Petrol vehicles older than 15 years cannot ply in NCR.'
      },
      {
        q: 'Which Section of the Motor Vehicles Act penalizes driving without a valid High Security Registration Plate (HSRP)?',
        opts: ['Section 177', 'Section 184', 'Section 192', 'Section 194B'],
        ans: 2,
        exp: 'Correct! Section 192 penalizes driving without valid registration marks or non-standard number plates with fines up to ₹10,000.'
      },
      {
        q: 'What is the legal blood alcohol concentration (BAC) limit beyond which driving is penalized under Section 185 in India?',
        opts: ['10 mg / 100 ml', '30 mg / 100 ml', '50 mg / 100 ml', '80 mg / 100 ml'],
        ans: 1,
        exp: 'Correct! Blood alcohol exceeding 30 mg per 100 ml blood invites court prosecution, up to ₹10,000 fine, and license suspension.'
      }
    ];

    let currentIdx = 0;
    let score = 0;
    const totalQ = 3;
    let activeQuestions = QUIZ_QUESTIONS.slice(0, totalQ);

    function renderQuestion() {
      if (currentIdx >= totalQ) {
        showResults();
        return;
      }

      const q = activeQuestions[currentIdx];
      if (qText) qText.textContent = q.q;
      if (qNumEl) qNumEl.textContent = `Question ${currentIdx + 1} of ${totalQ}`;
      if (scoreBadge) scoreBadge.textContent = `Score: ${score}`;
      if (progressFill) progressFill.style.width = `${((currentIdx) / totalQ) * 100}%`;

      if (fbBox) fbBox.style.display = 'none';
      if (optList) {
        optList.innerHTML = '';
        optList.style.display = 'flex';
        q.opts.forEach((opt, idx) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'quiz-option-btn';
          btn.textContent = opt;
          btn.addEventListener('click', () => handleAnswer(idx, btn));
          optList.appendChild(btn);
        });
      }
    }

    function handleAnswer(selectedIdx, selectedBtn) {
      const q = activeQuestions[currentIdx];
      const allBtns = optList.querySelectorAll('.quiz-option-btn');
      allBtns.forEach(b => b.disabled = true);

      if (selectedIdx === q.ans) {
        selectedBtn.classList.add('correct');
        score++;
        if (fbTitle) {
          fbTitle.textContent = '🎉 Correct Answer!';
          fbTitle.className = 'feedback-title correct';
        }
      } else {
        selectedBtn.classList.add('wrong');
        allBtns[q.ans]?.classList.add('correct');
        if (fbTitle) {
          fbTitle.textContent = '❌ Incorrect Answer';
          fbTitle.className = 'feedback-title wrong';
        }
      }

      if (fbDesc) fbDesc.textContent = q.exp;
      if (fbBox) fbBox.style.display = 'block';
      if (scoreBadge) scoreBadge.textContent = `Score: ${score}`;
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        currentIdx++;
        renderQuestion();
      });
    }

    function showResults() {
      if (qText) qText.style.display = 'none';
      if (optList) optList.style.display = 'none';
      if (fbBox) fbBox.style.display = 'none';
      if (progressFill) progressFill.style.width = '100%';

      if (completeBox) completeBox.style.display = 'block';

      if (score === 3) {
        if (compTitle) compTitle.textContent = '🏆 Verified RTO Master!';
        if (compDesc) compDesc.textContent = 'Flawless 3/3! You know the Indian Motor Vehicles Act and highway laws better than 95% of drivers.';
        launchConfetti(canvas);
      } else if (score === 2) {
        if (compTitle) compTitle.textContent = '🥈 Street Smart Driver!';
        if (compDesc) compDesc.textContent = `You scored ${score}/3. A solid score, but keep your eye on the latest RTO fine amendments.`;
        launchConfetti(canvas);
      } else {
        if (compTitle) compTitle.textContent = '🥉 Learner Driver';
        if (compDesc) compDesc.textContent = `You scored ${score}/3. Check out the RTO Challan Wizard above to avoid unexpected traffic fines.`;
      }
    }

    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        currentIdx = 0;
        score = 0;
        if (completeBox) completeBox.style.display = 'none';
        if (qText) qText.style.display = 'block';
        renderQuestion();
      });
    }

    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        const text = `🏆 I scored *${score}/3* on today's Indian RTO & Traffic Rules IQ Quiz!\n\nTest your driver IQ and see if you can beat my score:\nhttps://newsseconds.com/#interactiveGarage`;
        const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
        window.open(waUrl, '_blank');
      });
    }

    renderQuestion();
  }

  // Self-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGarage);
  } else {
    initGarage();
  }
})();
