const steps =
document.querySelectorAll(".step");

const progress =
document.getElementById("progress");

let currentStep = 0;

/* Show Steps */

function showStep(index){

steps.forEach((step)=>{

step.classList.remove("active");

});

steps[index].classList.add("active");

let percent =
(index/(steps.length-1))*100;

progress.style.width =
percent + "%";
}

/* Authentication Logic */

function authenticatePatient(){


/* RANDOM DEMO */

let existingPatient =
Math.random() > 0.5;

/* EXISTING PATIENT */

if(existingPatient){

currentStep = 1;

}

/* NEW PATIENT */

else{

currentStep = 2;

}

showStep(currentStep);
}

/* Next Step */

function nextStep(){

if(currentStep < steps.length-1){

currentStep++;

showStep(currentStep);

}
}

/* Start */

showStep(currentStep);

/* WAYFINDING */

function showRoute(department){

const routeInfo =
document.getElementById("routeInfo");

routeInfo.innerHTML =

"📍 Route to <b>" +
department +
"</b><br><br>" +

"➡ Go straight for 20 meters<br>" +

"⬆ Take elevator to 2nd floor<br>" +

"➡ Turn right near Pharmacy<br>" +

"✅ Destination reached";
}
/* PAYMENT SUCCESS */

function showPaymentSuccess(){

const paymentBox =
document.getElementById(
"paymentSuccess"
);

paymentBox.style.display =
"flex";
}
/* OPEN CARD GATEWAY */

function openCardGateway(){

document.getElementById(
"cardGateway"
).style.display = "flex";

document.getElementById(
"upiGateway"
).style.display = "none";
}

/* OPEN UPI GATEWAY */

function openUPIGateway(){

document.getElementById(
"upiGateway"
).style.display = "flex";

document.getElementById(
"cardGateway"
).style.display = "none";
}