/**
 * NewsPulse - High-Performance Clientside Engine
 * Handles instant search, category filtering, bookmarks, Web Speech TTS, modals, and theme switching.
 */

(function () {
  'use strict';

  // State Management
  const state = {
    activeCategory: 'all',
    searchQuery: '',
    showBookmarksOnly: false,
    bookmarks: JSON.parse(localStorage.getItem('newspulse_bookmarks') || '[]'),
    activeArticle: null,
    speechUtterance: null,
    speakingArticleId: null
  };

  // DOM Elements
  const searchInput = document.getElementById('newsSearchInput');
  const categoryPills = document.querySelectorAll('.cat-pill');
  const bookmarksToggleBtn = document.getElementById('bookmarksToggleBtn');
  const bookmarkCountBadge = document.getElementById('bookmarkCountBadge');
  const articlesContainer = document.getElementById('articlesGrid');
  const cards = document.querySelectorAll('.news-card');
  const emptyState = document.getElementById('emptyState');
  const modalOverlay = document.getElementById('quickReadModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const timeDisplay = document.getElementById('liveTimeDisplay');
  const toastMsg = document.getElementById('toastMsg');

  // Initialize
  function init() {
    initTheme();
    initClock();
    updateBookmarkBadges();
    setupEventListeners();
  }

  // Live UTC/Local Clock
  function initClock() {
    if (!timeDisplay) return;
    const updateTime = () => {
      const now = new Date();
      timeDisplay.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' ' + Intl.DateTimeFormat().resolvedOptions().timeZone;
    };
    updateTime();
    setInterval(updateTime, 1000);
  }

  // Theme Management
  function initTheme() {
    const savedTheme = localStorage.getItem('newspulse_theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    applyTheme(savedTheme);
  }

  function applyTheme(theme) {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      if (themeToggleBtn) themeToggleBtn.innerHTML = '☀️';
    } else {
      document.documentElement.removeAttribute('data-theme');
      if (themeToggleBtn) themeToggleBtn.innerHTML = '🌙';
    }
    localStorage.setItem('newspulse_theme', theme);
  }

  function toggleTheme() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    applyTheme(isLight ? 'dark' : 'light');
  }

  // Toast Notification
  let toastTimer;
  function showToast(message) {
    if (!toastMsg) return;
    toastMsg.textContent = message;
    toastMsg.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastMsg.classList.remove('show');
    }, 2800);
  }

  // Filter & Search Engine
  function applyFilters() {
    let visibleCount = 0;
    const query = state.searchQuery.toLowerCase().trim();

    cards.forEach(card => {
      const id = card.getAttribute('data-id');
      const cat = card.getAttribute('data-category');
      const title = (card.getAttribute('data-title') || '').toLowerCase();
      const summary = (card.getAttribute('data-summary') || '').toLowerCase();
      const source = (card.getAttribute('data-source') || '').toLowerCase();

      // Check Category
      const matchesCategory = state.activeCategory === 'all' || cat === state.activeCategory;

      // Check Bookmarks
      const matchesBookmark = !state.showBookmarksOnly || state.bookmarks.includes(id);

      // Check Search Query
      const matchesSearch = !query || title.includes(query) || summary.includes(query) || source.includes(query) || cat.includes(query);

      if (matchesCategory && matchesBookmark && matchesSearch) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  // Bookmark Handling
  function toggleBookmark(articleId) {
    const idx = state.bookmarks.indexOf(articleId);
    if (idx > -1) {
      state.bookmarks.splice(idx, 1);
      showToast('Removed from saved bookmarks');
    } else {
      state.bookmarks.push(articleId);
      showToast('Saved to bookmarks');
    }
    localStorage.setItem('newspulse_bookmarks', JSON.stringify(state.bookmarks));
    updateBookmarkBadges();
    applyFilters();
  }

  function updateBookmarkBadges() {
    if (bookmarkCountBadge) {
      bookmarkCountBadge.textContent = state.bookmarks.length;
    }
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
      const artId = btn.getAttribute('data-id');
      if (state.bookmarks.includes(artId)) {
        btn.classList.add('bookmarked');
        btn.innerHTML = '★';
        btn.title = 'Remove bookmark';
      } else {
        btn.classList.remove('bookmarked');
        btn.innerHTML = '☆';
        btn.title = 'Save story';
      }
    });
  }

  // Text to Speech (TTS)
  function stopTTS() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    document.querySelectorAll('.tts-btn').forEach(btn => btn.classList.remove('speaking'));
    state.speakingArticleId = null;
  }

  function speakArticle(articleId, textToRead, btnElement) {
    if (!('speechSynthesis' in window)) {
      showToast('Speech synthesis not supported in this browser');
      return;
    }

    if (state.speakingArticleId === articleId) {
      stopTTS();
      showToast('Audio paused');
      return;
    }

    stopTTS();

    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    // Pick best English voice if available
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Premium')));
    if (naturalVoice) utterance.voice = naturalVoice;

    utterance.onstart = () => {
      state.speakingArticleId = articleId;
      if (btnElement) btnElement.classList.add('speaking');
      showToast('Playing audio summary...');
    };

    utterance.onend = () => {
      stopTTS();
    };

    utterance.onerror = () => {
      stopTTS();
    };

    window.speechSynthesis.speak(utterance);
  }

  // Web Share API
  async function shareStory(title, url) {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title + ' - NewsPulse',
          text: title,
          url: url
        });
      } catch (e) {
        // User cancelled or not supported
      }
    } else {
      try {
        await navigator.clipboard.writeText(url);
        showToast('Link copied to clipboard!');
      } catch (err) {
        showToast('Could not copy link');
      }
    }
  }

  // Quick Read Modal
  function openQuickRead(articleData) {
    if (!modalOverlay) return;

    document.getElementById('modalImg').src = articleData.image;
    document.getElementById('modalTag').textContent = articleData.categoryName;
    document.getElementById('modalTag').style.backgroundColor = articleData.categoryColor;
    document.getElementById('modalSource').textContent = articleData.source;
    document.getElementById('modalTime').textContent = articleData.timeAgo;
    document.getElementById('modalTitle').textContent = articleData.title;
    document.getElementById('modalSummary').textContent = articleData.summary;

    // Bullets
    const bulletsList = document.getElementById('modalBullets');
    bulletsList.innerHTML = '';
    const bullets = JSON.parse(articleData.bullets || '[]');
    if (bullets.length > 0) {
      bullets.forEach(b => {
        const li = document.createElement('li');
        li.textContent = b;
        bulletsList.appendChild(li);
      });
      document.getElementById('modalTakeawaysWrapper').style.display = 'block';
    } else {
      document.getElementById('modalTakeawaysWrapper').style.display = 'none';
    }

    // Story Link
    const storyBtn = document.getElementById('modalStoryBtn');
    if (storyBtn) {
      storyBtn.href = `/stories/${articleData.slug}/`;
    }

    // Original Link
    const origBtn = document.getElementById('modalOriginalBtn');
    if (origBtn) {
      origBtn.href = articleData.originalUrl;
      origBtn.textContent = `Full Coverage on ${articleData.source} ↗`;
    }

    // Modal TTS
    const modalTtsBtn = document.getElementById('modalTtsBtn');
    if (modalTtsBtn) {
      modalTtsBtn.onclick = () => {
        speakArticle(articleData.id, `${articleData.title}. ${articleData.summary}`, modalTtsBtn);
      };
    }

    modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeQuickRead() {
    if (!modalOverlay) return;
    modalOverlay.classList.remove('active');
    document.body.style.overflow = '';
    stopTTS();
  }

  // Event Listeners Setup
  function setupEventListeners() {
    // Search input
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        applyFilters();
      });
    }

    // Category pills
    categoryPills.forEach(pill => {
      pill.addEventListener('click', () => {
        categoryPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        state.activeCategory = pill.getAttribute('data-cat');
        state.showBookmarksOnly = false;
        if (bookmarksToggleBtn) bookmarksToggleBtn.classList.remove('active');
        applyFilters();
      });
    });

    // Bookmarks toggle
    if (bookmarksToggleBtn) {
      bookmarksToggleBtn.addEventListener('click', () => {
        state.showBookmarksOnly = !state.showBookmarksOnly;
        bookmarksToggleBtn.classList.toggle('active', state.showBookmarksOnly);
        if (state.showBookmarksOnly) {
          categoryPills.forEach(p => p.classList.remove('active'));
        } else {
          document.querySelector('.cat-pill[data-cat="all"]')?.classList.add('active');
          state.activeCategory = 'all';
        }
        applyFilters();
      });
    }

    // Theme toggle
    if (themeToggleBtn) {
      themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Modal close
    if (modalCloseBtn) {
      modalCloseBtn.addEventListener('click', closeQuickRead);
    }
    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeQuickRead();
      });
    }
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeQuickRead();
    });

    // Card delegation (Quick read, bookmark, TTS, share)
    if (articlesContainer) {
      articlesContainer.addEventListener('click', (e) => {
        const quickReadBtn = e.target.closest('.btn-quick-read');
        if (quickReadBtn) {
          const card = quickReadBtn.closest('.news-card');
          if (card) {
            openQuickRead({
              id: card.getAttribute('data-id'),
              slug: card.getAttribute('data-slug'),
              title: card.getAttribute('data-title'),
              summary: card.getAttribute('data-summary'),
              bullets: card.getAttribute('data-bullets'),
              categoryName: card.getAttribute('data-category-name'),
              categoryColor: card.getAttribute('data-category-color'),
              source: card.getAttribute('data-source'),
              timeAgo: card.getAttribute('data-time-ago'),
              image: card.getAttribute('data-image'),
              originalUrl: card.getAttribute('data-original-url')
            });
          }
          return;
        }

        const bmarkBtn = e.target.closest('.bookmark-btn');
        if (bmarkBtn) {
          e.preventDefault();
          const artId = bmarkBtn.getAttribute('data-id');
          toggleBookmark(artId);
          return;
        }

        const ttsBtn = e.target.closest('.tts-btn');
        if (ttsBtn) {
          e.preventDefault();
          const card = ttsBtn.closest('.news-card');
          const artId = ttsBtn.getAttribute('data-id');
          const title = card.getAttribute('data-title');
          const summary = card.getAttribute('data-summary');
          speakArticle(artId, `${title}. ${summary}`, ttsBtn);
          return;
        }

        const shareBtn = e.target.closest('.share-btn');
        if (shareBtn) {
          e.preventDefault();
          const card = shareBtn.closest('.news-card');
          const title = card.getAttribute('data-title');
          const url = window.location.origin + `/stories/${card.getAttribute('data-slug')}/`;
          shareStory(title, url);
          return;
        }
      });
    }

    // Contact form simulation if on contact page
    const contactForm = document.getElementById('newsPulseContactForm');
    if (contactForm) {
      contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        showToast('Message sent! Our editorial desk will reply shortly.');
        contactForm.reset();
      });
    }
  }

  // Run on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
