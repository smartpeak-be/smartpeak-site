document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("hoofdmenu");
  if (!toggle || !nav) return;

  const setOpen = (open) => {
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.textContent = open ? "Sluiten" : "Menu";
  };

  toggle.addEventListener("click", () => setOpen(!nav.classList.contains("is-open")));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      setOpen(false);
      toggle.focus();
    }
  });
});

// Voorlezen: reads the page aloud with the speech built into the browser (no external service,
// nothing is sent anywhere). The buttons only appear when the browser has a Dutch voice.
document.addEventListener("DOMContentLoaded", () => {
  const synth = window.speechSynthesis;
  const main = document.getElementById("inhoud");
  const heading = main && main.querySelector("h1");
  if (!synth || typeof SpeechSynthesisUtterance === "undefined" || !heading) return;

  const BLOCKS = "h1, h2, h3, h4, p, li, dt, dd, figcaption, th, td, blockquote";
  const SKIP = ".read-aloud, .spa, .reviews-mount, .reviews-static, form, nav, script, noscript, [hidden], [aria-hidden='true'], .table-scroll caption";
  const SPEAKER = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/></svg>';

  const bar = document.createElement("div");
  bar.className = "read-aloud";
  bar.setAttribute("role", "group");
  bar.setAttribute("aria-label", "Voorlezen");
  bar.hidden = true;
  bar.innerHTML = `<button type="button" class="read-aloud-play">${SPEAKER}<span>Lees voor</span></button>` +
    '<button type="button" class="read-aloud-stop" hidden>Stop</button>';
  const lead = heading.parentElement.querySelector(".lead");
  (lead || heading).after(bar);

  const play = bar.querySelector(".read-aloud-play");
  const label = play.querySelector("span");
  const stop = bar.querySelector(".read-aloud-stop");
  let voice = null;
  let queue = [];
  let index = 0;
  let state = "idle";

  const dutchVoice = () => {
    const voices = synth.getVoices();
    return voices.find((v) => /^nl[-_]BE/i.test(v.lang)) || voices.find((v) => /^nl\b/i.test(v.lang)) || null;
  };
  const findVoice = () => {
    voice = dutchVoice();
    bar.hidden = !voice;
  };
  findVoice();
  synth.addEventListener?.("voiceschanged", findVoice);

  // Start at the page title; split long blocks into sentences, because some browsers stop
  // speaking in the middle of a long text.
  const parts = () => [...main.querySelectorAll(BLOCKS)]
    .filter((el) => (el === heading || heading.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING)
      && !el.closest(SKIP) && !el.querySelector(BLOCKS) && el.innerText.trim() && el.offsetParent !== null)
    .flatMap((el) => {
      const text = el.innerText.replace(/\s+/g, " ").trim();
      const sentences = text.match(/[^.!?]+(?:[.!?]+(?=\s|$)|$)/g) || [text];
      return sentences.map((sentence) => ({ el, text: sentence.trim() })).filter((part) => part.text);
    });

  const mark = (el) => {
    main.querySelectorAll(".is-reading").forEach((e) => e.classList.remove("is-reading"));
    if (!el) return;
    el.classList.add("is-reading");
    const r = el.getBoundingClientRect();
    if (r.top < 80 || r.bottom > window.innerHeight) {
      const smooth = window.matchMedia("(prefers-reduced-motion: no-preference)").matches;
      el.scrollIntoView({ block: "center", behavior: smooth ? "smooth" : "auto" });
    }
  };

  const setState = (next) => {
    state = next;
    label.textContent = next === "playing" ? "Pauzeer" : next === "paused" ? "Verder lezen" : "Lees voor";
    play.setAttribute("aria-pressed", String(next === "playing"));
    stop.hidden = next === "idle";
    if (next === "idle") mark(null);
  };

  const speakNext = () => {
    if (state !== "playing") return;
    if (index >= queue.length) { setState("idle"); return; }
    const { el, text } = queue[index];
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.lang = voice.lang;
    utterance.onend = () => { index += 1; speakNext(); };
    utterance.onerror = (event) => { if (event.error !== "interrupted" && event.error !== "canceled") { index += 1; speakNext(); } };
    mark(el);
    synth.speak(utterance);
  };

  play.addEventListener("click", () => {
    if (state === "idle") {
      synth.cancel();
      queue = parts();
      index = 0;
      setState("playing");
      speakNext();
    } else if (state === "playing") {
      synth.pause();
      setState("paused");
    } else {
      synth.resume();
      setState("playing");
    }
  });
  stop.addEventListener("click", () => {
    setState("idle");
    synth.cancel();
    play.focus();
  });
  window.addEventListener("pagehide", () => synth.cancel());
});

// Reviews: the build puts the published reviews in the HTML (for search engines and as a fallback).
// The widget loads the current list in a hidden mount; once it has, it replaces the static copy,
// so a review approved after the last build is visible at once. On a load error the copy stays.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".reviews-live").forEach((box) => {
    const mount = box.querySelector(".reviews-mount");
    const copy = box.querySelector(".reviews-static");
    if (!mount || !copy) return;
    const swap = () => {
      const empty = mount.querySelector(".sp-review-widget__empty");
      const loaded = mount.querySelector(".sp-review-widget__track") || (empty && /^Nog geen/.test(empty.textContent.trim()));
      if (!loaded) return false;
      copy.remove();
      mount.hidden = false;
      return true;
    };
    if (swap()) return;
    const watch = new MutationObserver(() => { if (swap()) watch.disconnect(); });
    watch.observe(mount, { childList: true, subtree: true });
  });
});
