# PeerSphere Premium Instagram-Style Overhaul

Transform PeerSphere from a basic social platform into an addictive, premium Instagram-style experience with engaging features and stunning UI.

## Bug Fixes

### Errors Found

1. **`current_user.username`** — `dashboard.html:16` references `current_user.username` but the [User](file:///d:/peersphere/backend/app/models/user.py#11-57) model has no `username` field
2. **`upcoming_events`** — `dashboard.html:214` references `upcoming_events` but [main.py](file:///d:/peersphere/backend/app/routes/main.py) dashboard route doesn't pass it
3. **Missing CSS classes** — Dashboard template uses `dashboard-sidebar`, `dashboard-main`, `profile-card`, `profile-card-header`, `profile-card-avatar`, etc. that don't exist in [style.css](file:///d:/peersphere/frontend/static/css/style.css)
4. **Font mismatch** — CSS body uses `Plus Jakarta Sans` but [base.html](file:///d:/peersphere/frontend/templates/base.html) only loads `Inter` from Google Fonts
5. **Missing asset** — `default-community.svg` referenced in dashboard but doesn't exist in `/static/img/`

---

## Proposed Changes

### Bug Fixes Component

#### [MODIFY] [user.py](file:///d:/peersphere/backend/app/models/user.py)
- Add `username` property that auto-generates from email (e.g., `user@email.com` → [user](file:///d:/peersphere/backend/app/models/user.py#6-9))

#### [MODIFY] [main.py](file:///d:/peersphere/backend/app/routes/main.py)
- Query upcoming events and pass `upcoming_events` to the dashboard template

#### [MODIFY] [dashboard.html](file:///d:/peersphere/frontend/templates/main/dashboard.html)
- Fix all template references to match the actual model/context

#### [MODIFY] [base.html](file:///d:/peersphere/frontend/templates/base.html)
- Load both `Inter` and `Plus Jakarta Sans` fonts, add notification bell, add Instagram-style mobile bottom nav

#### [NEW] [default-community.svg](file:///d:/peersphere/frontend/static/img/default-community.svg)
- Create a placeholder community avatar SVG

---

### Premium Features — Backend

#### [MODIFY] [post.py](file:///d:/peersphere/backend/app/models/post.py)
- Add `Bookmark` model for saving posts
- Add `Reaction` model with emoji types (❤️ fire, clap, mind-blown, etc.)
- Add `Poll`, `PollOption`, `PollVote` models for in-post polls

#### [NEW] [story.py](file:///d:/peersphere/backend/app/models/story.py)
- `Story` model: user_id, image_url, text_overlay, created_at, expires_at (24h), view tracking

#### [MODIFY] [user.py](file:///d:/peersphere/backend/app/models/user.py)
- Add `streak_count`, `last_active`, `is_verified` fields
- Add `username` property

#### [MODIFY] [feed.py](file:///d:/peersphere/backend/app/routes/feed.py)
- Add bookmark/unbookmark endpoint
- Add reaction endpoint (multiple emoji types)
- Add `/api/feed` infinite scroll JSON endpoint
- Add poll vote endpoint

#### [NEW] [stories.py](file:///d:/peersphere/backend/app/routes/stories.py)
- Create/view/delete stories
- Mark story as viewed

#### [MODIFY] [__init__.py](file:///d:/peersphere/backend/app/__init__.py)
- Register stories blueprint

---

### UI Overhaul — Instagram Premium Vibe

#### [MODIFY] [style.css](file:///d:/peersphere/frontend/static/css/style.css)
Complete rewrite with:
- **Premium color palette**: Rich purples, electric blues, warm amber accents
- **Gradient everywhere**: Profile rings (story indicator), buttons, badges
- **Glassmorphism 2.0**: Frosted glass cards with colored borders
- **Micro-animations**: Heart burst on like, shimmer loading skeletons, smooth page transitions
- **Mobile-first**: Bottom tab bar for mobile, swipeable stories carousel
- **Dark mode perfected**: OLED-black option with neon accents
- **New components**: Stories bar, reaction picker, streak flame badge, achievement popup, poll UI
- **Missing dashboard classes**: Add all missing CSS classes for sidebar layout

#### [MODIFY] [app.js](file:///d:/peersphere/frontend/static/js/app.js)
- Double-tap to like with animated heart overlay
- Infinite scroll loader
- Story carousel with auto-advance timer
- Emoji reaction picker popup
- Streak counter animation
- Confetti burst on achievements
- Image preview before upload
- Poll voting with animated bars
- Bookmark toggle animation

#### [MODIFY] [feed/index.html](file:///d:/peersphere/frontend/templates/feed/index.html)
- Add stories bar at top
- Redesign post cards: gradient avatar rings, reaction picker, bookmark button, share
- Add poll creation UI in post composer
- Infinite scroll container
- Shimmer loading skeleton placeholders

#### [MODIFY] [dashboard.html](file:///d:/peersphere/frontend/templates/main/dashboard.html)
- Add stories bar
- Streak counter with fire emoji
- Achievement badges showcase
- "Who viewed your profile" teaser card
- Quick reactions on posts
- Engagement stats sparkline

#### [MODIFY] [base.html](file:///d:/peersphere/frontend/templates/base.html)
- Instagram-style mobile bottom navigation
- Notification bell with live count badge
- Animated gradient brand logo
- Story-style avatar ring in navbar
- Premium "verified" checkmark support

---

### Suggested Cool Features

| Feature | Description |
|---------|-------------|
| **Stories** | 24-hour ephemeral photo/text posts with view tracking |
| **Polls** | In-post voting with animated result bars |
| **Streaks** | Daily login streak counter with fire emoji badge |
| **Quick Reactions** | Emoji row (❤️ 🔥 👏 🤯 😂 🎉) on every post |
| **Bookmarks** | Save posts to private collection |
| **Achievement Badges** | Earned milestones (First Post, 100 Likes, etc.) |
| **Profile Views Teaser** | "X people viewed your profile this week" |
| **Verified Badge** | Premium checkmark for verified users |

---

## Verification Plan

### Automated Verification
Run the Flask server and verify no errors:
```bash
cd d:\peersphere\backend
python run.py
```
Then visit these endpoints in browser to confirm no 500 errors:
- `http://localhost:5000/` (landing)
- `http://localhost:5000/dashboard` (after login)
- `http://localhost:5000/feed/` (feed page)

### Browser Testing
Use the browser tool to:
1. Navigate to the app and register/login
2. Verify dashboard loads without errors
3. Verify stories bar renders at top of feed
4. Test creating a post with poll
5. Test reactions and bookmarks
6. Verify mobile bottom nav appears at smaller viewport
7. Toggle dark mode and verify premium dark theme
8. Check streak counter displays

### Manual Verification
After implementation, please:
1. Open the app at `http://localhost:5000` and check the UI looks premium/Instagram-like
2. Try the dark mode toggle — it should have rich OLED blacks with neon accents
3. Scroll the feed — it should feel smooth and engaging with animations
4. React to a post with different emojis
5. Create a poll in a post and vote on it
