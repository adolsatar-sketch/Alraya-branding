(function(){
  var d=document, root=d.documentElement; root.classList.add('js');
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  // opening sequence
  var open=d.querySelector('.open');
  requestAnimationFrame(function(){ open.classList.add('go'); });

  // reveal on arrival (no scroll blocking; everything rests in its final state)
  var targets=[].slice.call(d.querySelectorAll('[data-r]'));
  function showAll(){targets.forEach(function(t){t.classList.add('in')})}
  if(reduce || !('IntersectionObserver' in window)){ showAll(); }
  else{
    var io=new IntersectionObserver(function(es){es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} })},
      {threshold:0.12, rootMargin:'0px 0px -6% 0px'});
    targets.forEach(function(t){io.observe(t)});
    addEventListener('beforeprint', showAll);
  }

  // scroll-linked scenes: each pinned scene gets --p from 0 to 1 while it is pinned
  var scenes=[].slice.call(d.querySelectorAll('[data-scene]'));
  var active=new Set();
  if(reduce){ scenes.forEach(function(s){ s.style.setProperty('--t','1'); [].forEach.call(s.querySelectorAll('[data-pour]'),function(r){ r.setAttribute('transform',r.getAttribute('data-base')); }); }); }
  else if('IntersectionObserver' in window){
    var so=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting) active.add(e.target); else active.delete(e.target); }); tick(); },{rootMargin:'20% 0px 20% 0px'});
    scenes.forEach(function(s){ so.observe(s); });
  } else { scenes.forEach(function(s){ s.style.setProperty('--t','1'); [].forEach.call(s.querySelectorAll('[data-pour]'),function(r){ r.setAttribute('transform',r.getAttribute('data-base')); }); }); }

  // progress, current section, nav colour
  var secs=[].slice.call(d.querySelectorAll('[data-nav]'));
  var dots=[].slice.call(d.querySelectorAll('.nav a')), mlinks=[].slice.call(d.querySelectorAll('.mbar-l a'));
  var nav=d.querySelector('.nav'), mbar=d.querySelector('.mbar'), mbtn=d.querySelector('.mbar-b'), mcur=d.querySelector('.mbar-c');
  var darks=[d.querySelector('.open'), d.getElementById('rec'), d.getElementById('end')];
  var last=-1, ticking=false;
  function tick(){
    ticking=false;
    var vh=innerHeight;
    active.forEach(function(s){
      var r=s.getBoundingClientRect(), span=r.height-vh;
      var p=span>0 ? Math.min(1,Math.max(0,-r.top/span)) : 1;
      s.style.setProperty('--t', p.toFixed(4));
      [].forEach.call(s.querySelectorAll('[data-pour]'),function(r){
        var a=r.getAttribute('data-pour').split(' ').map(Number), q=Math.min(1,Math.max(0,(p-a[0])/(a[1]-a[0])));
        r.setAttribute('transform',r.getAttribute('data-base')+' translate(0 '+((1-q)*a[2]).toFixed(1)+')');
      });
    });
    var h=root.scrollHeight-vh, pg=h>0?Math.min(1,scrollY/h):0;
    root.style.setProperty('--pg', pg.toFixed(4));
    var cur=0, mid=vh*0.4;
    for(var i=0;i<secs.length;i++){ if(secs[i].getBoundingClientRect().top<mid) cur=i; }
    if(cur!==last){
      last=cur;
      dots.forEach(function(a,i){ a.classList.toggle('cur',i===cur); if(i===cur) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); });
      mlinks.forEach(function(a,i){ a.classList.toggle('cur',i===cur); });
      mcur.textContent=secs[cur].getAttribute('data-nav');
    }
    var y=vh/2, dark=darks.some(function(el){ if(!el) return false; var r=el.getBoundingClientRect(); return r.top<y && r.bottom>y; });
    nav.classList.toggle('dark',dark);
  }
  addEventListener('scroll',function(){ if(!ticking){ ticking=true; requestAnimationFrame(tick); } },{passive:true});
  addEventListener('resize',tick); tick();

  // mobile menu
  function closeM(){ mbar.classList.remove('is-open'); mbtn.setAttribute('aria-expanded','false'); }
  mbtn.addEventListener('click',function(e){ e.stopPropagation(); var o=mbar.classList.toggle('is-open'); mbtn.setAttribute('aria-expanded',o?'true':'false'); });
  mlinks.forEach(function(a){ a.addEventListener('click',closeM); });
  d.addEventListener('click',function(e){ if(!mbar.contains(e.target)) closeM(); });
  addEventListener('keydown',function(e){ if(e.key==='Escape') closeM(); });

  // nav links land on the start of the section (pinned scenes start at their top)
  [].forEach.call(d.querySelectorAll('.nav a, .mbar-l a, .lu-c, .op-cue'),function(a){
    a.addEventListener('click',function(e){
      var id=a.getAttribute('href'); if(!id || id.charAt(0)!=='#') return;
      var el=d.querySelector(id); if(!el) return;
      e.preventDefault();
      var top=el.getBoundingClientRect().top+scrollY;
      scrollTo({top:top, behavior: reduce?'auto':'smooth'});
      history.replaceState(null,'',id);
    });
  });

  // applications: one switch changes the logo in every application
  var apps=d.getElementById('apps');
  [].forEach.call(d.querySelectorAll('.chip'),function(c){
    c.addEventListener('click',function(){
      var k=c.getAttribute('data-k');
      [].forEach.call(d.querySelectorAll('.chip'),function(o){ o.classList.toggle('on',o===c); o.setAttribute('aria-pressed',o===c?'true':'false'); });
      apps.classList.add('swap');
      setTimeout(function(){
        [].forEach.call(apps.querySelectorAll('use.sw'),function(u){ u.setAttribute('href','#L-'+k+'-'+u.getAttribute('data-kind')+'-'+u.getAttribute('data-al')); });
        apps.classList.remove('swap');
      }, reduce?0:230);
    });
  });
})();
