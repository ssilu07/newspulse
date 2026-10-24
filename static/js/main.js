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
    initCookieConsent();
    handleUrlParamsAndHash();
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
    const currentCards = document.querySelectorAll('.news-card');

    currentCards.forEach(card => {
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
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    const heroSection = document.getElementById('heroSection');
    if (heroSection) {
      const heroCard = heroSection.querySelector('.news-card');
      if (heroCard && heroCard.style.display === 'none') {
        heroSection.style.display = 'none';
      } else if (heroSection) {
        heroSection.style.display = '';
      }
    }

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

  // Cookie & GDPR Consent Initialization (AdSense EU User Consent Policy)
  function initCookieConsent() {
    const consentBar = document.getElementById('cookieConsentBar');
    const acceptBtn = document.getElementById('cookieAcceptBtn');
    const manageBtn = document.getElementById('cookieManageBtn');
    if (!consentBar) return;

    const consent = localStorage.getItem('newspulse_cookie_consent');
    if (!consent) {
      consentBar.style.display = 'block';
    }

    if (acceptBtn) {
      acceptBtn.addEventListener('click', () => {
        localStorage.setItem('newspulse_cookie_consent', 'accepted');
        consentBar.style.display = 'none';
        showToast('Cookie preferences saved.');
      });
    }

    if (manageBtn) {
      manageBtn.addEventListener('click', () => {
        window.location.href = '/privacy/#cookies';
      });
    }
  }

  // Handle URL Query (?q=...) and Hash (#tech, #world, etc.)
  function handleUrlParamsAndHash() {
    // 1. Search Query param (?q=keyword)
    const urlParams = new URLSearchParams(window.location.search);
    const qParam = urlParams.get('q');
    if (qParam && searchInput) {
      searchInput.value = qParam;
      state.searchQuery = qParam;
    }

    // 2. Hash category filter (#tech, #ai-future, #business, etc.)
    const hash = window.location.hash.replace('#', '').trim();
    if (hash && hash !== 'team' && hash !== 'cookies') {
      const targetPill = document.querySelector(`.cat-pill[data-cat="${hash}"]`);
      if (targetPill) {
        categoryPills.forEach(p => p.classList.remove('active'));
        targetPill.classList.add('active');
        state.activeCategory = hash;
      }
    }

    if (cards.length > 0) {
      applyFilters();
    }
  }

  // Clientside Infinite Pagination & Load More
  let allArticlesCache = null;
  let currentlyRendered = 36;

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function createArticleCardHtml(art) {
    const artId = escapeHtml(art.id || '');
    const slug = escapeHtml(art.slug || '');
    const catSlug = escapeHtml(art.category || 'tech');
    const catName = escapeHtml(art.category_name || 'News');
    const catColor = escapeHtml(art.category_color || '#3b82f6');
    const title = escapeHtml(art.title || '');
    const summary = escapeHtml(art.summary || '');
    const source = escapeHtml(art.source || 'News Seconds');
    const timeAgo = escapeHtml(art.time_ago || 'Recently');
    const image = escapeHtml(art.image_url || 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&fit=crop');
    const origUrl = escapeHtml(art.original_url || '#');
    const bulletsJson = escapeHtml(JSON.stringify(art.bullet_points || []));

    return `
      <article class="news-card"
        data-id="${artId}"
        data-slug="${slug}"
        data-category="${catSlug}"
        data-category-name="${catName}"
        data-category-color="${catColor}"
        data-title="${title}"
        data-summary="${summary}"
        data-bullets="${bulletsJson}"
        data-source="${source}"
        data-time-ago="${timeAgo}"
        data-image="${image}"
        data-original-url="${origUrl}">
        <div class="card-media">
          <a href="/news/${slug}/" class="card-media-link" aria-label="${title}">
            <img src="${image}" alt="${title}" class="card-img" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&fit=crop';">
          </a>
          <span class="card-tag" style="background-color: ${catColor};">${catName}</span>
          <span class="card-meta-badge">🕒 ${timeAgo}</span>
        </div>
        <div class="card-body">
          <div class="card-source-row">
            <span class="card-source"><span class="source-dot"></span>${source}</span>
            <span class="read-badge">1 min read</span>
          </div>
          <h3 class="card-title"><a href="/news/${slug}/" class="card-title-link">${title}</a></h3>
          <p class="card-summary">${summary}</p>
          <div class="card-actions">
            <div class="action-btn-group">
              <a href="/news/${slug}/" class="full-article-link" title="Read Full In-Depth Story">📰 Full Story</a>
              <a href="/stories/${slug}/" class="web-story-link" title="Open 5-Slide AMP Story">⚡ Web Story</a>
              <button class="btn-quick-read" title="Quick Read Drawer">📖 Summary</button>
            </div>
            <div class="action-btn-group">
              <button class="icon-action-btn tts-btn" data-id="${artId}" title="Listen to summary" aria-label="Listen">🔊</button>
              <button class="icon-action-btn bookmark-btn" data-id="${artId}" title="Save story" aria-label="Bookmark">☆</button>
              <button class="icon-action-btn share-btn" title="Share story" aria-label="Share">🔗</button>
            </div>
          </div>
        </div>
      </article>`;
  }

  async function loadMoreArticles() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const loadMoreWrapper = document.getElementById('loadMoreWrapper');
    if (!loadMoreBtn) return;

    loadMoreBtn.disabled = true;
    const btnSpan = loadMoreBtn.querySelector('span');
    if (btnSpan) btnSpan.textContent = 'Loading stories...';

    try {
      if (!allArticlesCache) {
        const resp = await fetch('/api/articles.json');
        allArticlesCache = await resp.json();
      }
      const nextBatch = allArticlesCache.slice(currentlyRendered, currentlyRendered + 24);
      if (!nextBatch || nextBatch.length === 0) {
        if (loadMoreWrapper) loadMoreWrapper.style.display = 'none';
        return;
      }
      const frag = document.createDocumentFragment();
      nextBatch.forEach(art => {
        const div = document.createElement('div');
        div.innerHTML = createArticleCardHtml(art);
        if (div.firstElementChild) frag.appendChild(div.firstElementChild);
      });
      if (articlesContainer) {
        articlesContainer.appendChild(frag);
      }
      currentlyRendered += nextBatch.length;
      updateBookmarkBadges();
      applyFilters();
      if (currentlyRendered >= allArticlesCache.length) {
        if (loadMoreWrapper) loadMoreWrapper.style.display = 'none';
      }
    } catch (e) {
      console.warn('Load more error:', e);
    } finally {
      loadMoreBtn.disabled = false;
      if (btnSpan) btnSpan.textContent = 'Load More Breaking Mobility Stories';
    }
  }

  // Event Listeners Setup
  function setupEventListeners() {
    // Search input (supports instant search on home, Enter key on article/compliance pages)
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        if (cards.length > 0) {
          applyFilters();
        }
      });

      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const val = searchInput.value.trim();
          if (cards.length === 0 && val) {
            window.location.href = `/?q=${encodeURIComponent(val)}`;
          } else if (cards.length > 0) {
            applyFilters();
          }
        }
      });
    }

    // Hash change routing
    window.addEventListener('hashchange', handleUrlParamsAndHash);

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

    // Load More Stories Button
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', loadMoreArticles);
    }

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

    // Dedicated Article Page Audio TTS Listener
    const articleTtsBtn = document.getElementById('articleTtsBtn');
    if (articleTtsBtn) {
      articleTtsBtn.addEventListener('click', () => {
        if (!('speechSynthesis' in window)) {
          showToast('Text-to-speech not supported in this browser.');
          return;
        }

        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
          articleTtsBtn.innerHTML = '<span>🔊</span> <span>Listen to Story</span>';
          showToast('Audio playback stopped.');
          return;
        }

        const title = document.querySelector('.article-title')?.textContent || '';
        const lead = document.querySelector('.article-lead')?.textContent || '';
        const bullets = Array.from(document.querySelectorAll('.article-takeaways-list li')).map(li => li.textContent).join('. ');
        const textToRead = `${title}. Key highlights: ${bullets}. Briefing: ${lead}`;

        const utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
          articleTtsBtn.innerHTML = '<span>⏹️</span> <span>Stop Audio</span>';
          showToast('Playing audio narration...');
        };

        utterance.onend = () => {
          articleTtsBtn.innerHTML = '<span>🔊</span> <span>Listen to Story</span>';
        };

        utterance.onerror = () => {
          articleTtsBtn.innerHTML = '<span>🔊</span> <span>Listen to Story</span>';
        };

        window.speechSynthesis.speak(utterance);
      });
    }

    // Article Page Copy Link Handler
    const copyLinkBtn = document.getElementById('copyArticleLinkBtn');
    if (copyLinkBtn) {
      copyLinkBtn.addEventListener('click', (e) => {
        e.preventDefault();
        navigator.clipboard.writeText(window.location.href).then(() => {
          showToast('Link copied to clipboard!');
        }).catch(() => {
          showToast('Copied: ' + window.location.href);
        });
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
