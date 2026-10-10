(function(){
  'use strict';
  let timer=null, handled=false, unknownSince=0;
  const UNKNOWN_CONFIRM_MS=3200;
  const status=document.getElementById('faceStatus');
  function setStatus(t){if(status)status.textContent=t;}
  async function beginNew(){
    if(handled)return; handled=true;
    setStatus('New user detected. Redirecting to Neo Nano Medical Intelligence...');
    sessionStorage.setItem('is_new_user', 'true');
    sessionStorage.removeItem('patient');
    setTimeout(() => { location.href = 'neo_nano_symptoms.html'; }, 800);
  }
  async function poll(){
    if(handled)return;
    try{
      const r=await fetch('/api/face/status',{cache:'no-store'}); const d=await r.json();
      if(d.success&&d.ready&&d.recognized&&d.patient){
        handled=true; unknownSince=0;
        sessionStorage.setItem('is_new_user', 'false');
        sessionStorage.setItem('patient', JSON.stringify(d.patient));
        setStatus('Existing patient recognized: ' + (d.patient['PATIENT NAME'] || ''));
        setTimeout(() => { location.href = 'neo_nano_symptoms.html'; }, 800);
        return;
      }
      if(d.success&&d.ready&&d.present&&!d.recognized){
        if(!unknownSince)unknownSince=Date.now();
        if(Date.now()-unknownSince>=UNKNOWN_CONFIRM_MS || d.new_patient){await beginNew();return;}
        setStatus('Checking your patient record…');
      }else if(d.success&&d.ready&&!d.present){unknownSince=0;setStatus('Checking your patient record…');}
      else if(d.ready===false&&d.message){setStatus('Hospital camera is starting…');}
      const choices=document.getElementById('manualChoices');
      if(choices&&d.ready===false&&d.message&&/could not|unavailable|not installed|opencv|face recognition/i.test(d.message))choices.style.display='block';
    }catch(e){setStatus('Connecting to the hospital camera…');}
    timer=setTimeout(poll,350);
  }
  document.addEventListener('DOMContentLoaded',poll);
})();
