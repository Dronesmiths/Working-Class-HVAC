// Basic interactions scripts
document.addEventListener('DOMContentLoaded', () => {
    console.log('Working Class HVAC site loaded');

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile Menu Toggle
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');
    const icon = mobileBtn ? mobileBtn.querySelector('i') : null;

    if (mobileBtn && navMenu) {
        mobileBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent bubbling
            navMenu.classList.toggle('active');

            // Toggle icon
            if (icon) {
                if (navMenu.classList.contains('active')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });

        // Close menu when clicking a link
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (navMenu.classList.contains('active') && !navMenu.contains(e.target) && !mobileBtn.contains(e.target)) {
                navMenu.classList.remove('active');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }


    // Dynamic Year in Footer
    const yearSpan = document.getElementById('year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Service Popup Logic
    const popupClosedTime = localStorage.getItem('wc_popup_closed');
    const now = new Date().getTime();
    const fiveMinutes = 5 * 60 * 1000;

    if (!popupClosedTime || (now - popupClosedTime > fiveMinutes)) {
        setTimeout(showServicePopup, 15000); // 15 seconds
    }

    function showServicePopup() {
        // Prevent multiple popups
        if (document.querySelector('.service-popup-overlay')) return;

        const popupHTML = `
            <div class="service-popup">
                <div class="popup-close-x" id="popup-close-x">&times;</div>
                <div class="popup-header">
                    <div class="popup-icon">❄️</div>
                    <h2>Don't Lose Your Cool!</h2>
                </div>
                <div class="popup-body">
                    <p>Our technicians are in the neighborhood! Grab a priority slot before they fill up.</p>
                    <a href="tel:6614948075" class="btn popup-btn-call">
                        <i class="fas fa-phone"></i> Call Tech Now
                    </a>
                    <div class="popup-close-link" id="popup-close-link" style="color: #60a5fa;">No thanks, I'm cool</div>
                </div>
            </div>
        `;

        const overlay = document.createElement('div');
        overlay.className = 'service-popup-overlay';
        overlay.innerHTML = popupHTML;
        document.body.appendChild(overlay);

        // Animation in
        setTimeout(() => {
            overlay.classList.add('active');
        }, 10);

        // Close Handlers
        function closePopup() {
            overlay.classList.remove('active');
            localStorage.setItem('wc_popup_closed', new Date().getTime());
            setTimeout(() => {
                overlay.remove();
            }, 400); // Wait for transition
        }

        document.getElementById('popup-close-x').addEventListener('click', closePopup);
        document.getElementById('popup-close-link').addEventListener('click', closePopup);

        // Close on outside click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closePopup();
        });
    }

});
