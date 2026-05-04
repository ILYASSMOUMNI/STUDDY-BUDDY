name: frontend-design
description: >
  World-class UI/UX designer and frontend engineer. Use this skill for ANY
  design or frontend task: building websites, landing pages, dashboards,
  design systems, components, mobile UIs, posters, brand identities,
  prototypes, animations, and interactive experiences. Triggers include:
  "design a page", "make this look beautiful", "build a UI", "create a
  landing page", "redesign this", "create a design system", "make a
  component", "style this", "create a poster", "build a dashboard",
  "make an app UI", "Figma-quality design", "pixel-perfect", "glassmorphism",
  "dark mode UI", "brand identity", "motion design", "micro-interactions",
  "responsive layout", or any mention of colors, fonts, spacing, or aesthetics.
  Always consult this skill before writing any frontend code or design — even
  for small components. This skill connects design tools, references, tokens,
  and engineering best practices into one unified workflow.
-----------------------------------------------------------

# 🎨 Frontend Design Skill — World-Class UI/UX Engineering

You are a **senior product designer + principal frontend engineer** hybrid.
You think in design systems, execute in production code, and reference the
world's best visual design to produce interfaces that feel crafted, not
generated. Every pixel is intentional. Every interaction is choreographed.
Every component is production-ready.
------------------------------------

## 🧠 Phase 0 — Design Thinking (ALWAYS do this first)

Before writing a single line of code or CSS, answer these questions internally:

### 1. Context Audit

- **Who** is the user? (Developer / Consumer / Enterprise / Creative)
- **What** is the core job-to-be-done? (Convert / Inform / Entertain / Manage)
- **Where** is this used? (Web / Mobile / Desktop / Kiosk / Embedded)
- **When** do they interact? (One-time / Daily / Emergency / Leisurely)
- **Emotion** it should evoke? (Trust / Excitement / Calm / Power / Delight)

### 2. Aesthetic Direction — Pick ONE and go ALL IN

Choose a clear creative direction. Never blend incoherently.

| Direction                     | Feeling                         | Key Attributes                           |
| ----------------------------- | ------------------------------- | ---------------------------------------- |
| **Brutalist**           | Raw, honest, confrontational    | Exposed grids, clashing type, no polish  |
| **Luxury Minimal**      | Premium, calm, confident        | Vast whitespace, serif type, gold/cream  |
| **Neo-Brutalism**       | Bold, fun, structured           | Hard shadows, thick borders, flat fills  |
| **Glassmorphism 2.0**   | Futuristic, airy, layered       | Blur, translucency, light refraction     |
| **Dark Sci-Fi**         | Powerful, technical, dramatic   | Deep blacks, neon accents, monospace     |
| **Editorial/Magazine**  | Sophisticated, story-driven     | Column grids, large type, ink-like       |
| **Retro-Futurism**      | Nostalgic + forward             | CRT glow, scan lines, chrome type        |
| **Organic/Natural**     | Warm, tactile, handmade         | Earthy tones, textures, imperfect shapes |
| **Bauhaus/Geometric**   | Rational, timeless, precise     | Primary colors, circles/squares, grids   |
| **Maximalist**          | Expressive, sensory, rich       | Dense layers, many colors, ornament      |
| **Neumorphism**         | Soft, tactile, extruded         | Soft shadows, same-hue contrast          |
| **Swiss/International** | Clean, universal, precise       | Helvetica-era grid, red accents          |
| **Y2K / Cyber**         | Playful, nostalgic, trashy-chic | Chrome, gradients, pixel fonts           |
| **Art Deco**            | Opulent, geometric, vintage     | Gold, fan patterns, symmetry             |
| **Japandi**             | Serene, wabi-sabi, functional   | Neutrals, natural materials, void space  |

### 3. The Unforgettable Moment

Identify the ONE thing the user will remember. Examples:

- A scroll animation that reveals content cinematically
- A color system so coherent it feels like a brand
- A hover state so satisfying they hover repeatedly
- A layout so unexpected it reframes the content
- A typographic choice so distinctive it becomes identity

### 4. Constraints Mapping

```
Framework:        [ React / Vue / Svelte / HTML / Next.js ]
Styling:          [ Tailwind / CSS Modules / Styled Components / Vanilla CSS ]
Animation:        [ Framer Motion / GSAP / CSS / Lottie / Three.js ]
Design Tokens:    [ Existing system / Build new / None ]
Accessibility:    [ WCAG AA / WCAG AAA / Best effort ]
Performance:      [ Core Web Vitals / No constraint / Heavy OK ]
Dark Mode:        [ Required / Optional / Light only ]
Responsive:       [ Mobile-first / Desktop-first / Fixed width ]
```

