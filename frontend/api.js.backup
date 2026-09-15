const BASE_URL = "http://127.0.0.1:5000";


// ==========================================
// GET ALL PATIENTS
// ==========================================

async function getPatients() {

    const response = await fetch(
        `${BASE_URL}/api/patients`
    );

    return await response.json();
}


// ==========================================
// GET PATIENT
// ==========================================

async function getPatient(patientId) {

    const response = await fetch(
        `${BASE_URL}/api/patient/${patientId}`
    );

    return await response.json();
}


// ==========================================
// REGISTER PATIENT
// ==========================================

async function registerPatient(patient) {

    const response = await fetch(
        `${BASE_URL}/api/register_patient`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(patient)
        }
    );

    return await response.json();
}


// ==========================================
// UPDATE PATIENT
// ==========================================

async function updatePatient(patientId, patient) {

    const response = await fetch(
        `${BASE_URL}/api/update_patient/${patientId}`,
        {
            method: "PUT",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(patient)
        }
    );

    return await response.json();
}


// =====================================
// AUTHENTICATE PATIENT
// =====================================

async function authenticatePatientBackend(patientId){

    const response = await fetch(
        `${BASE_URL}/api/authenticate`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                patient_id: patientId

            })
        }
    );

    return await response.json();

}


// ==========================================
// GET DEPARTMENTS
// ==========================================

async function getDepartments(){

    const response = await fetch(
        `${BASE_URL}/api/departments`
    );

    return await response.json();

}


// ==========================================
// GET DOCTORS
// ==========================================

async function getDoctors(department){

    const response = await fetch(
        `${BASE_URL}/api/doctors/${encodeURIComponent(department)}`
    );

    return await response.json();

}


// ==========================================
// GET SCHEDULE
// ==========================================

async function getSchedule(doctor){

    const response = await fetch(
        `${BASE_URL}/api/schedule/${encodeURIComponent(doctor)}`
    );

    return await response.json();

}


// ==========================================
// BOOK APPOINTMENT
// ==========================================

async function bookAppointment(data){

    const response = await fetch(
        `${BASE_URL}/api/book_appointment`,
        {
            method: "POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)
        }
    );

    return await response.json();

}


// ==========================================
// GET APPOINTMENT
// ==========================================

async function getAppointment(patientId){

    const response = await fetch(
        `${BASE_URL}/api/appointment/${patientId}`
    );

    return await response.json();

}


// ==========================================
// TODAY APPOINTMENTS
// ==========================================

async function getTodayAppointments(){

    const response = await fetch(
        `${BASE_URL}/api/today_appointments`
    );

    return await response.json();

}


// ==========================================
// UPDATE PAYMENT STATUS
// ==========================================

async function updatePaymentStatus(
    patientId,
    status
){

    const response = await fetch(
        `${BASE_URL}/api/payment_status`,
        {
            method:"PUT",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                patient_id:patientId,

                status:status

            })
        }
    );

    return await response.json();

}


// ==========================================
// CONSULTANT BILL
// ==========================================

async function getConsultantBill(patientId){

    const response = await fetch(
        `${BASE_URL}/api/consultant_bill/${patientId}`
    );

    return await response.json();

}


// ==========================================
// PAYMENT HISTORY
// ==========================================

async function getPaymentHistory(patientId){

    const response = await fetch(
        `${BASE_URL}/api/payment_history/${patientId}`
    );

    return await response.json();

}


// ==========================================
// DEPARTMENT MAP
// ==========================================

async function getDepartmentMap(department){

    const response = await fetch(
        `${BASE_URL}/api/map/${encodeURIComponent(department)}`
    );

    return await response.json();

}


// ==========================================
// SERVICE BILL
// ==========================================

async function getServiceBill(patientId){

    const response = await fetch(
        `${BASE_URL}/api/service_bill/${patientId}`
    );

    return await response.json();

}


// ==========================================
// FAQ
// ==========================================

async function getFAQs(){

    const response = await fetch(
        `${BASE_URL}/api/faqs`
    );

    return await response.json();

}


// ==========================================
// PRINT RECEIPT
// ==========================================

async function printReceipt(receipt){

    try{

        const response = await fetch(
            `${BASE_URL}/api/print_receipt`,
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    html: receipt

                })
            }
        );


        let result;


        try{

            result =
            await response.json();

        }

        catch(error){

            throw new Error(
                "Invalid response from print server."
            );

        }


        if(!response.ok){

            return {

                success:false,

                message:

                    result.message ||

                    `Server error: ${response.status}`

            };

        }


        return result;

    }

    catch(error){

        console.error(
            "Print API error:",
            error
        );

        return {

            success:false,

            message:error.message

        };

    }

}


// ==========================================
// NEO NANO MEDICAL AI
// ==========================================

async function analyzeWithNeoNano(query, limit = 5) {

    const response = await fetch(
        `${BASE_URL}/api/neo-nano/analyze`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query,
                limit
            })
        }
    );

    return await response.json();

}


async function getNeoNanoKnowledgeGraph() {

    const response = await fetch(
        `${BASE_URL}/api/neo-nano/knowledge-graph`
    );

    return await response.json();

}


async function getNeoNanoGenomics(diseaseId) {

    const response = await fetch(
        `${BASE_URL}/api/neo-nano/genomics/${encodeURIComponent(diseaseId)}`
    );

    return await response.json();

}