// Scroll-reveal for .aviary-reveal elements, the start signal for the
// hero's CSS-only draw-in animations, and a small typewriter cycle for the
// decorative terminal. Progressive enhancement only: every element this
// touches is fully visible/legible with this script absent (see
// extra.css's `.aviary-reveal` base state and the terminal's static
// default text), and nothing here runs under `prefers-reduced-motion: reduce`.
(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.documentElement.classList.add('aviary-js');

  if (reduceMotion) {
    document.documentElement.classList.add('aviary-reduced-motion');
    return;
  }

  document.documentElement.classList.add('aviary-motion-ready');

  if ('IntersectionObserver' in window) {
    var makeObserver = function (options) {
      return new IntersectionObserver(function (entries, self) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            self.unobserve(entry.target);
          }
        });
      }, options);
    };

    // Generic reveals (hero, cards): fire as soon as they edge into view.
    var generic = makeObserver({ threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    // Scrollytelling panels fire much later, and the two settings do
    // different jobs. rootMargin's -45% bottom shrinks the trigger zone to
    // the top ~55% of the viewport, so a panel must be scrolled well up the
    // screen before it counts as visible at all -- that is the "more
    // scrolling required" part, and unlike threshold it does not scale with
    // the panel's own height. threshold then asks for 30% of the panel to be
    // inside that reduced zone. Raising min-height alone (88vh) did not delay
    // anything, because threshold is a fraction of the panel: a taller panel
    // reaches 15% of itself at the same point on screen.
    var scrolly = makeObserver({ threshold: 0.3, rootMargin: '0px 0px -45% 0px' });

    document.querySelectorAll('.aviary-reveal').forEach(function (el) {
      var isPanel = el.classList.contains('aviary-scrolly__panel');
      (isPanel ? scrolly : generic).observe(el);
    });
  } else {
    // No observer support: just show everything, skip the choreography.
    document.querySelectorAll('.aviary-reveal').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  /**
   * Type/erase-loop through a comma-separated `data-commands` list on an
   * element, starting from whatever static text it already contains (the
   * no-JS/reduced-motion fallback state).
   * @param {HTMLElement} el
   * @returns {void}
   */
  function typewriterLoop(el) {
    var words = (el.getAttribute('data-commands') || '')
      .split(',')
      .map(function (s) { return s.trim(); })
      .filter(Boolean);
    if (words.length < 2) return;

    var index = 0;
    var TYPE_MS = 55;
    var ERASE_MS = 30;
    var HOLD_MS = 1800;

    function type(word, done) {
      var pos = 0;
      (function step() {
        el.textContent = word.slice(0, pos);
        pos += 1;
        if (pos <= word.length) {
          setTimeout(step, TYPE_MS);
        } else {
          done();
        }
      })();
    }

    function erase(word, done) {
      var pos = word.length;
      (function step() {
        el.textContent = word.slice(0, pos);
        pos -= 1;
        if (pos >= 0) {
          setTimeout(step, ERASE_MS);
        } else {
          done();
        }
      })();
    }

    (function cycle() {
      var current = words[index % words.length];
      setTimeout(function () {
        erase(current, function () {
          index += 1;
          type(words[index % words.length], cycle);
        });
      }, HOLD_MS);
    })();
  }

  document.querySelectorAll('.aviary-terminal__type').forEach(typewriterLoop);
})();