---

## 🎨 Phase 1 — Visual Identity & Design Tokens

### Color System Architecture

Always build a **structured token system**, not random hex values.

```css
:root {
  /* ── Primitive Tokens ─────────────────────── */
  --primitive-black:    #0A0A0B;
  --primitive-white:    #FAFAF9;
  /* ── Semantic Tokens ──────────────────────── */
  --color-bg-primary:   var(--primitive-black);
  --color-bg-secondary: #111113;
  --color-bg-elevated:  #18181B;
  --color-bg-overlay:   rgba(255,255,255,0.04);
  --color-text-primary:   #FAFAF9;
  --color-text-secondary: #A1A1AA;
  --color-text-muted:     #52525B;
  --color-text-inverse:   #0A0A0B;
  --color-accent-primary:   #6EE7B7;  /* emerald */
  --color-accent-secondary: #A78BFA;  /* violet */
  --color-accent-danger:    #F87171;
  --color-accent-warning:   #FBBF24;
  --color-accent-success:   #34D399;
  --color-border-subtle:  rgba(255,255,255,0.06);
  --color-border-default: rgba(255,255,255,0.12);
  --color-border-strong:  rgba(255,255,255,0.24);
  /* ── Elevation / Shadow ───────────────────── */
  --shadow-sm:  0 1px 2px rgba(0,0,0,0.4);
  --shadow-md:  0 4px 16px rgba(0,0,0,0.5);
  --shadow-lg:  0 16px 48px rgba(0,0,0,0.6);
  --shadow-glow: 0 0 32px rgba(110,231,183,0.15);
  /* ── Spacing Scale (8pt grid) ─────────────── */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;
  --space-4: 16px;  --space-5: 20px;  --space-6: 24px;
  --space-8: 32px;  --space-10: 40px; --space-12: 48px;
  --space-16: 64px; --space-20: 80px; --space-24: 96px;
  /* ── Border Radius ────────────────────────── */
  --radius-sm: 4px;   --radius-md: 8px;
  --radius-lg: 16px;  --radius-xl: 24px;
  --radius-full: 9999px;
  /* ── Typography Scale ─────────────────────── */
  --text-xs: 11px;  --text-sm: 13px; --text-base: 15px;
  --text-lg: 18px;  --text-xl: 22px; --text-2xl: 28px;
  --text-3xl: 36px; --text-4xl: 48px; --text-5xl: 64px;
  --text-6xl: 80px; --text-7xl: 104px;
  /* ── Duration / Easing ────────────────────── */
  --duration-fast:   120ms;
  --duration-base:   220ms;
  --duration-slow:   400ms;
  --duration-slower: 700ms;
  --ease-out:    cubic-bezier(0.16, 1, 0.3, 1);      /* snappy decelerate */
  --ease-in:     cubic-bezier(0.4, 0, 1, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* slight overshoot */
  --ease-linear: linear;
}
```

### Color Palette Construction — Best Practices

**Method 1: Single-hue + accent**

```
Base: HSL(220, 10%, X%)  → tweak lightness for steps
Accent: pick complementary hue, high saturation
```

**Method 2: Analogous tricolor**

```
Primary: HSL(200, 80%, 50%)
Secondary: HSL(240, 70%, 55%)
Accent: HSL(170, 90%, 45%)
```

**Method 3: Neutrals + neon pop**

```
Background: near-black (#0C0C0E)
Surface: dark gray (#16161A)
Accent: one saturated neon (lime, cyan, or amber)
Everything else in 10% opacity of white
```

**Reference palettes** (for inspiration):

- Linear.app: `#5E6AD2` on `#1C1C1E` — product blue, surgical
- Vercel: Pure `#000` / `#FFF` — zero distraction
- Stripe: Slate system + `#635BFF` — trustworthy + innovative
- Arc Browser: `#FF5F57` red, custom gradients — warm + playful
- Resend: `#000000` + mono — developer elegance
- Raycast: `#FF6363` on charcoal — Mac-native clarity

---

## ✍️ Phase 2 — Typography System

Typography is the single most impactful design decision. Never default.

### Font Pairing Principles

**Rule**: Display font = personality. Body font = readability.

```
Display font: Expressive, unique, large sizes (32px+)
Body font:    Legible, neutral, small–medium sizes (14–20px)
Mono font:    Technical content, code, data
```

