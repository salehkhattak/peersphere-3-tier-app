/**
 * PeerSphere Premium JS — Instagram-Style Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initToasts();
    initTooltips();
    initNavHighlight();
    initLandingNav();
    initConfettiOnLoad();
});

/* ── Theme ── */
function initTheme() {
    const saved = localStorage.getItem('ps-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('ps-theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';
}

/* ── Toasts ── */
function initToasts() {
    document.querySelectorAll('.toast-notification').forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 350);
        }, 4500);
    });
}

/* ── Tooltips ── */
function initTooltips() {
    if (typeof bootstrap !== 'undefined') {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
    }
}

/* ── Nav Highlight ── */
function initNavHighlight() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-icon-link').forEach(link => {
        if (link.href && link.href !== window.location.origin + '/' && path.startsWith(new URL(link.href).pathname)) {
            link.classList.add('active');
        }
    });
}

/* ── Landing Navbar on Scroll ── */
function initLandingNav() {
    const nav = document.querySelector('.landing-nav');
    if (!nav) return;
    window.addEventListener('scroll', () => {
        nav.classList.toggle('scrolled', window.scrollY > 50);
    }, { passive: true });
}

/* ── Confetti on first visit / achievement ── */
function initConfettiOnLoad() {
    const justJoined = sessionStorage.getItem('ps-just-joined');
    if (justJoined) {
        sessionStorage.removeItem('ps-just-joined');
        fireConfetti();
    }
}

function fireConfetti() {
    const colors = ['#6C5CE7','#E84393','#FDCB6E','#00B894','#FD79A8','#A29BFE'];
    for (let i = 0; i < 80; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.style.cssText = `
            left:${Math.random()*100}vw;
            top:-10px;
            background:${colors[Math.floor(Math.random()*colors.length)]};
            border-radius:${Math.random()>0.5?'50%':'2px'};
            width:${6+Math.random()*8}px;
            height:${6+Math.random()*8}px;
            transform:rotate(${Math.random()*360}deg);
            animation:confettiFall ${1.5+Math.random()*2}s ease-in ${Math.random()*1.5}s forwards;
        `;
        document.body.appendChild(piece);
        setTimeout(() => piece.remove(), 4000);
    }
}

