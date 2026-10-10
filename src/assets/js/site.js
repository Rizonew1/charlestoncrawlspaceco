(function(){
  var btn=document.querySelector('.menu-btn'),nav=document.getElementById('nav');
  if(btn&&nav){btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o);btn.textContent=o?'Close':'Menu';});}
  document.querySelectorAll('.has-drop>button.nl').forEach(function(b){
    b.addEventListener('click',function(){
      var li=b.parentNode,o=li.classList.toggle('open');b.setAttribute('aria-expanded',o);
    });
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){document.querySelectorAll('.has-drop.open').forEach(function(l){l.classList.remove('open')});}});

  // phone click tracking (GA4 event: phone_click)
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href^="tel:"]');
    if(!a||typeof window.gtag!=='function')return;
    var spots=[['.site-header','header'],['.callbar','mobile_call_bar'],['.site-footer','footer'],['.endcta','closing_cta'],['.proof','proof_band'],['.side','sidebar'],['.hero','hero'],['.page-head','page_head'],['.callout','inline_callout'],['.gauge','hero']],loc='body';
    for(var i=0;i<spots.length;i++){if(a.closest(spots[i][0])){loc=spots[i][1];break;}}
    window.gtag('event','phone_click',{phone_number:a.getAttribute('href').replace('tel:',''),link_text:(a.textContent||'').trim().slice(0,60),link_location:loc,page_path:location.pathname,transport_type:'beacon'});
  });

  // humidity gauge
  var needle=document.getElementById('needle'),read=document.getElementById('g-read');
  if(needle&&read){
    var from=88,to=48,rot=function(p){return (p/100)*180-90;};
    var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(!reduce){
      needle.style.transition='none';needle.style.transform='rotate('+rot(from)+'deg)';read.textContent=from+'%';
      requestAnimationFrame(function(){requestAnimationFrame(function(){
        needle.style.transition='';needle.style.transform='rotate('+rot(to)+'deg)';
        var t0=null,dur=2400;
        function step(ts){if(!t0)t0=ts;var k=Math.min(1,(ts-t0)/dur);k=1-Math.pow(1-k,3);
          read.textContent=Math.round(from+(to-from)*k)+'%';if(k<1)requestAnimationFrame(step);}
        setTimeout(function(){requestAnimationFrame(step)},350);
      });});
    }
  }

  // cost estimator
  var est=document.getElementById('estimator');
  if(est){
    var sq=est.querySelector('#sqft'),sqv=est.querySelector('#sqval'),cond=est.querySelector('#cond'),
        out=est.querySelector('#est-range'),checks=est.querySelectorAll('input[type=checkbox]');
    var fmt=function(n){return '$'+(Math.round(n/100)*100).toLocaleString('en-US');};
    function calc(){
      var s=+sq.value;sqv.textContent=s.toLocaleString('en-US');
      var o=cond.options[cond.selectedIndex];
      var lo=s*parseFloat(o.dataset.lo),hi=s*parseFloat(o.dataset.hi);
      checks.forEach(function(c){if(c.checked){lo+=+c.dataset.lo;hi+=+c.dataset.hi;}});
      out.textContent=fmt(lo)+' – '+fmt(hi);
    }
    est.addEventListener('input',calc);calc();
  }
})();
