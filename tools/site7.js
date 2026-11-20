(function(){
  var d=document, root=d.documentElement;
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small=matchMedia('(max-width: 640px)').matches;
  var hasIO='IntersectionObserver' in window;
  if(!reduce) root.classList.add('js');

  // ---- opening: lines are set out, then the title arrives
  var op=d.querySelector('.op');
  if(op && !reduce) requestAnimationFrame(function(){ requestAnimationFrame(function(){ op.classList.add('go'); }); });

  // ---- text and figures arrive softly, once
  var targets=[].slice.call(d.querySelectorAll('[data-r]'));
  function showAll(){ targets.forEach(function(t){ t.classList.add('in'); }); }
  if(reduce || !hasIO){ showAll(); }
  else{
    var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } }); },
      {threshold:.1, rootMargin:'0px 0px -6% 0px'});
    targets.forEach(function(t){ io.observe(t); });
    addEventListener('beforeprint', showAll);
  }

  // ---- the mark is built once, in the order of its idea
  var STAGE={frame:[0,.36], plan:[.16,.48], build:[.28,.7], beam:[.56,.8], point:[.7,.88], accent:[.78,1]};
  var DUR=small?1500:2300;
  function ease(q){ return q<.5 ? 4*q*q*q : 1-Math.pow(-2*q+2,3)/2; }
  function local(st,t,hasFrame){
    var a=STAGE[st][0], b=STAGE[st][1];
    if(!hasFrame){ a=Math.max(0,(a-.26)*1.35); b=Math.min(1,(b-.26)*1.35); }
    return ease(Math.min(1,Math.max(0,(t-a)/(b-a))));
  }
  function setRv(svg,t){
    var hasFrame=!!svg.querySelector('[data-st=frame]');
    [].forEach.call(svg.querySelectorAll('[data-st]'),function(el){
      var st=el.getAttribute('data-st'), q=local(st,t,hasFrame);
      if(st==='frame'){ el.setAttribute('stroke-dashoffset',(1.02*(1-q)).toFixed(4)); }
      else if(el.hasAttribute('data-box')){
        var b=el.getAttribute('data-box').split(' ').map(Number), m=el.getAttribute('data-m');
        if(m==='up'){ el.setAttribute('y',b[1]+b[3]*(1-q)); el.setAttribute('height',b[3]*q); }
        else if(m==='rtl'){ el.setAttribute('x',b[0]+b[2]*(1-q)); el.setAttribute('width',b[2]*q); }
        else { el.setAttribute('width',b[2]*q); }
      }
      else if(st==='point'){
        var c=el.getAttribute('data-c').split(' ');
        el.setAttribute('opacity',Math.min(1,q*1.6).toFixed(3));
        el.setAttribute('transform','translate('+c[0]+' '+c[1]+') scale('+(1+1.2*(1-q)).toFixed(3)+') translate('+(-c[0])+' '+(-c[1])+')');
      }
      else if(st==='accent'){
        el.setAttribute('opacity',Math.min(1,q*1.6).toFixed(3));
        el.setAttribute('transform','translate(0 '+(-54*(1-q)).toFixed(1)+')');
      }
    });
  }
  function play(svg){
    var t0=null;
    function f(now){ if(t0===null) t0=now+250; var t=Math.max(0,(now-t0)/DUR); setRv(svg,Math.min(1,t)); if(t<1) requestAnimationFrame(f); }
    requestAnimationFrame(f);
  }
  var rvs=[].slice.call(d.querySelectorAll('[data-rv]'));
  if(!reduce && hasIO){
    rvs.forEach(function(s){ setRv(s,0); });
    var ro=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ ro.unobserve(e.target); play(e.target); } }); },{threshold:.5});
    rvs.forEach(function(s){ ro.observe(s); });
  }

  // ---- choosing a direction
  var cards=[].slice.call(d.querySelectorAll('[data-pick]')), pick=d.querySelector('.pick');
  var KEY='alraya-pick';
  function store(v){ try{ if(v) localStorage.setItem(KEY,v); else localStorage.removeItem(KEY); }catch(e){} }
  function choose(n){
    var name='';
    cards.forEach(function(c){ var on=c.getAttribute('data-pick')===n; c.classList.toggle('on',on);
      var b=c.querySelector('.cc-b'); b.setAttribute('aria-pressed',on?'true':'false'); b.textContent=on?'✓ اختياري':'أفضّل هذا الاتجاه';
      if(on) name=n+' · '+c.getAttribute('data-name'); });
    if(pick){ pick.hidden=!name; if(name) pick.querySelector('.pick-n').textContent=name; }
    store(name?n:'');
  }
  cards.forEach(function(c){ c.querySelector('.cc-b').addEventListener('click',function(){ choose(c.classList.contains('on')?'':c.getAttribute('data-pick')); }); });
  if(pick){
    pick.querySelector('.pick-x').addEventListener('click',function(){ choose(''); });
    var cb=pick.querySelector('.pick-c');
    cb.addEventListener('click',function(){
      var txt='الاتجاه المفضّل لهوية الراية: '+pick.querySelector('.pick-n').textContent;
      function done(){ cb.textContent='تم النسخ'; setTimeout(function(){ cb.textContent='نسخ الاختيار'; },1800); }
      if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).then(done,function(){}); }
    });
  }
  try{ var saved=localStorage.getItem(KEY); if(saved) choose(saved); }catch(e){}

  // ---- navigation: current section, dots colour, top bar that steps aside while reading
  var secs=[].slice.call(d.querySelectorAll('[data-nav]'));
  var dots=[].slice.call(d.querySelectorAll('.dots a')), dnav=d.querySelector('.dots');
  var tb=d.querySelector('.tb'), tbc=d.querySelector('.tb-c'), tbm=d.querySelector('.tb-m');
  var darks=[].slice.call(d.querySelectorAll('.op,.intro,.close,.end'));
  var ids=dots.map(function(a){ return a.getAttribute('href').slice(1); });
  var last=-1, lastY=scrollY, ticking=false;
  function tick(){
    ticking=false;
    var vh=innerHeight, mid=vh*.4, cur=0;
    for(var i=0;i<secs.length;i++){ if(secs[i].getBoundingClientRect().top<mid) cur=i; }
    if(cur!==last){ last=cur;
      var k=ids.lastIndexOf(secs[cur].id); if(k<0){ for(var j=cur;j>=0&&k<0;j--) k=ids.lastIndexOf(secs[j].id); }
      dots.forEach(function(a,i){ a.classList.toggle('cur',i===k); if(i===k) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); });
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
