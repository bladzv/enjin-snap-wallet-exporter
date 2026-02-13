# UI/UX Best Practices & Standards for Secure Development

## 1. Design Principles

**Clarity Over Cleverness** - Every interface element should have a clear, singular purpose. Users should never guess what something does.

**Progressive Disclosure** - Show only what's needed at each step. Complex features emerge as users need them.

**Consistency** - Same actions produce same results. Same elements behave the same way everywhere.

**Forgiveness** - Make errors hard to commit, easy to undo. Never punish users for mistakes.

**Accessibility First** - Design for WCAG 2.1 AA minimum. Screen readers, keyboard navigation, and color contrast are not afterthoughts.

## 2. Layout & Spacing

**Spacing Scale** - Use a consistent 8px or 4px base unit system: 4, 8, 12, 16, 24, 32, 48, 64, 96px.

**White Space** - Generous breathing room between sections (48-64px), moderate within components (16-24px), tight within elements (8-12px).

**Grid System** - Use 12-column grids for desktop, 4-column for mobile. Maintain consistent gutters (16-24px).

**Max Width** - Content containers should max at 1200-1400px. Text columns at 65-75 characters (about 600-700px).

**Responsive Breakpoints** - Mobile: 320-767px, Tablet: 768-1023px, Desktop: 1024-1439px, Large: 1440px+

## 3. Typography

**Hierarchy** - H1: 32-48px, H2: 24-32px, H3: 20-24px, Body: 16-18px, Small: 14px, Caption: 12px.

**Line Height** - Headings: 1.2-1.3, Body text: 1.5-1.6, Small text: 1.4.

**Font Weights** - Use no more than 3-4 weights. Regular (400) for body, Medium (500-600) for emphasis, Bold (700) for headings.

**Font Stack** - System fonts for performance: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif.

**Measure** - Never exceed 75 characters per line. 45-65 is optimal for readability.

## 4. Color System

**Palette Structure** - Primary (brand), Secondary (accent), Neutral (gray scale 50-900), Semantic (success, warning, error, info).

**Contrast Ratios** - Normal text: 4.5:1 minimum, Large text (18px+): 3:1 minimum, Interactive elements: 3:1 against adjacent colors.

