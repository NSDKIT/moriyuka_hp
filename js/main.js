/* ==============================================
   Mori Yuka Official Site - Yukos Style JavaScript
   ゆうこす公式サイト完全再現インタラクション
============================================== */

$(document).ready(function() {
    initializeYukosStyle();
});

function initializeYukosStyle() {
    // Initialize all yukos-style features
    initCustomCursor();
    initImageSlider();
    initSmoothScroll();
    initPCMobileToggle();
    initHamburgerMenu();
    initScrollAnimations();
    initHoverEffects();
    initResponsiveAdjustments();
    
    console.log('🌸 Yukos-style site initialized');
}

/* ==============================================
   Custom Cursor - PC Only
============================================== */
function initCustomCursor() {
    if (window.innerWidth < 1024) return;
    
    const cursor = $('.cursor');
    const follower = $('.follower');
    
    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    let followerX = 0;
    let followerY = 0;
    
    // Track mouse movement
    $(document).mousemove(function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    // Animate cursor and follower
    function animateCursor() {
        // Cursor follows mouse directly
        cursorX += (mouseX - cursorX) * 0.1;
        cursorY += (mouseY - cursorY) * 0.1;
        
        // Follower follows with delay
        followerX += (mouseX - followerX) * 0.05;
        followerY += (mouseY - followerY) * 0.05;
        
        cursor.css({
            'left': cursorX + 'px',
            'top': cursorY + 'px'
        });
        
        follower.css({
            'left': followerX + 'px',
            'top': followerY + 'px'
        });
        
        requestAnimationFrame(animateCursor);
    }
    
    animateCursor();
    
    // Hover effects for cursor
    $('a, button').mouseenter(function() {
        cursor.css('transform', 'scale(1.5)');
        follower.css('transform', 'scale(0.8)');
    }).mouseleave(function() {
        cursor.css('transform', 'scale(1)');
        follower.css('transform', 'scale(1)');
    });
}

/* ==============================================
   Image Slider - Simple Fade Effect
============================================== */
function initImageSlider() {
    // PC slider only
    initPCSlider();
}

function initPCSlider() {
    const pcSlides = $('#pc-slider .slide');
    let currentSlide = 0;
    
    if (pcSlides.length <= 1) return;
    
    // Show first slide
    pcSlides.eq(0).addClass('active');
    
    function showNextSlide() {
        pcSlides.eq(currentSlide).removeClass('active');
        currentSlide = (currentSlide + 1) % pcSlides.length;
        pcSlides.eq(currentSlide).addClass('active');
    }
    
    // Auto-advance slides every 4 seconds
    setInterval(showNextSlide, 4000);
}

/* ==============================================
   Smooth Scroll Navigation
============================================== */
function initSmoothScroll() {
    $('header nav a[href^="#"]').click(function(e) {
        e.preventDefault();
        
        const target = $(this.getAttribute('href'));
        if (target.length) {
            const offset = $('header').outerHeight() + 20;
            
            $('html, body').animate({
                scrollTop: target.offset().top - offset
            }, 800, 'swing');
        }
    });
}

/* ==============================================
   PC/Mobile Layout Toggle
============================================== */
function initPCMobileToggle() {
    function toggleLayout() {
        if (window.innerWidth >= 1024) {
            $('.pcbody').show();
            $('.spbox').show(); // Keep spbox visible on PC too
            $('.spbox').css('margin-top', '100vh'); // Position below PC layout
        } else {
            $('.pcbody').hide();
            $('.spbox').show();
            $('.spbox').css('margin-top', '0'); // Reset margin for mobile
        }
    }
    
    toggleLayout();
    
    $(window).resize(function() {
        toggleLayout();
    });
}

/* ==============================================
   Hamburger Menu Functionality
============================================== */
function initHamburgerMenu() {
    const hamburgerToggle = $('#hamburger-toggle');
    const menuOverlay = $('#menu-overlay');
    const menuLinks = $('.menu-link');
    
    // Toggle menu
    hamburgerToggle.click(function() {
        $(this).toggleClass('active');
        menuOverlay.toggleClass('active');
        
        // Prevent body scroll when menu is open
        if (menuOverlay.hasClass('active')) {
            $('body').addClass('menu-open');
        } else {
            $('body').removeClass('menu-open');
        }
    });
    
    // Close menu when clicking on a link
    menuLinks.click(function() {
        hamburgerToggle.removeClass('active');
        menuOverlay.removeClass('active');
        $('body').removeClass('menu-open');
    });
    
    // Close menu when clicking overlay background
    menuOverlay.click(function(e) {
        if (e.target === this) {
            hamburgerToggle.removeClass('active');
            menuOverlay.removeClass('active');
            $('body').removeClass('menu-open');
        }
    });
    
    // Close menu with Escape key
    $(document).keydown(function(e) {
        if (e.key === 'Escape' && menuOverlay.hasClass('active')) {
            hamburgerToggle.removeClass('active');
            menuOverlay.removeClass('active');
            $('body').removeClass('menu-open');
        }
    });
}

/* ==============================================
   Scroll Animations with GSAP
============================================== */
function initScrollAnimations() {
    // Fade in animations on scroll (using WOW.js classes)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = $(entry.target);
                
                // Add wow animation class
                element.addClass('animated fadeIn');
                
                // Unobserve after animation
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with wow classes
    $('.wow').each(function() {
        observer.observe(this);
    });
}

/* ==============================================
   Hover Effects
============================================== */
function initHoverEffects() {
    // SNS list hover effects
    $('.snslist li').hover(
        function() {
            $(this).css('transform', 'translateY(-5px)');
        },
        function() {
            $(this).css('transform', 'translateY(0)');
        }
    );
    
    // Works list hover effects
    $('.worklist li').hover(
        function() {
            $(this).css('transform', 'translateY(-5px)');
        },
        function() {
            $(this).css('transform', 'translateY(0)');
        }
    );
    
    // News list hover effects
    $('.newslist li a').hover(
        function() {
            $(this).find('h3').css('color', '#666');
        },
        function() {
            $(this).find('h3').css('color', '#333');
        }
    );
}

/* ==============================================
   Responsive Adjustments
============================================== */
function initResponsiveAdjustments() {
    function adjustForScreenSize() {
        const windowWidth = $(window).width();
        
        // Adjust navigation for small screens
        if (windowWidth < 480) {
            $('header nav ul li a').css({
                'font-size': '8px',
                'padding': '3px 5px'
            });
        } else if (windowWidth < 768) {
            $('header nav ul li a').css({
                'font-size': '10px',
                'padding': '5px 8px'
            });
        } else {
            $('header nav ul li a').css({
                'font-size': '12px',
                'padding': '8px 12px'
            });
        }
        
        // Adjust slider for mobile
        if (windowWidth < 600) {
            $('#slider').css('max-width', '100%');
        } else {
            $('#slider').css('max-width', '600px');
        }
    }
    
    adjustForScreenSize();
    
    $(window).resize(function() {
        adjustForScreenSize();
    });
}

/* ==============================================
   GSAP Animations (if GSAP is loaded)
============================================== */
if (typeof TweenMax !== 'undefined') {
    // PC layout entrance animation
    function animatePCLayout() {
        if (window.innerWidth >= 1024) {
            TweenMax.from('.pcbox h1', 1.5, {
                opacity: 0,
                scale: 0.8,
                ease: Power2.easeOut,
                delay: 0.5
            });
            
            TweenMax.from('.imgL img', 2, {
                x: -200,
                opacity: 0,
                ease: Power2.easeOut,
                delay: 0.8
            });
            
            TweenMax.from('.imgR img', 2, {
                x: 200,
                opacity: 0,
                ease: Power2.easeOut,
                delay: 1
            });
        }
    }
    
    // Mobile elements animation
    function animateMobileElements() {
        if (window.innerWidth < 1024) {
            TweenMax.from('.topkv', 1.2, {
                opacity: 0,
                y: 30,
                ease: Power2.easeOut,
                delay: 0.3
            });
            
            TweenMax.from('header nav ul li', 0.8, {
                opacity: 0,
                y: -20,
                stagger: 0.1,
                ease: Power2.easeOut,
                delay: 0.5
            });
        }
    }
    
    $(window).on('load', function() {
        animatePCLayout();
        animateMobileElements();
    });
}

/* ==============================================
   Utility Functions
============================================== */

// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/* ==============================================
   Performance Optimizations
============================================== */

// Optimize scroll events
const optimizedScroll = throttle(function() {
    // Add scroll-based effects here if needed
}, 16); // ~60fps

$(window).on('scroll', optimizedScroll);

// Optimize resize events
const optimizedResize = debounce(function() {
    initResponsiveAdjustments();
    initPCMobileToggle();
}, 250);

$(window).on('resize', optimizedResize);

/* ==============================================
   Touch Device Optimizations
============================================== */
function initTouchOptimizations() {
    // Check if device supports touch
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        // Disable hover effects on touch devices
        $('body').addClass('touch-device');
        
        // Add touch-friendly interactions
        $('.snslist li, .worklist li').on('touchstart', function() {
            $(this).addClass('touch-active');
        }).on('touchend', function() {
            $(this).removeClass('touch-active');
        });
    }
}

// Initialize touch optimizations
initTouchOptimizations();

/* ==============================================
   Error Handling
============================================== */
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
});

// Performance monitoring
$(window).on('load', function() {
    if (window.performance && window.performance.timing) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`🚀 Page loaded in ${loadTime}ms`);
    }
});

/* ==============================================
   Accessibility Enhancements
============================================== */
function initAccessibility() {
    // Keyboard navigation support
    $('header nav ul li a').on('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            $(this).trigger('click');
        }
    });
    
    // Skip to main content link
    $('body').prepend('<a href="#profile" class="skip-link">メインコンテンツにスキップ</a>');
    
    // Focus management
    $('.skip-link').on('focus', function() {
        $(this).css({
            'position': 'absolute',
            'top': '10px',
            'left': '10px',
            'background': '#000',
            'color': '#fff',
            'padding': '8px',
            'text-decoration': 'none',
            'border-radius': '4px',
            'z-index': '10000'
        });
    }).on('blur', function() {
        $(this).css({
            'position': 'absolute',
            'left': '-9999px'
        });
    });
}

// Initialize accessibility features
initAccessibility();