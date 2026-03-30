
// Scroll progress
const sp=document.getElementById('sp');
window.addEventListener('scroll',()=>{sp.style.width=(window.scrollY/(document.documentElement.scrollHeight-window.innerHeight)*100)+'%';},{passive:true});

// Nav scroll
const nav=document.getElementById('nav');
window.addEventListener('scroll',()=>nav.classList.toggle('scrolled',window.scrollY>50),{passive:true});

// Cursor (desktop only – skip on touch devices for performance)
const cd=document.getElementById('cd'),cr=document.getElementById('cr');
if(window.innerWidth>900){
  let cx=0,cy=0,rx=0,ry=0;
  document.addEventListener('mousemove',e=>{cx=e.clientX;cy=e.clientY;},{passive:true});
  (function a(){rx+=(cx-rx)*.12;ry+=(cy-ry)*.12;cd.style.left=cx+'px';cd.style.top=cy+'px';cr.style.left=rx+'px';cr.style.top=ry+'px';requestAnimationFrame(a);})();
  document.querySelectorAll('a,button,.faq-q,.svc,.proj-feat,.proj-sm,.wi,.p-item').forEach(el=>{
    el.addEventListener('mouseenter',()=>{cr.style.width='40px';cr.style.height='40px';},{passive:true});
    el.addEventListener('mouseleave',()=>{cr.style.width='28px';cr.style.height='28px';},{passive:true});
  });
} else {
  cd.style.display='none';cr.style.display='none';
}

// Mobile menu
function openMM(){document.getElementById('mm').classList.add('open');document.body.style.overflow='hidden';}
function closeMM(){document.getElementById('mm').classList.remove('open');document.body.style.overflow='';}

// Intersection observer - reveal + stagger
const io=new IntersectionObserver((entries)=>{
  entries.forEach((e,i)=>{
    if(e.isIntersecting){
      const d=+(e.target.dataset.delay||0);
      setTimeout(()=>e.target.classList.add('vis'),d);
    }
  });
},{threshold:0.1,rootMargin:'0px 0px -40px 0px'});

document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
document.querySelectorAll('.stagger').forEach((el,i)=>{
  el.dataset.delay=(i%6)*80;
  io.observe(el);
});
document.querySelectorAll('.proc-step').forEach((el,i)=>{
  el.dataset.delay=i*100;
  io.observe(el);
});

// FAQ
function faq(el){
  const it=el.parentElement;
  const isOpen=it.classList.contains('open');
  document.querySelectorAll('.faq-item.open').forEach(f=>f.classList.remove('open'));
  if(!isOpen)it.classList.add('open');
}

// Form sub

// Foto items + cards: activate when scrolled into center of viewport
(function(){
  var fotoEls=document.querySelectorAll('.foto-item,.foto-card');
  if(!fotoEls.length) return;
  function checkFotos(){
    var cy=window.innerHeight/2;
    fotoEls.forEach(function(el){
      var r=el.getBoundingClientRect();
      var elCenter=r.top+r.height/2;
      var dist=Math.abs(cy-elCenter);
      if(dist<r.height*0.8){
        el.classList.add('in-view');
      } else {
        el.classList.remove('in-view');
      }
    });
  }
  window.addEventListener('scroll',checkFotos,{passive:true});
  checkFotos();
})();

// Mobile & Tablet: observe additional elements for entrance animations
if(window.innerWidth<=900){
  document.querySelectorAll('.c-item,.svc,.proj-feat,.proj-sm,.faq-item,.wi,.p-item,.foto-card').forEach(function(el){
    io.observe(el);
  });
}
