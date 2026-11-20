(function(){
  var d=document, root=d.documentElement; root.classList.add('js');
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small=matchMedia('(max-width: 640px)').matches;
  var hasIO='IntersectionObserver' in window;

  // ---- text and figures arrive softly, once
  var targets=[].slice.call(d.querySelectorAll('[data-r]'));
  function showAll(){ targets.forEach(function(t){ t.classList.add('in'); }); }
  if(reduce || !hasIO){ showAll(); }
  else{
    var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } }); },
      {threshold:.12, rootMargin:'0px 0px -6% 0px'});
    targets.forEach(function(t){ io.observe(t); });
    addEventListener('beforeprint', showAll);
  }

  // ---- the mark is built in order, once: frame, plan, structure, beam, point, accent
  var STAGE={frame:[0,.38], plan:[.18,.5], build:[.3,.72], beam:[.56,.8], point:[.68,.86], accent:[.74,1]};
  var DUR=small?1300:1900;
  function ease(q){ return 1-Math.pow(1-q,3); }
  function local(st,t,hasFrame){
    var r=STAGE[st]; var a=r[0], b=r[1];
    if(!hasFrame){ a=Math.max(0,a-.25)*1.3; b=Math.min(1,(b-.25)*1.3); if(b<=a) b=a+.2; }
    return ease(Math.min(1,Math.max(0,(t-a)/(b-a))));
  }
  function setRv(svg,t){
    var hasFrame=!!svg.querySelector('[data-st=frame]');
    [].forEach.call(svg.querySelectorAll('[data-st]'),function(el){
      var st=el.getAttribute('data-st'), q=local(st,t,hasFrame);
      if(st==='frame'){ el.setAttribute('stroke-dashoffset',(1.02*(1-q)).toFixed(4)); }
      else if(st==='build'||st==='beam'){
        var b=el.getAttribute('data-box').split(' ').map(Number), m=el.getAttribute('data-m');
        if(m==='up'){ el.setAttribute('y',b[1]+b[3]*(1-q)); el.setAttribute('height',b[3]*q); }
        else { el.setAttribute('width',b[2]*q); }
      }
      else if(st==='plan'){ el.setAttribute('opacity',q.toFixed(3)); }
      else if(st==='point'){
        var c=el.getAttribute('data-c').split(' '), s=(1+.9*(1-q)).toFixed(3);
        el.setAttribute('opacity',q.toFixed(3));
        el.setAttribute('transform','translate('+c[0]+' '+c[1]+') scale('+s+') translate('+(-c[0])+' '+(-c[1])+')');
      }
      else if(st==='accent'){
        el.setAttribute('opacity',q.toFixed(3));
        el.setAttribute('transform','translate(0 '+(-46*(1-q)).toFixed(1)+')');
      }
    });
  }
  function play(svg,delay){
    var t0=null;
    function f(now){ if(t0===null) t0=now+(delay||0); var t=Math.max(0,(now-t0)/DUR); setRv(svg,Math.min(1,t)); if(t<1) requestAnimationFrame(f); }
    requestAnimationFrame(f);
  }
  var rvs=[].slice.call(d.querySelectorAll('[data-rv]'));
  if(!reduce && hasIO){
    rvs.forEach(function(s){ setRv(s,0); });
    var groups=new Map();
    var ro=new IntersectionObserver(function(es){ es.forEach(function(e){
      if(!e.isIntersecting) return; ro.unobserve(e.target);
      var g=e.target.closest('[data-rv-group]'), delay=0;
      if(g){ delay=[].indexOf.call(g.querySelectorAll('[data-rv]'),e.target)*(small?120:220)+300; }
      play(e.target,delay);
    }); },{threshold:.35});
    rvs.forEach(function(s){ ro.observe(s); });
  }

  // ---- opening background: a slight depth shift while leaving the first screen
  var op=d.querySelector('.op');
  if(!reduce && !small && op){
    var tk=false; addEventListener('scroll',function(){ if(tk) return; tk=true; requestAnimationFrame(function(){ tk=false;
      if(scrollY<innerHeight*1.2) op.style.setProperty('--sy',scrollY.toFixed(0)); }); },{passive:true});
  }

  // ---- navigation: current section, dots colour, top bar that steps aside while reading
  var secs=[].slice.call(d.querySelectorAll('[data-nav]'));
  var dots=[].slice.call(d.querySelectorAll('.dots a')), dnav=d.querySelector('.dots');
  var tb=d.querySelector('.tb'), tbc=d.querySelector('.tb-c'), tbm=d.querySelector('.tb-m');
  var darks=[].slice.call(d.querySelectorAll('.op,.end'));
  var last=-1, lastY=scrollY, ticking=false;
  function tick(){
    ticking=false;
    var vh=innerHeight, mid=vh*.4, cur=0;
    for(var i=0;i<secs.length;i++){ if(secs[i].getBoundingClientRect().top<mid) cur=i; }
    if(cur!==last){ last=cur;
      dots.forEach(function(a,i){ a.classList.toggle('cur',i===cur); if(i===cur) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); });
      tbc.textContent=secs[cur].getAttribute('data-nav');
    }
    var y=vh/2; dnav.classList.toggle('dark',darks.some(function(el){ var r=el.getBoundingClientRect(); return r.top<y && r.bottom>y; }));
    var sy=scrollY;
    if(!tb.classList.contains('open')){
      if(sy<vh*.6) tb.classList.remove('show');
      else if(sy<lastY-6) tb.classList.add('show');
      else if(sy>lastY+6) tb.classList.remove('show');
    }
    lastY=sy;
  }
  addEventListener('scroll',function(){ if(!ticking){ ticking=true; requestAnimationFrame(tick); } },{passive:true});
  addEventListener('resize',tick); tick();
  function closeM(){ tb.classList.remove('open'); tbm.setAttribute('aria-expanded','false'); }
  tbm.addEventListener('click',function(e){ e.stopPropagation(); var o=tb.classList.toggle('open'); tbm.setAttribute('aria-expanded',o?'true':'false'); });
  [].forEach.call(d.querySelectorAll('.tb-l a, .tb-b'),function(a){ a.addEventListener('click',function(){ closeM(); tb.classList.remove('show'); }); });
  d.addEventListener('click',function(e){ if(!tb.contains(e.target)) closeM(); });
  addEventListener('keydown',function(e){ if(e.key==='Escape') closeM(); });
})();