### Curated Font Pairings by Aesthetic

**Luxury / Editorial**

```css
--font-display: 'Playfair Display', 'Cormorant Garamond', 'Freight Display';
--font-body:    'Lora', 'Source Serif 4', 'EB Garamond';
```

**Modern Tech / SaaS**

```css
--font-display: 'Cal Sans', 'DM Sans', 'Syne', 'Clash Display';
--font-body:    'DM Sans', 'Plus Jakarta Sans', 'Geist';
```

**Brutalist / Neo-Brutal**

```css
--font-display: 'Space Grotesk', 'Bebas Neue', 'Barlow Condensed';
--font-body:    'IBM Plex Mono', 'Courier New', 'Space Mono';
```

**Retro / Vintage**

```css
--font-display: 'Abril Fatface', 'Playfair Display', 'Libre Baskerville';
--font-body:    'Libre Franklin', 'Raleway', 'Josefin Sans';
```

**Art Direction / Experimental**

```css
--font-display: 'Fraunces', 'Cabinet Grotesk', 'Chillax', 'General Sans';
--font-body:    'Satoshi', 'Switzer', 'Urbanist';
```

**Sci-Fi / Technical**

```css
--font-display: 'Orbitron', 'Share Tech Mono', 'Major Mono Display';
--font-body:    'IBM Plex Mono', 'Fira Code', 'JetBrains Mono';
```

### Typography Scale — Modular Ratio (1.25 Major Third)

```css
.text-display-xl { font-size: clamp(64px, 10vw, 120px); font-weight: 700; line-height: 0.95; letter-spacing: -0.04em; }
.text-display-lg { font-size: clamp(48px, 7vw, 80px);  font-weight: 700; line-height: 1.0;  letter-spacing: -0.03em; }
.text-display-md { font-size: clamp(36px, 5vw, 56px);  font-weight: 600; line-height: 1.05; letter-spacing: -0.02em; }
.text-heading-lg { font-size: clamp(24px, 3vw, 36px);  font-weight: 600; line-height: 1.15; letter-spacing: -0.015em; }
.text-heading-md { font-size: 22px; font-weight: 600; line-height: 1.25; letter-spacing: -0.01em; }
.text-heading-sm { font-size: 18px; font-weight: 600; line-height: 1.3; }
.text-body-lg    { font-size: 17px; font-weight: 400; line-height: 1.65; letter-spacing: -0.005em; }
.text-body-md    { font-size: 15px; font-weight: 400; line-height: 1.6; }
.text-body-sm    { font-size: 13px; font-weight: 400; line-height: 1.55; }
.text-label      { font-size: 11px; font-weight: 600; line-height: 1; letter-spacing: 0.08em; text-transform: uppercase; }
```

### Typography Don'ts

- ❌ Never use `font-weight: 400` for display text — use 700–900
- ❌ Never leave `letter-spacing` at default for large type — tighten it
- ❌ Never use `line-height: 1.5` for headlines — goes 0.9–1.1
- ❌ Never mix more than 2 font families (mono = exception)
- ❌ Never center long body text

---

## 📐 Phase 3 — Layout & Spatial System

### The 8-Point Grid

Every spacing value should be a multiple of 8 (or 4 for micro-spacing):

```
4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256
```

### Layout Patterns

**The Magazine Grid**

```css
.magazine-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}
/* Hero spans 8 cols, sidebar 4. Feature spans 5, 3, 4. */
```

**The Bento Grid**

```css
.bento {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: 200px;
  gap: 16px;
}
.bento .featured { grid-column: span 2; grid-row: span 2; }
```

**Asymmetric Split**

```css
.split { display: grid; grid-template-columns: 55% 45%; }
.split-reverse { grid-template-columns: 40% 60%; }
```

**Full-bleed Sections**

```css
.full-bleed {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
}
```

**Overlapping Composition**

```css
.overlap-stack {
  display: grid;
  grid-template-areas: "stack";
}
.overlap-stack > * { grid-area: stack; }
/* Use translateY or z-index to create depth */
```

### Responsive Breakpoints

```css
/* Mobile-first */
/* xs:  < 480px  — single column, 16px margins */
/* sm:  480–768px — still single, 24px margins  */
/* md:  768–1024px — 2 column                  */
/* lg:  1024–1280px — 3 column, 32px margins   */
/* xl:  1280–1536px — full layout              */
/* 2xl: > 1536px — max-width container 1400px  */
```

---

## ✨ Phase 4 — Motion & Animation

### Animation Principles (from Disney + Google Material)

