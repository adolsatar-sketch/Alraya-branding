(function(){
  var d=document, root=d.documentElement; root.classList.add('js');
  var targets=[].slice.call(d.querySelectorAll('[data-r]'));
  function showAll(){targets.forEach(function(t){t.classList.add('in')})}
  if(!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches){ showAll(); }
  else{
    var io=new IntersectionObserver(function(es){es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} })},
      {threshold:0.12, rootMargin:'0px 0px -6% 0px'});
    targets.forEach(function(t){io.observe(t)});
    addEventListener('beforeprint', showAll);
    // anything already above the fold on load
    requestAnimationFrame(function(){targets.forEach(function(t){var r=t.getBoundingClientRect(); if(r.top<innerHeight && r.bottom>0) t.classList.add('in');});});
  }
  // replay a logo's motion
  [].forEach.call(d.querySelectorAll('.stage'),function(st){
    st.addEventListener('click',function(){ st.classList.remove('in'); void st.getBoundingClientRect(); st.classList.add('in'); });
  });

  // progress + current section (desktop dots and mobile menu share the same links)
  var bar=d.querySelector('.prog i'), secs=[].slice.call(d.querySelectorAll('[data-nav]'));
  var nav=d.querySelector('.nav'), dots=[].slice.call(d.querySelectorAll('.nav a')), mlinks=[].slice.call(d.querySelectorAll('.mnav-l a'));
  var mnav=d.querySelector('.mnav'), mbtn=d.querySelector('.mnav-b'), mcur=d.querySelector('.mnav-c');
  var rec=d.getElementById('rec'), last=-1, ticking=false;
  function onScroll(){
    ticking=false;
    var h=root.scrollHeight-innerHeight, p=h>0?scrollY/h:0;
    bar.style.transform='scaleX('+Math.min(1,p)+')';
    var cur=0, mid=innerHeight*0.38;
    secs.forEach(function(s,i){ if(s.getBoundingClientRect().top<mid) cur=i; });
    if(h-scrollY<4) cur=secs.length-1;
    if(cur!==last){
      last=cur;
      dots.forEach(function(a,i){ a.classList.toggle('cur', i===cur); if(i===cur) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); });
      mlinks.forEach(function(a,i){ a.classList.toggle('cur', i===cur); });
      mcur.textContent=secs[cur].getAttribute('data-nav');
    }
    var r=rec.getBoundingClientRect(), y=innerHeight/2;
    nav.classList.toggle('dark', r.top<y && r.bottom>y);
  }
  addEventListener('scroll',function(){ if(!ticking){ticking=true; requestAnimationFrame(onScroll);} },{passive:true});
  addEventListener('resize',onScroll); onScroll();
  mbtn.addEventListener('click',function(){ var o=mnav.classList.toggle('open'); mbtn.setAttribute('aria-expanded',o?'true':'false'); });
  mlinks.forEach(function(a){ a.addEventListener('click',function(){ mnav.classList.remove('open'); mbtn.setAttribute('aria-expanded','false'); }); });
  d.addEventListener('click',function(e){ if(!mnav.contains(e.target)){ mnav.classList.remove('open'); mbtn.setAttribute('aria-expanded','false'); } });

  // applications: one switch changes every logo in the section to the same direction
  var apps=d.getElementById('apps');
  [].forEach.call(d.querySelectorAll('.chip'),function(c){
    c.addEventListener('click',function(){
      var k=c.getAttribute('data-k');
      [].forEach.call(d.querySelectorAll('.chip'),function(o){o.classList.toggle('on',o===c);o.setAttribute('aria-pressed',o===c?'true':'false')});
      apps.classList.add('swap');
      setTimeout(function(){
        [].forEach.call(apps.querySelectorAll('use.sw'),function(u){
          u.setAttribute('href','#L-'+k+'-'+u.getAttribute('data-kind')+'-'+u.getAttribute('data-al'));
        });
        apps.classList.remove('swap');
      },200);
    });
  });
})();