**Dark Mode** - Provide both light and dark themes. Never use pure black (#000), use dark grays (#0A0A0A to #1A1A1A).

**Color Blindness** - Never rely on color alone. Use icons, patterns, or text labels alongside color indicators.

## 5. Buttons

**Hierarchy** - Primary (filled), Secondary (outlined), Tertiary (text only), Destructive (red/warning).

**Sizing** - Small: 32px, Medium: 40px, Large: 48px height. Minimum touch target: 44x44px.

**States** - Default, Hover, Active, Focus, Disabled, Loading. Each must be visually distinct.

**Labels** - Use verb-first language: "Save Changes", "Delete Account", "Download Report". Never ambiguous words like "Submit" or "OK" alone.

**Icon Placement** - Leading icons for actions, trailing icons for dropdowns or external links.

**Loading States** - Replace button content with spinner, disable interaction, maintain button dimensions.

## 6. Forms & Inputs

**Field Labels** - Always above the field, left-aligned, sentence case. Never inside as placeholders alone.

**Input Height** - 40-48px for touch devices, 36-40px for desktop. Consistent across all input types.

**Error Handling** - Inline validation on blur, not on every keystroke. Show errors below the field with icon and clear message.

**Required Fields** - Mark with asterisk (*) and explain at form top. Don't rely on color alone.

**Help Text** - Use for complex fields. Place below field, above error messages. Keep under 100 characters.

**Autocomplete** - Implement proper HTML autocomplete attributes for security and UX.

**Password Fields** - Include show/hide toggle, strength indicator, clear requirements list upfront.

## 7. Modals & Overlays

**Purpose** - Use sparingly. Only for critical actions, confirmations, or self-contained tasks.

**Dismissal** - Multiple ways to close: X button (top-right), Cancel button, Escape key, click outside (for non-critical modals).

**Size** - Small: 400px, Medium: 600px, Large: 800px width. Never exceed 90vw or 90vh.

**Focus Management** - Trap focus within modal, return focus to trigger element on close.

**Animation** - Fade in/out with 200-300ms ease. Slight scale (0.95 to 1) for polish.

**Mobile** - Full screen or bottom sheets on mobile. Never tiny modals on small screens.

## 8. Navigation

**Depth Limit** - Keep navigation 3 levels deep maximum. If deeper, reconsider your IA.

**Active States** - Always indicate current location with visual cue (color, underline, background).

**Mobile Navigation** - Hamburger menu acceptable but consider bottom navigation for 3-5 primary items.

**Breadcrumbs** - Use for deep hierarchies. Show path from home, make each level clickable except current.

**Search** - Prominent placement if content-heavy. Include autocomplete suggestions, recent searches.

## 9. Tables & Data Display

**Responsive Strategy** - Stack cards on mobile, horizontal scroll for narrow tables, hide non-critical columns.

**Sorting** - Show sort direction with arrows. Allow multi-column sort for power users.

**Pagination** - Show current page, total pages, and items per page option. Include "Go to page" for large datasets.

**Row Actions** - Consistent placement (right side or hover-reveal). Use icons with tooltips.

**Empty States** - Never show blank tables. Provide illustration, message, and action to populate.

## 10. Loading & Feedback

**Loading Indicators** - Skeleton screens for content, spinners for actions, progress bars for known duration.

**Optimistic UI** - Update UI immediately for fast actions, rollback if error occurs.

**Toast Notifications** - Auto-dismiss after 5-7 seconds for success, keep errors until dismissed. Max one at a time.

**Progress States** - Show percentage, time remaining, and cancel option for long operations.

## 11. Icons & Imagery

**Icon Size** - 16px (small), 20px (default), 24px (large), 32px (extra large). Align to 8px grid.

**Icon System** - Use single icon library (Heroicons, Lucide, Feather). Maintain consistent stroke width (1.5-2px).

**Alt Text** - Descriptive for informative images, empty for decorative. Never "image of" or "picture of".

**Aspect Ratios** - Maintain consistent ratios: 16:9 for media, 1:1 for avatars, 4:3 for thumbnails.

**Image Optimization** - WebP with fallback, lazy loading below fold, responsive sizes with srcset.

## 12. Animation & Transitions

**Duration** - Micro: 100-200ms, Standard: 200-300ms, Complex: 300-500ms. Never exceed 500ms for UI.

**Easing** - Ease-out for entrances, ease-in for exits, ease-in-out for attention-seeking animations.

**Purpose** - Only animate to communicate, never to decorate. Guide attention, show relationships, indicate state changes.

**Reduced Motion** - Respect prefers-reduced-motion media query. Provide instant transitions as fallback.

## 13. Accessibility (WCAG 2.1 AA)

**Keyboard Navigation** - All interactive elements reachable via Tab. Logical order. Visible focus indicators.

**Screen Readers** - Semantic HTML (header, nav, main, article), ARIA labels where needed, skip links.

**Focus Management** - Never remove focus outlines without replacement. Manage focus for modals and dynamic content.

**Error Identification** - Programmatically identify errors with ARIA. Provide suggestions to fix.

**Touch Targets** - Minimum 44x44px for all interactive elements. 8px spacing between adjacent targets.

## 14. Security-Focused UX

**Password Visibility** - Allow users to see passwords while typing. Use toggle icon.

**Session Timeout** - Warn users 2-5 minutes before timeout. Allow extension without data loss.

**Sensitive Data** - Mask by default (cards, SSN). Provide reveal option with re-authentication for high sensitivity.

**Multi-Factor Auth** - Clear setup flow, backup codes prominently displayed, device trust options.

**Permissions** - Just-in-time requests with clear explanation of why. Never ask unnecessarily.

**Error Messages** - Generic for security failures ("Invalid credentials") never reveal which field is wrong.

**HTTPS Visual** - Show secure connection indicators. Warn prominently if connection degrades.

## 15. Performance & Optimization

**Perceived Performance** - Show content immediately, load data progressively. Skeleton screens beat spinners.

**Critical Path** - Inline critical CSS, defer non-critical scripts, lazy load below fold.

**Image Loading** - Blur-up or dominant color placeholders. Dimension reservations to prevent layout shift.

**Debouncing** - Debounce search inputs (300ms), throttle scroll events (100ms).

**Bundle Size** - Code split by route. Lazy load heavy components. Monitor with performance budget.

## 16. Microcopy & Content

**Error Messages** - Explain what happened, why, and how to fix. Never blame the user.

**Empty States** - Explain why it's empty, what goes here, and how to add content. Friendly tone.

**Placeholder Text** - Show format examples: "name@company.com" not "Enter your email".

**Button Labels** - Action-oriented and specific: "Delete 3 files" not "Delete", "Continue to payment" not "Next".

**Confirmation Dialogs** - State consequences clearly. "Delete account" buttons should say "Delete" not "Yes".

## 17. Mobile-Specific Patterns

**Bottom Navigation** - For 3-5 primary actions. Icons with labels. Active state prominent.

**Thumb Zones** - Place primary actions in lower third. Avoid top corners.

**Pull to Refresh** - Standard gesture for content updates. Show clear loading indicator.

**Swipe Actions** - Reveal destructive actions (delete, archive) with swipe. Provide undo.

**Safe Areas** - Respect notches and system UI. Use env(safe-area-inset-*).

## 18. Component States

**Every Interactive Element Needs**: Default, Hover, Focus, Active, Disabled, Loading, Error, Success.

**State Priority** - Error > Loading > Disabled > Success > Active > Focus > Hover > Default.

**Visual Distinction** - Each state must be perceivable without color alone. Use opacity, icons, or borders.

## 19. Design Tokens

**Structure** - Semantic tokens reference base tokens. Components use semantic tokens only.

**Naming** - base-color-blue-500, semantic-color-primary, component-button-background.

**Scale** - Size: 0.25rem increments, Color: 50-900 scale, Shadow: 4-5 levels.

**Documentation** - Every token documented with usage guidelines and examples.

## 20. Testing & Validation

**Browser Testing** - Latest 2 versions of Chrome, Firefox, Safari, Edge. IE11 if required.

**Device Testing** - iOS Safari, Android Chrome, plus 2-3 real devices minimum.

**Accessibility Audit** - Automated (axe, Lighthouse) plus manual keyboard and screen reader testing.

**Performance Budget** - First Contentful Paint < 1.8s, Largest Contentful Paint < 2.5s, Total Blocking Time < 200ms.

**Usability Testing** - 5 users minimum per iteration. Watch where they struggle, not what they say.

---

**Remember**: Good UI/UX is invisible. Users should accomplish their goals without thinking about the interface. Security should enable, not obstruct. Every design decision should serve the user's needs while protecting their data and privacy.