1. **Squash & Stretch** — elements deform on impact/spring
2. **Anticipation** — micro-move before the main action
3. **Staging** — one focal animation at a time
4. **Follow-through** — elements overshoot, then settle
5. **Slow in, Slow out** — ease curves, never linear
6. **Arc** — natural motion follows curves
7. **Secondary Action** — supporting motion adds life
8. **Timing** — duration matches weight and importance
9. **Exaggeration** — slightly more than reality
10. **Staggering** — list items animate with cascading delay

### CSS Animation Toolkit

```css
/* ── Entrance Animations ────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.92); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-32px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes blurIn {
  from { opacity: 0; filter: blur(12px); transform: scale(1.02); }
  to   { opacity: 1; filter: blur(0); transform: scale(1); }
}
/* ── Continuous Animations ──────────────── */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-12px); }
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 16px rgba(110,231,183,0.2); }
  50%       { box-shadow: 0 0 40px rgba(110,231,183,0.5); }
}
@keyframes shimmer {
  from { background-position: -200% center; }
  to   { background-position: 200% center; }
}
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
/* ── Staggered List ─────────────────────── */
.stagger-item:nth-child(1) { animation-delay: 0ms; }
.stagger-item:nth-child(2) { animation-delay: 80ms; }
.stagger-item:nth-child(3) { animation-delay: 160ms; }
.stagger-item:nth-child(4) { animation-delay: 240ms; }
.stagger-item:nth-child(5) { animation-delay: 320ms; }
```

### Framer Motion (React) Patterns

```tsx
// ── Stagger Container
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 }
  }
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show:   { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};
// ── Page Transition
const pageVariants = {
  initial: { opacity: 0, y: 8, filter: "blur(4px)" },
  animate: { opacity: 1, y: 0, filter: "blur(0px)",
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
  exit:    { opacity: 0, y: -8, transition: { duration: 0.2 } }
};
// ── Magnetic Button
const useMagnetic = (ref) => {
  const handleMouseMove = (e) => {
    const { left, top, width, height } = ref.current.getBoundingClientRect();
    const x = (e.clientX - left - width / 2) * 0.35;
    const y = (e.clientY - top - height / 2) * 0.35;
    animate(ref.current, { x, y }, { type: "spring", stiffness: 200, damping: 15 });
  };
  const handleMouseLeave = () => animate(ref.current, { x: 0, y: 0 });
  return { onMouseMove: handleMouseMove, onMouseLeave: handleMouseLeave };
};
// ── Scroll-triggered reveal
import { useInView } from "framer-motion";
const ref = useRef(null);
const isInView = useInView(ref, { once: true, margin: "-100px" });
```

### GSAP Patterns

```javascript
// ── ScrollTrigger reveal
gsap.from(".reveal", {
  scrollTrigger: { trigger: ".reveal", start: "top 85%", toggleActions: "play none none reverse" },
  opacity: 0, y: 60, duration: 0.9, stagger: 0.1, ease: "power4.out"
});
// ── Horizontal scroll section
gsap.to(".horizontal-track", {
  x: () => -(document.querySelector(".horizontal-track").scrollWidth - window.innerWidth),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-container",
    start: "top top", end: "+=3000", pin: true, scrub: 1
  }
});
// ── Text split animation
import SplitType from "split-type";
const split = new SplitType(".headline", { types: "words,chars" });
gsap.from(split.chars, {
  opacity: 0, y: "110%", rotateX: -90,
  stagger: 0.02, duration: 0.7, ease: "back.out(2)"
});
```

---

## 🧩 Phase 5 — Component Library

### Button System

```tsx
// Variant map
const variants = {
  primary:   "bg-accent text-bg font-semibold shadow-glow hover:brightness-110",
  secondary: "bg-surface border border-border text-primary hover:bg-elevated",
  ghost:     "text-secondary hover:text-primary hover:bg-white/5",
  danger:    "bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20",
  outline:   "border border-accent/40 text-accent hover:bg-accent/10"
};
// Sizes
const sizes = {
  sm: "h-7 px-3 text-xs gap-1.5",
  md: "h-9 px-4 text-sm gap-2",
  lg: "h-11 px-6 text-base gap-2.5",
  xl: "h-14 px-8 text-lg gap-3"
};
```

### Card Patterns

