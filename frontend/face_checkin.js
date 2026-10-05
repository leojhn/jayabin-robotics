(function(){
  'use strict';
  let timer=null, handled=false, unknownSince=0;
  const UNKNOWN_CONFIRM_MS=3200;
  const status=document.getElementById('faceStatus');
  function setStatus(t){if(status)status.textContent=t;}

  function beginNew(){
    if(handled)return; handled=true;
    sessionStorage.setItem('is_existing_user', 'false');
    sessionStorage.removeItem('patient');
    setStatus('No matching patient record found. Proceeding as new user.');
    setTimeout(()=>{ location.href='neo_nano_welcome.html'; }, 800);
  }

  function beginExisting(patient){
    if(handled)return; handled=true;
    sessionStorage.setItem('is_existing_user', 'true');
    sessionStorage.setItem('patient', JSON.stringify(patient));
    setStatus('Patient recognized: ' + (patient['PATIENT NAME'] || ''));
    setTimeout(()=>{ location.href='neo_nano_welcome.html'; }, 800);
  }

  async function poll(){
    if(handled)return;
    try{
      const r=await fetch('/api/face/status',{cache:'no-store'}); const d=await r.json();
      if(d.success&&d.ready&&d.recognized&&d.patient){
        unknownSince=0;
        beginExisting(d.patient);
        return;
      }
      if(d.success&&d.ready&&d.present&&!d.recognized){
        if(!unknownSince)unknownSince=Date.now();
        if(Date.now()-unknownSince>=UNKNOWN_CONFIRM_MS || d.new_patient){beginNew();return;}
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
