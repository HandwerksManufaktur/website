/* Leistungsseiten — dieselbe Bedienung wie auf der Startseite:
   Burger-Menü mit Abdunklung und Escape, FAQ über grid-template-rows,
   Nav wird beim Scrollen fester. Bewusst klein gehalten. */

function navHoehe(){
  var n = document.getElementById('nav'); if(!n) return;
  document.documentElement.style.setProperty('--navh', Math.round(n.getBoundingClientRect().height) + 'px');
}
navHoehe();
addEventListener('resize', navHoehe, { passive:true });
addEventListener('load', navHoehe);

addEventListener('scroll', function(){
  var n = document.getElementById('nav');
  if(n) n.classList.toggle('scrolled', scrollY > 30);
}, { passive:true });

function toggleMenu(auf){
  var b = document.getElementById('navBurger'),
      p = document.getElementById('mnav'),
      bd = document.getElementById('mnavBd');
  if(!b || !p) return;
  var offen = auf === 0 ? false : b.getAttribute('aria-expanded') !== 'true';
  b.setAttribute('aria-expanded', offen ? 'true' : 'false');
  b.setAttribute('aria-label', offen ? 'Menü schließen' : 'Menü öffnen');
  navHoehe();
  if(offen){
    p.hidden = false; if(bd) bd.hidden = false;
    document.body.style.overflow = 'hidden';
    requestAnimationFrame(function(){ p.classList.add('auf'); if(bd) bd.classList.add('auf'); });
  } else {
    p.classList.remove('auf'); if(bd) bd.classList.remove('auf');
    document.body.style.overflow = '';
    setTimeout(function(){ p.hidden = true; if(bd) bd.hidden = true; }, 300);
  }
}
addEventListener('keydown', function(e){
  if(e.key === 'Escape'){
    var b = document.getElementById('navBurger');
    if(b && b.getAttribute('aria-expanded') === 'true') toggleMenu(0);
  }
});
addEventListener('resize', function(){
  var b = document.getElementById('navBurger');
  if(innerWidth > 860 && b && b.getAttribute('aria-expanded') === 'true') toggleMenu(0);
}, { passive:true });

/* FAQ: immer nur eine offen, animiert wird die Zeilenhöhe, nicht max-height */
function faq(el){
  var it = el.parentElement, offen = it.classList.contains('open');
  document.querySelectorAll('.faq-item.open').forEach(function(f){ f.classList.remove('open'); });
  if(!offen) it.classList.add('open');
}

/* Kundenvideos: erst laden, wenn sie im Bild sind — vier Clips sind rund 2,5 MB,
   die soll niemand mitschleppen, der nie so weit scrollt. Wer weniger Bewegung
   eingestellt hat, bekommt das Standbild statt der Schleife. */
(function(){
  var ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var vids = document.querySelectorAll('.lp-vid video[data-quelle]');
  if(!vids.length) return;
  function laden(v){
    if(v.dataset.geladen) return;
    v.dataset.geladen = '1';
    var q = document.createElement('source');
    q.src = v.dataset.quelle; q.type = 'video/mp4';
    v.appendChild(q); v.load();
    if(!ruhig) v.play().catch(function(){});
  }
  if(!('IntersectionObserver' in window)){ vids.forEach(laden); return; }
  var beobachter = new IntersectionObserver(function(eintraege){
    eintraege.forEach(function(e){
      if(e.isIntersecting){ laden(e.target); }
      else if(e.target.dataset.geladen && !e.target.paused){ e.target.pause(); }
    });
  }, { rootMargin: '200px 0px' });
  vids.forEach(function(v){ beobachter.observe(v); });
})();