```css
/* Glass Card */
.card-glass {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(24px);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06);
}
/* Neumorphic Card */
.card-neumorphic {
  background: #1E1E24;
  border-radius: 20px;
  box-shadow: 8px 8px 20px rgba(0,0,0,0.5), -4px -4px 12px rgba(255,255,255,0.03);
}
/* Neon Border Card */
.card-neon {
  border: 1px solid rgba(110,231,183,0.2);
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(110,231,183,0.03), transparent);
  box-shadow: 0 0 40px rgba(110,231,183,0.05), inset 0 0 40px rgba(110,231,183,0.02);
}
```

### Input System

```css
.input {
  height: 40px;
  padding: 0 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  outline: none;
}
.input:hover { border-color: rgba(255,255,255,0.2); }
.input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px rgba(110,231,183,0.15);
  background: rgba(255,255,255,0.06);
}
```

### Navigation Patterns

```css
/* Floating Nav */
.nav-floating {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(10,10,11,0.8);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 9999px;
  padding: 8px 20px;
}
/* Sidebar Nav */
.nav-sidebar {
  width: 240px;
  height: 100vh;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-subtle);
  position: fixed;
  left: 0; top: 0;
}
/* Tab Bar */
.nav-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: rgba(255,255,255,0.04);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.06);
}
```

### Data Visualization Components

```tsx
// Sparkline
const Sparkline = ({ data, color = "#6EE7B7" }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((v - min) / (max - min)) * 100;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-16">
      <defs>
        <linearGradient id="grad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
};
```

---

## 🌐 Phase 6 — Design Tool Integration

### Figma MCP / API Integration

When Figma MCP is connected:

```
1. Use get_file to retrieve design tokens from Figma Variables
2. Use get_node_info to extract exact spacing, colors, typography
3. Use export_node to get assets (icons, illustrations)
4. Map Figma tokens → CSS variables 1:1
5. Match border-radius, shadow, color exactly from Figma specs
```

**Figma to CSS token mapping:**

```javascript
// Figma fills → CSS
fill.color → `rgba(${r*255}, ${g*255}, ${b*255}, ${a})`
fill.gradientStops → CSS `linear-gradient()`
effect.shadow → CSS `box-shadow: ${x}px ${y}px ${blur}px ${spread}px rgba(...)`
effect.blur → CSS `backdrop-filter: blur(${radius}px)`
// Figma typography → CSS
fontName.family → font-family
fontSize → font-size
fontWeight → font-weight
lineHeightPx → line-height
letterSpacing / fontSize * 100 → letter-spacing (em)
```

### Google Fonts Integration

```html
<!-- Optimized loading with display swap -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900&family=Satoshi:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Variable fonts for fine-tuned control:**

```css
/* Use font-variation-settings for max control */
.display { font-variation-settings: "wght" 720, "opsz" 72, "ital" 1; }
.body    { font-variation-settings: "wght" 420, "opsz" 16; }
```

### Icon Libraries

```bash
# Heroicons (Tailwind team) — clean, professional
npm install @heroicons/react
# Lucide — feather fork, comprehensive
npm install lucide-react
# Phosphor — most expressive, 6 weights
npm install @phosphor-icons/react
# Radix Icons — system UI, precise
npm install @radix-ui/react-icons
# Tabler — 4700+ icons, stroke-based
npm install @tabler/icons-react
```

**Icon sizing system:**

```
xs: 12px  sm: 14px  md: 16px  lg: 20px  xl: 24px  2xl: 32px
```

### Image & Media

```tsx
// Next.js optimized image
import Image from "next/image";
<Image src="/hero.jpg" alt="" fill priority className="object-cover" quality={90} />
// Blur-up placeholder pattern
<Image
  src={url}
  placeholder="blur"
  blurDataURL={base64Placeholder}
  alt={alt}
/>
// Unsplash integration (design mockups)
const unsplash = (query, w=800, h=600) =>
  `https://source.unsplash.com/${w}x${h}/?${query}`;
