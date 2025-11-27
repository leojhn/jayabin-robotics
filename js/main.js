// Add your JavaScript code here
window.addEventListener('scroll', function() {
    const header = document.getElementById('global-header');
    if (window.scrollY > 50) { // Add scrolled class after 50px scroll
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Subtle scroll animations for sections
const sections = document.querySelectorAll('section');

const options = {
    root: null, // it is the viewport
    threshold: 0.1, // 10% of the item is visible
    rootMargin: "0px"
};

const observer = new IntersectionObserver(function(entries, observer) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, options);

sections.forEach(section => {
    observer.observe(section);
});
// Mobile Menu Toggle
const menuToggle = document.getElementById('menu-toggle');
const nav = document.querySelector('nav');

menuToggle.addEventListener('click', () => {
    nav.classList.toggle('active');
});