/* ── Story ── */
function openStory(avatar, name, text, gradient, imageUrl) {
    const overlay = document.getElementById('storyModalOverlay');
    const wrap = document.getElementById('storyContentWrap');
    const header = document.getElementById('storyHeader');
    const body = document.getElementById('storyBody');
    if (!overlay) return;
    wrap.className = 'story-content-wrap ' + (gradient || 'gradient-1');
    header.innerHTML = `<img src="${avatar}" /><span>${name}</span>`;
    if (imageUrl && imageUrl !== 'None' && imageUrl !== '') {
        body.innerHTML = `<img src="/static/uploads/${imageUrl}" class="story-img-full" alt="story"/>`;
    } else {
        body.innerHTML = text ? `<p>${text}</p>` : `<p style="opacity:0.5">👋 No content</p>`;
    }
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeStoryModal(e) {
    if (e.target === document.getElementById('storyModalOverlay')) closeStoryModalDirect();
}

function closeStoryModalDirect() {
    const overlay = document.getElementById('storyModalOverlay');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
}

/* ── Double-tap Like ── */
function doubleTapLike(postId, container) {
    const heart = document.getElementById('heart-' + postId);
    if (!heart) return;
    heart.classList.remove('animate');
    void heart.offsetWidth;
    heart.classList.add('animate');
    const likeBtn = document.getElementById('like-btn-' + postId);
    if (likeBtn && !likeBtn.classList.contains('liked')) {
        const form = document.querySelector(`.like-form[data-post-id="${postId}"]`);
        if (form) form.submit();
    }
    setTimeout(() => heart.classList.remove('animate'), 900);
}

/* ── Toggle Comments ── */
function toggleComments(postId) {
    const el = document.getElementById('comments-' + postId);
    if (!el) return;
    const isHidden = el.style.display === 'none' || el.style.display === '';
    el.style.display = isHidden ? 'block' : 'none';
}

/* ── Reaction Picker ── */
function showReactionPicker(postId) {
    const picker = document.getElementById('reaction-picker-' + postId);
    if (picker) picker.classList.add('show');
}

function hideReactionPicker(postId) {
    setTimeout(() => {
        const picker = document.getElementById('reaction-picker-' + postId);
        if (picker && !picker.matches(':hover')) picker.classList.remove('show');
    }, 200);
}

/* ── Poll toggle ── */
function togglePoll() {
    const el = document.getElementById('pollCreator');
    if (el) el.classList.toggle('active');
}

function addPollOption() {
    const container = document.getElementById('pollOptionsContainer');
    if (!container) return;
    const count = container.querySelectorAll('input').length;
    if (count >= 4) return;
    const inp = document.createElement('input');
    inp.type = 'text'; inp.name = 'poll_options[]';
    inp.placeholder = 'Option ' + (count + 1);
    inp.style.cssText = 'width:100%;padding:0.5rem 0.75rem;border:1px solid var(--border-color);border-radius:var(--radius-sm);background:var(--surface);color:var(--text-main);font-family:inherit;margin-bottom:0.5rem;display:block;';
    container.appendChild(inp);
}

/* ── Image Preview ── */
function previewImage(input) {
    if (!input.files || !input.files[0]) return;
    const reader = new FileReader();
    reader.onload = e => {
        const preview = document.getElementById('imagePreview');
        const container = document.getElementById('imagePreviewContainer');
        if (preview && container) { preview.src = e.target.result; container.style.display = 'block'; }
    };
    reader.readAsDataURL(input.files[0]);
}

function clearImagePreview() {
    const preview = document.getElementById('imagePreview');
    const container = document.getElementById('imagePreviewContainer');
    const input = document.getElementById('imageInput');
    if (preview) preview.src = '';
    if (container) container.style.display = 'none';
    if (input) input.value = '';
}

/* ── Share Post ── */
function sharePost(postId) {
    if (navigator.share) {
        navigator.share({ title: 'PeerSphere Post', url: window.location.href }).catch(() => {});
    } else {
        navigator.clipboard.writeText(window.location.href).then(() => showToast('Link copied! 🔗', 'success'));
    }
}

/* ── Random Emoji insert ── */
function insertEmoji() {
    const ta = document.getElementById('postTextarea');
    if (!ta) return;
    const emojis = ['😊','🚀','🔥','💡','🎉','✨','❤️','🎯','💪','🌟'];
    ta.value += emojis[Math.floor(Math.random() * emojis.length)];
    ta.focus();
}

/* ── Inline Toast ── */
function showToast(message, category = 'info') {
    const icons = { success:'check-circle-fill', danger:'exclamation-circle-fill', warning:'exclamation-triangle-fill', info:'info-circle-fill' };
    const container = document.getElementById('toastContainer') || (() => {
        const div = document.createElement('div'); div.className = 'toast-container'; div.id = 'toastContainer';
        document.body.appendChild(div); return div;
    })();
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${category}`;
    toast.innerHTML = `<div class="toast-icon"><i class="bi bi-${icons[category]||icons.info}"></i></div><span>${message}</span><button class="toast-close" onclick="this.parentElement.remove()"><i class="bi bi-x"></i></button>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity='0'; toast.style.transform='translateX(100%)'; setTimeout(() => toast.remove(), 350); }, 4000);
}

/* ── CSRF helper ── */
function getCsrfToken() {
    const t = document.querySelector('input[name="csrf_token"]');
    return t ? t.value : '';
}

/* ── Confetti keyframe (injected once) ── */
(function injectConfettiCSS() {
    if (document.getElementById('ps-confetti-style')) return;
    const s = document.createElement('style');
    s.id = 'ps-confetti-style';
    s.textContent = '@keyframes confettiFall{0%{transform:translateY(0) rotate(0);opacity:1}100%{transform:translateY(100vh) rotate(720deg);opacity:0}}';
    document.head.appendChild(s);
})();
