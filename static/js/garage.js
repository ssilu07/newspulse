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

  // Self-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGarage);
  } else {
    initGarage();
  }
})();
