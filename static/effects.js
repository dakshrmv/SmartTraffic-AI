// Scroll reveal
const obs=new IntersectionObserver(entries=>{
  entries.forEach(ent=>{
    if(ent.isIntersecting){
      ent.target.classList.add("reveal");
      obs.unobserve(ent.target);
    }
  });
},{threshold:0.12});

document.querySelectorAll(
  "section, .card, .feature-card, .team-card, .tech-category, .stat-card, .content-card"
).forEach(el=>{
  el.classList.add("will-reveal");
  obs.observe(el);
});

// 3D tilt cards
document.querySelectorAll(
  ".card, .feature-card, .team-card, .tech-category, .stat-card"
).forEach(card=>{
  card.addEventListener("mousemove", e=>{
    const r=card.getBoundingClientRect();
    const x=e.clientX - r.left;
    const y=e.clientY - r.top;
    card.style.setProperty("--ry", ((x/r.width)-.5)*18+"deg");
    card.style.setProperty("--rx", ((y/r.height)-.5)*-18+"deg");
  });
  card.addEventListener("mouseleave", ()=>{
    card.style.setProperty("--ry","0deg");
    card.style.setProperty("--rx","0deg");
  });
});
