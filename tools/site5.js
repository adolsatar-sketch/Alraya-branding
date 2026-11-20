(function(){
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wipes=[].slice.call(document.querySelectorAll('[data-wipe]'));
  function setWipe(r,q){
    var a=r.getAttribute('data-wipe').split(' '), b=r.getAttribute('data-box').split(' ').map(Number);
    var x=b[0],y=b[1],w=b[2],h=b[3];
    if(a[2]==='up'){ r.setAttribute('x',x); r.setAttribute('width',w); r.setAttribute('y',y+h*(1-q)); r.setAttribute('height',h*q); }
    else if(a[2]==='ltr'){ r.setAttribute('x',x); r.setAttribute('width',w*q); r.setAttribute('y',y); r.setAttribute('height',h); }
    else { r.setAttribute('x',x+w*(1-q)); r.setAttribute('width',w*q); r.setAttribute('y',y); r.setAttribute('height',h); }
  }
  function upd(){
    wipes.forEach(function(r){
      var a=r.getAttribute('data-wipe').split(' ').map(Number);
      var sc=r.closest('[data-scene]'); var t=reduce?1:parseFloat(getComputedStyle(sc).getPropertyValue('--t'))||0;
      setWipe(r, Math.min(1,Math.max(0,(t-a[0])/(a[1]-a[0]))));
    });
  }
  var tk=false; addEventListener('scroll',function(){ if(!tk){tk=true; requestAnimationFrame(function(){tk=false; upd();});} },{passive:true});
  addEventListener('resize',upd); setTimeout(upd,50); upd();
  // the mobile menu steps aside while reading down, returns on the way up
  var bar=document.querySelector('.mbar'), lastY=scrollY;
  addEventListener('scroll',function(){ var y=scrollY; if(bar.classList.contains('is-open')) return;
    bar.classList.toggle('away', y>lastY+4 && y>200); if(y<lastY-4) bar.classList.remove('away'); lastY=y; },{passive:true});
})();