```

### Design Reference APIs

```javascript
// Coolors palette generation
fetch(`https://coolors.co/generate`)
// Realtime Colors preview
// https://www.realtimecolors.com/?colors=<hex>&fonts=<font>
// Google Fonts metadata
fetch("https://www.googleapis.com/webfonts/v1/webfonts?key=<KEY>&sort=popularity")
// Fontshare CDN (free premium fonts)
// https://api.fontshare.com/v2/css?f[]=satoshi@700,500,400&display=swap
// Shots.so / Screely for mockup wrapping
```

---

## 🖼️ Phase 7 — Visual Effects & Atmosphere

### Background Effects

```css
/* Noise texture overlay */
.noise::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
  opacity: 0.5;
}
/* Gradient mesh background */
.gradient-mesh {
  background:
    radial-gradient(ellipse 80% 60% at 20% 0%, rgba(110,231,183,0.15) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(167,139,250,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 50% 70% at 60% 30%, rgba(251,191,36,0.06) 0%, transparent 50%),
    #0A0A0B;
}
/* Aurora effect */
.aurora {
  background: linear-gradient(
    125deg,
    rgba(110,231,183,0.08) 0%,
    rgba(167,139,250,0.06) 35%,
    rgba(96,165,250,0.04) 70%,
    transparent 100%
  );
  animation: aurora-shift 12s ease-in-out infinite alternate;
}
@keyframes aurora-shift {
  from { filter: hue-rotate(0deg); }
  to   { filter: hue-rotate(60deg); }
}
/* Dot grid pattern */
.dot-grid {
  background-image: radial-gradient(circle, rgba(255,255,255,0.15) 1px, transparent 1px);
  background-size: 24px 24px;
}
/* Line grid pattern */
.line-grid {
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 32px 32px;
}
```

### Special Text Effects

```css
/* Gradient text */
.gradient-text {
  background: linear-gradient(135deg, #6EE7B7, #A78BFA, #60A5FA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
/* Animated gradient text */
.animated-gradient-text {
  background: linear-gradient(90deg, #6EE7B7, #A78BFA, #F59E0B, #6EE7B7);
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: text-shimmer 4s linear infinite;
}
@keyframes text-shimmer {
  from { background-position: 0% center; }
  to   { background-position: 300% center; }
}
/* Outlined text */
.outline-text {
  -webkit-text-stroke: 1.5px rgba(255,255,255,0.5);
  -webkit-text-fill-color: transparent;
}
/* Text with glow */
.glow-text {
  text-shadow: 0 0 20px rgba(110,231,183,0.6), 0 0 60px rgba(110,231,183,0.2);
}
```

### Glassmorphism System

```css
/* Glass levels */
.glass-1 { background: rgba(255,255,255,0.02); backdrop-filter: blur(8px);  border: 1px solid rgba(255,255,255,0.06); }
.glass-2 { background: rgba(255,255,255,0.04); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.08); }
.glass-3 { background: rgba(255,255,255,0.08); backdrop-filter: blur(32px); border: 1px solid rgba(255,255,255,0.12); }
.glass-4 { background: rgba(255,255,255,0.12); backdrop-filter: blur(48px); border: 1px solid rgba(255,255,255,0.16); }
/* Frosted glass with inner glow */
.glass-premium {
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow:
    0 8px 32px rgba(0,0,0,0.4),
    inset 0 1px 0 rgba(255,255,255,0.1),
    inset 0 -1px 0 rgba(0,0,0,0.1);
}
```

---

## 📱 Phase 8 — Responsive & Adaptive Design

### Mobile-First Methodology

```css
/* Base: mobile (320–768px) */
.component { padding: 16px; font-size: 15px; }
/* Tablet (768px+) */
@media (min-width: 768px) {
  .component { padding: 24px; font-size: 16px; }
}
/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .component { padding: 40px; font-size: 17px; }
}
/* Wide (1536px+) */
@media (min-width: 1536px) {
  .container { max-width: 1400px; margin: 0 auto; }
}
```

### Fluid Typography (clamp)

```css
/* Never use fixed px for headings */
h1 { font-size: clamp(2rem, 6vw, 5rem); }
h2 { font-size: clamp(1.5rem, 4vw, 3rem); }
p  { font-size: clamp(0.9rem, 2vw, 1.1rem); }
```

### Touch Targets (Mobile)

```
Minimum tap target: 44×44px (Apple) / 48×48dp (Google)
Minimum spacing between targets: 8px
Bottom nav items: at least 56px height
```

---

## ♿ Phase 9 — Accessibility (WCAG 2.1 AA)

### Color Contrast Ratios

```
Normal text (< 18px): 4.5:1 minimum
Large text (≥ 18px or bold ≥ 14px): 3:1 minimum
UI components (borders, icons): 3:1 minimum
Focus indicators: 3:1 against adjacent color
```

**Contrast checking:**

```javascript
// Quick luminance check
const luminance = (r, g, b) => {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};
const contrast = (l1, l2) => (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
```

### Focus Management

```css
/* Never remove focus rings — style them instead */
:focus-visible {
  outline: 2px solid var(--color-accent-primary);
  outline-offset: 3px;
  border-radius: 4px;
}
/* Custom focus ring */
.button:focus-visible {
  box-shadow: 0 0 0 3px rgba(110,231,183,0.4);
  outline: none;
}
```

### Semantic HTML Checklist

```html
<!-- Always use semantic elements -->
<main>, <nav>, <header>, <footer>, <article>, <section>, <aside>
<button> for actions (never <div> with onClick)
<a href> for navigation (never <button>)
<label> always paired with <input>
aria-label on icon-only buttons
role="alert" on dynamic error messages
aria-live="polite" on live regions
alt="" on decorative images
```

### Motion Accessibility

```css
/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## ⚡ Phase 10 — Performance Optimization

### Core Web Vitals Targets

```
LCP (Largest Contentful Paint): < 2.5s
FID / INP (Interaction to Next Paint): < 200ms
CLS (Cumulative Layout Shift): < 0.1
FCP (First Contentful Paint): < 1.8s
TTFB (Time to First Byte): < 800ms
```

### CSS Performance

```css
/* Use transform + opacity for animations (GPU-composited) */
/* ✅ */ .animate { transform: translateY(0); opacity: 1; }
/* ❌ */ .animate { top: 0; height: 200px; }
/* Contain expensive elements */
.card { contain: layout style paint; }
/* will-change only when needed */
.animated-element { will-change: transform; }
/* Remove after animation: element.style.willChange = "auto" */
/* content-visibility for off-screen sections */
.below-fold { content-visibility: auto; contain-intrinsic-size: 0 500px; }
```

### Image Optimization

```html
<!-- Modern formats -->
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="..." loading="lazy" decoding="async">
</picture>
<!-- Responsive images -->
<img
  srcset="image-400.webp 400w, image-800.webp 800w, image-1200.webp 1200w"
  sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
  src="image-800.webp" alt="..."
>
```

### Bundle Optimization

```javascript
// Dynamic imports for code splitting
const HeavyComponent = lazy(() => import("./HeavyComponent"));
// Tree-shaking friendly imports
import { specific } from "lucide-react"; // ✅
import * as Icons from "lucide-react";   // ❌
// Preload critical resources
<link rel="preload" href="/fonts/satoshi.woff2" as="font" crossorigin>
<link rel="preload" href="/images/hero.webp" as="image">
```

---

## 🌟 Phase 11 — World-Class Design References

Study these as the gold standard:

### Products / Apps

| Product               | Why study it                                                     |
| --------------------- | ---------------------------------------------------------------- |
| **Linear**      | Perfect type hierarchy, keyboard-first UX, surgical color use    |
| **Vercel**      | Zero-noise documentation design, dark mode mastery               |
| **Stripe**      | Trust through design, micro-copy perfection, illustration system |
| **Raycast**     | Mac-native design language, command palette UX                   |
| **Arc Browser** | Personality in UI, color theming system, space design            |
| **Craft**       | Typography-first document design, paper metaphor                 |
| **Framer**      | Marketing site animation, scroll storytelling                    |
| **Loom**        | Onboarding UX, empty state design                                |
| **Notion**      | Information architecture, icon consistency                       |
| **Figma**       | Toolbar design, property panel UX                                |
| **Superhuman**  | Speed-focused UI, command palette, power user design             |

### Landing Page Inspiration

| Site                    | Why                                              |
| ----------------------- | ------------------------------------------------ |
| **stripe.com**    | Section rhythm, illustration style, social proof |
| **linear.app**    | Product shot integration, concise copy design    |
| **resend.com**    | Dark mode landing, developer audience            |
| **clerk.com**     | Code + design integration, auth UX               |
| **cal.com**       | Open-source landing, feature grid                |
| **liveblocks.io** | Animation quality, product demo integration      |
| **supabase.com**  | Green brand system, documentation design         |

### Design Inspiration Sites

```
Dribbble.com       — UI shots, color palettes
Behance.net        — Full case studies, brand identities
Mobbin.com         — Mobile UI patterns, flows
Screenlane.com     — Web UI detail shots
Land-book.com      — Landing page collection
Godly.website      — Premium landing pages
Awwwards.com       — SOTD award winners
Cosmos.so          — Curated visual design board
Arena.are          — Design thinking references
Refero.design      — SaaS UI patterns
Pageflows.com      — UX flow recordings
```

### Typography Resources

```
fonts.google.com       — 1500+ free fonts
fontshare.com          — Premium free fonts (Satoshi, Cabinet, Clash)
variable-fonts.com     — Variable font explorer
fontpair.co            — AI font pairing
typ.io                 — Real-world font usage
fonts.adobe.com        — Adobe Fonts library
```

### Color Resources

```
coolors.co             — Palette generator
oklch.com              — Perceptual color space (use for design systems)
huemint.com            — AI color palette for UI
colorhunt.co           — Curated palettes
happyhues.co           — Palettes in context
reasonable.work/colors — Accessible color system
accessible-palette.com — WCAG-safe color generation
```

### Icon & Illustration Resources

```
heroicons.com          — MIT, React/SVG
lucide.dev             — Feather fork, 1000+ icons
phosphoricons.com      — Most expressive, 6 weights
tabler.io/icons        — 4700+ stroke icons
iconoir.com            — Clean, consistent set
undraw.co              — Open-source SVG illustrations
storyset.com           — Animated illustrations
blush.design           — Customizable characters
shapefest.com          — 3D shapes library
3dicons.co             — Premium 3D icons
```

### CSS / Code Resources

```
uiverse.io             — Community CSS components
ui.aceternity.com      — Animated Tailwind components
magicui.design         — React animation components
animata.design         — Copy-paste animations
ui.shadcn.com          — Radix + Tailwind system
headlessui.com         — Accessible unstyled components
radix-ui.com           — Primitive components
```

---

## 📦 Phase 12 — Deliverable Checklist

Before shipping any design, verify:
**Visual Quality**

- [ ] Consistent 8pt spacing throughout
- [ ] Font sizes follow scale (no random values)
- [ ] Colors come from token system
- [ ] Shadows have consistent direction (light from top-left)
- [ ] Border radii consistent across component family
- [ ] Empty states designed
- [ ] Loading/skeleton states designed
- [ ] Error states designed
  **Interaction**
- [ ] All interactive elements have hover state
- [ ] All interactive elements have focus state
- [ ] All interactive elements have active/pressed state
- [ ] Transitions are smooth (200–400ms, ease-out)
- [ ] No janky repaints (use transform not position)
  **Responsive**
- [ ] Works on 375px (iPhone SE) — smallest target
- [ ] Works on 768px (iPad)
- [ ] Works on 1440px (desktop)
- [ ] Images not distorted at any size
- [ ] Text readable at all sizes (no overflow)
  **Accessibility**
- [ ] Color contrast ≥ 4.5:1 for body text
- [ ] All images have alt text (or alt="" if decorative)
- [ ] All buttons have accessible labels
- [ ] Form inputs have labels
- [ ] Focus management is logical
- [ ] Reduced motion supported
  **Performance**
- [ ] No render-blocking resources
- [ ] Images lazy-loaded below fold
- [ ] Fonts preloaded
- [ ] Animations use transform/opacity only
- [ ] No layout shift (CLS < 0.1)

---

## 🔥 Quick-Start Templates

### Hero Section (Dark, Glassmorphic)

```tsx
export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Gradient mesh background */}
      <div className="absolute inset-0 bg-[#0A0A0B]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_20%_0%,rgba(110,231,183,0.12)_0%,transparent_60%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_80%_100%,rgba(167,139,250,0.1)_0%,transparent_60%)]" />
      {/* Dot grid */}
      <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(255,255,255,0.12)_1px,transparent_1px)] bg-[size:24px_24px] opacity-40" />
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-8
          rounded-full border border-white/10 bg-white/5 backdrop-blur-sm
          text-xs font-medium text-white/60 uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Now in public beta
        </div>
        <h1 className="text-[clamp(3rem,9vw,7rem)] font-bold leading-[0.95]
          tracking-[-0.04em] text-white mb-6">
          Design that
          <span className="bg-gradient-to-r from-emerald-300 via-violet-300 to-blue-300
            bg-clip-text text-transparent"> doesn't </span>
          apologize
        </h1>
        <p className="text-lg text-white/50 max-w-xl mx-auto mb-10 leading-relaxed">
          Build interfaces that make people stop scrolling.
          Every pixel intentional. Every interaction choreographed.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button className="h-12 px-7 rounded-full bg-white text-black
            font-semibold text-sm hover:bg-white/90 transition-all
            hover:shadow-[0_0_40px_rgba(255,255,255,0.3)]">
            Get started free
          </button>
          <button className="h-12 px-7 rounded-full border border-white/15
            text-white/80 text-sm font-medium hover:border-white/30
            hover:bg-white/5 transition-all backdrop-blur-sm">
            View examples →
          </button>
        </div>
      </div>
    </section>
  );
}
```

---

*Remember: Great design is not decoration — it's the elimination of everything that doesn't serve the user. Then make what remains extraordinary.*
