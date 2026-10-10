// ======================================
// Global Language Data
// ======================================

let languageData = {};

// ======================================
// Load Selected Language
// ======================================

async function loadLanguage(){

    const language =
    sessionStorage.getItem("language") || "en";

    let langPath = "";

    // Detect whether page is inside /pages/
    if(window.location.pathname.includes("/pages/")){

        langPath = "../lang/";

    }

    else{

        langPath = "lang/";

    }

    try{

        const response =
        await fetch(

            langPath + language + ".json"

        );

        if(!response.ok){

            throw new Error(
                "Language file not found."
            );

        }

        languageData =
        await response.json();

        translatePage();

    }

    catch(error){

        console.error(error);

    }

}

// ======================================
// Translate HTML Elements
// ======================================

function translatePage(){

    document.querySelectorAll(

        "[data-lang]"

    ).forEach(function(element){

        const key =
        element.getAttribute(
            "data-lang"
        );

        if(languageData[key]){

            element.innerHTML =
            languageData[key];

        }

    });

}

// ======================================
// Translate JavaScript Text
// ======================================

function t(key){

    if(languageData[key]){

        return languageData[key];

    }

    return key;

}

// ======================================
// Change Language
// ======================================

function changeLanguage(language){

    sessionStorage.setItem(

        "language",

        language

    );

    loadLanguage();

}

// ======================================
// Auto Load
// ======================================

document.addEventListener(

    "DOMContentLoaded",

    loadLanguage

);