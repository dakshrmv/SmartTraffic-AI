// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a =>
  a.addEventListener('click', e => {
    const t = document.querySelector(a.getAttribute('href'));
    if (!t) return;
    e.preventDefault();
    t.scrollIntoView({ behavior: "smooth" });
  })
);

// Active nav highlight
function updateNav(){
  const curr = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll("nav a")
    .forEach(a => a.classList.toggle("active", a.getAttribute("href") == curr));
}
updateNav();

// Mobile menu toggle
function toggleMobileMenu(){
  document.querySelector("nav ul").classList.toggle("mobile-active");
}

if(window.innerWidth <= 768){
  const nav=document.querySelector("nav .container");
  if(!document.querySelector(".mobile-menu-btn")){
    let b=document.createElement("button");
    b.className="mobile-menu-btn";
    b.textContent="☰";
    b.onclick=toggleMobileMenu;
    nav.appendChild(b);
  }
}

// Parallax hero
const hero = document.querySelector(".hero");
window.addEventListener("scroll", () => {
  if(hero) hero.style.transform = `translateY(${window.scrollY * 0.25}px)`;
});

// Scroll progress bar
window.addEventListener("scroll", () => {
  const height = document.documentElement.scrollHeight - window.innerHeight;
  const scrolled = (window.scrollY / height) * 100;
  document.querySelector("nav").style.setProperty("--progress", scrolled + "%");
});

// Typewriter effect (hero tagline)
(function(){
  let t=document.querySelector(".tagline"); if(!t) return;
  let text=t.textContent;
  t.textContent="";
  let i=0;
  (function type(){
    if(i<text.length){ t.textContent+=text[i++]; setTimeout(type,40);}
  })();
})();

// Counter animation
function animateCounter(el, target, duration=2000) {
  let start=0;
  let increment=target/(duration/16);
  const timer=setInterval(()=>{
    start+=increment;
    if(start>=target){ el.textContent=target; clearInterval(timer);}
    else{ el.textContent=Math.floor(start);}
  },16);
}

const counterObs = new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting && !e.target.dataset.animated){
      e.target.dataset.animated="true";
      animateCounter(e.target, parseInt(e.target.textContent));
    }
  });
},{threshold:0.5});

document.querySelectorAll(".stat-number").forEach(s=>counterObs.observe(s));
