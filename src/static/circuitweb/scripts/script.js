// Interactive functionality for the Hume website

// API Configuration
const API_CONFIG = {
    // Use the working API at vdp-peach.vercel.app
    baseUrl: 'https://vdp-peach.vercel.app/api',
    
    // Your API token
    token: '3a9a704ebb4540ee1f948caa7fc801b33db26de4631d3bb2b5073ce2b6cb7cea',
    
    // Common headers for all API requests
    getHeaders: function(isFormData = false) {
        const headers = {
            'Authorization': `Bearer ${this.token}`
        };
        
        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        
        return headers;
    }
};

async function makeAPIRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.baseUrl}${endpoint}`;
    const isFormData = options.body instanceof FormData;
    
    const requestOptions = {
        ...options,
        headers: {
            ...API_CONFIG.getHeaders(isFormData),
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, requestOptions);
        
        if (!response.ok) {
            const errorText = await response.text();
            
            if (response.status === 401) {
                throw new Error('Authentication failed');
            } else if (response.status === 403) {
                throw new Error('Access denied');
            } else {
                throw new Error(`${response.status}: ${errorText}`);
            }
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

async function analyzeTextDirect(text) {
    const response = await fetch(`${API_CONFIG.baseUrl}/analyze-text`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_CONFIG.token}`
        },
        body: JSON.stringify({ text })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Analysis failed');
    }
    
    return await response.json();
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize all interactive elements
        initializeNavigation();
        initializeCards();
        // Persona carousel removed
        addScrollEffects();
        initializeCanvas();
        // Video section replaced with action cards
        initializeCTAButtons();
        initializeDemo();
        initializeTimelineNavigation();
        initializeAboutVideo();
        // Initialize voice demo on all pages
        initializeVoiceDemo();
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});

// Navigation functionality
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item.dropdown');
    
    navItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            const arrow = this.querySelector('.dropdown-arrow');
            if (arrow) {
                arrow.style.transform = 'rotate(180deg)';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            const arrow = this.querySelector('.dropdown-arrow');
            if (arrow) {
                arrow.style.transform = 'rotate(0deg)';
            }
        });
    });

    // Button interactions
    const contactBtn = document.querySelector('.contact-btn');

    if (contactBtn) {
        contactBtn.addEventListener('click', function() {
            // Simulate contact sales action
            showNotification('Contact sales clicked! This would open a contact form.');
        });
    }
}

// Card interactions
function initializeCards() {
    const actionCards = document.querySelectorAll('.action-card');
    const personaCards = document.querySelectorAll('.persona-card');

    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('.card-title').textContent;
            if (title.includes('Watch')) {
                // Show AI warning for video
                showAIWarning();
            } else if (title.includes('Demo')) {
                // Navigate to demo page (handled by onclick in HTML)
                showNotification('Taking you to our interactive demo page!');
            }
        });

        // Add hover sound effect simulation
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.01)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    personaCards.forEach(card => {
        card.addEventListener('click', function() {
            const persona = this.querySelector('.persona-name').textContent;
            showNotification(`${persona} persona selected! This would configure the AI with this personality.`);
        });
    });
}

// Persona carousel functionality
function initializePersonaCarousel() {
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');
    const personaGrid = document.querySelector('.persona-grid');
    
    let currentSet = 0;
    const personaSets = [
        ['Podcast Host', 'Spanish Teacher', 'Outgoing Friend', 'Fastidious Robo-Butler'],
        ['Meditation Guide', 'Sports Commentator', 'Cooking Instructor', 'Storyteller'],
        ['News Anchor', 'Therapist', 'Game Show Host', 'Librarian']
    ];

    function updatePersonaCards(setIndex) {
        const cards = personaGrid.querySelectorAll('.persona-card');
        const currentPersonas = personaSets[setIndex];
        
        cards.forEach((card, index) => {
            if (currentPersonas[index]) {
                card.querySelector('.persona-name').textContent = currentPersonas[index];
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.opacity = '1';
                }, index * 100);
            }
        });
    }

    if (leftArrow) {
        leftArrow.addEventListener('click', function() {
            currentSet = (currentSet - 1 + personaSets.length) % personaSets.length;
            updatePersonaCards(currentSet);
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    }

    if (rightArrow) {
        rightArrow.addEventListener('click', function() {
            currentSet = (currentSet + 1) % personaSets.length;
            updatePersonaCards(currentSet);
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    }

    // Auto-rotate personas every 8 seconds
    setInterval(() => {
        currentSet = (currentSet + 1) % personaSets.length;
        updatePersonaCards(currentSet);
    }, 8000);
}

// Scroll effects
function addScrollEffects() {
    const hero = document.querySelector('.hero');
    const actionCards = document.querySelectorAll('.action-card');
    const personaCards = document.querySelectorAll('.persona-card');

    // Parallax effect for hero
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        if (hero) {
            hero.style.transform = `translateY(${rate}px)`;
        }
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe cards for scroll animations
    [...actionCards, ...personaCards].forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Utility function for beautiful notifications
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
        backdrop-filter: blur(20px);
        padding: 20px 28px;
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        z-index: 1000;
        font-size: 14px;
        color: #333;
        max-width: 350px;
        font-family: 'Sohne', sans-serif;
        font-weight: 500;
        line-height: 1.4;
        transform: translateX(100%);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);

    // Animate in with bounce
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
            document.body.removeChild(notification);
            }
        }, 400);
    }, 5000);
}

// Canvas-based gradient rendering (like Hume's Three.js approach)
function initializeCanvas() {
    const canvas = document.getElementById('gradientCanvas');
    if (!canvas) {
        console.log('No gradient canvas found, skipping canvas initialization');
        return;
    }
    
    // Skip canvas initialization on demo page (uses galaxy animation instead)
    if (window.location.pathname.includes('demo.html')) {
        console.log('Demo page detected, skipping gradient canvas initialization');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    let animationId;
    
    // Set canvas size to match viewport
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        renderGradient();
    }
    
    // Render the gradient with precise ring alignment
    function renderGradient() {
        const width = canvas.width;
        const height = canvas.height;
        
        // Get current colors
        const innerStart = document.getElementById('inner-start-color')?.value || '#C49BFF';
        const innerEnd = document.getElementById('inner-end-color')?.value || '#805AD5';
        const middleStart = document.getElementById('middle-start-color')?.value || '#D4B5FF';
        const middleEnd = document.getElementById('middle-end-color')?.value || '#9F7AEA';
        const outerStart = document.getElementById('outer-start-color')?.value || '#E8D5FF';
        const outerEnd = document.getElementById('outer-end-color')?.value || '#B794F6';
        
        // Get boundaries (convert to pixel values)
        const ring1Boundary = (document.getElementById('ring1-boundary')?.value || 25) / 100;
        const ring2Boundary = (document.getElementById('ring2-boundary')?.value || 30) / 100;
        
        // Use EXACT ring dimensions - no percentage calculations
        const centerX = width / 2;
        const centerY = 500; // Same as ring position
        const maxRadius = Math.max(width, height);
        
        // EXACT ring radii from CSS (not percentage-based)
        const ring1Radius = 1299 / 2; // 649.5px - EXACT ring 1 radius
        const ring2Radius = 1496 / 2; // 748px - EXACT ring 2 radius
        
        // Create radial gradients
        ctx.clearRect(0, 0, width, height);
        
        // Outer gradient (background)
        const outerGradient = ctx.createRadialGradient(centerX, centerY, ring2Radius, centerX, centerY, maxRadius);
        outerGradient.addColorStop(0, outerStart);
        outerGradient.addColorStop(1, outerEnd);
        ctx.fillStyle = outerGradient;
        ctx.fillRect(0, 0, width, height);
        
        // Middle gradient (between rings)
        const middleGradient = ctx.createRadialGradient(centerX, centerY, ring1Radius, centerX, centerY, ring2Radius);
        middleGradient.addColorStop(0, middleStart);
        middleGradient.addColorStop(1, middleEnd);
        ctx.fillStyle = middleGradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, ring2Radius, 0, 2 * Math.PI);
        ctx.fill();
        
        // Inner gradient (center)
        const innerGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, ring1Radius);
        innerGradient.addColorStop(0, innerStart);
        innerGradient.addColorStop(1, innerEnd);
        ctx.fillStyle = innerGradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, ring1Radius, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    // Render gradient with pulsed dimensions - now with 3 gradient circles
    function renderGradientWithPulse(ring1PulsedRadius, ring2PulsedRadius, ring3PulsedRadius, centerX, centerY) {
        const width = canvas.width;
        const height = canvas.height;
        const maxRadius = Math.max(width, height) * 1.5; // Ensure full coverage
        
        // Dynamic gradient configuration from color picker or defaults
        const colors = window.gradientColors || {
            center: '#eff5f0',
            ring1: '#c8eacd', 
            ring2: '#9ce2a7',
            outer: '#81e491'
        };
        
        // Debug: Log what colors we're actually using (only once per second to avoid spam)
        if (window.gradientColors && Math.floor(Date.now() / 1000) % 5 === 0) {
            console.log('DEBUG: Using custom colors:', colors);
        }
        
        const innerStart = colors.center;
        const innerEnd = colors.ring1;
        const middleStart = colors.ring1;
        const middleEnd = colors.ring2;
        const outerStart = colors.ring2;
        const outerEnd = colors.outer;
        const extremeStart = colors.outer;
        const extremeEnd = colors.outer;
        
        // Ring positions calculated for alignment
        
        // Create radial gradients with EXACT PULSED radii matching rings
        ctx.clearRect(0, 0, width, height);
        
        // Create a single composite gradient with exact ring boundaries
        const compositeGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
        
        // Calculate stops based on actual ring radii
        const ring1Stop = ring1PulsedRadius / maxRadius;
        const ring2Stop = ring2PulsedRadius / maxRadius;
        const ring3Stop = ring3PulsedRadius / maxRadius;
        
        // Inner space (0 to ring1)
        compositeGradient.addColorStop(0, innerStart);
        compositeGradient.addColorStop(ring1Stop * 0.99, innerEnd);
        
        // Middle space (ring1 to ring2) 
        compositeGradient.addColorStop(ring1Stop, middleStart);
        compositeGradient.addColorStop(ring2Stop * 0.99, middleEnd);
        
        // Outer space (ring2 to ring3)
        compositeGradient.addColorStop(ring2Stop, outerStart);
        compositeGradient.addColorStop(ring3Stop * 0.99, outerEnd);
        
        // Extreme outer space (ring3 to edge)
        compositeGradient.addColorStop(ring3Stop, extremeStart);
        compositeGradient.addColorStop(1, extremeEnd);
        
        ctx.fillStyle = compositeGradient;
        ctx.fillRect(0, 0, width, height);
        
        // Draw gradient circle borders (replacing the CSS rings)
        const circleColor = window.currentCircleColor || '#ffffff';
        ctx.strokeStyle = hexToRgba(circleColor, 0.4);
        ctx.lineWidth = 3;
        
        // Ring 1 border
        ctx.beginPath();
        ctx.arc(centerX, centerY, ring1PulsedRadius, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Ring 2 border
        ctx.beginPath();
        ctx.arc(centerX, centerY, ring2PulsedRadius, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Ring 3 border
        ctx.beginPath();
        ctx.arc(centerX, centerY, ring3PulsedRadius, 0, 2 * Math.PI);
        ctx.stroke();
    }
    
    // Store render function globally for updates
    window.renderCanvasGradient = renderGradient;
    
    // Initialize
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Add pulsing animation - EXACT same as rings with synchronized start
    let startTime = Date.now();
    function animateCanvas() {
        const elapsed = (Date.now() - startTime) * 0.001; // Synchronized timing from start
        const pulseScale = 1 + Math.sin(elapsed * 2 * Math.PI / 10) * 0.03; // EXACT same 10s cycle, 3% pulse as rings
        
        // Calculate pulsed radii to match ring dimensions exactly
        const centerX = canvas.width / 2;
        const centerY = 500; // Same as ring position
        
        // EXACT ring dimensions from CSS - now with third ring and 1/3 bigger
        const ring1BaseRadius = (1299 / 2) * 0.8 * 1.333; // Original * 0.8 * 1.333 = 1/3 bigger than original
        const ring2BaseRadius = (1496 / 2) * 0.8 * 1.333; // Original * 0.8 * 1.333 = 1/3 bigger than original
        // Calculate third ring with same spacing pattern
        const spacing = ring2BaseRadius - ring1BaseRadius;
        const ring3BaseRadius = ring2BaseRadius + spacing;
        
        // Apply EXACT same pulse scale as rings (restored pulse effect)
        const ring1PulsedRadius = ring1BaseRadius * pulseScale;
        const ring2PulsedRadius = ring2BaseRadius * pulseScale;
        const ring3PulsedRadius = ring3BaseRadius * pulseScale;
        
        // Render with pulsed dimensions - restored pulse
        renderGradientWithPulse(ring1PulsedRadius, ring2PulsedRadius, ring3PulsedRadius, centerX, centerY);
        
        animationId = requestAnimationFrame(animateCanvas);
    }
    
    animateCanvas();
}

// Gradient configuration applied via CSS - no admin panel needed

// Helper function to convert hex to rgba
function hexToRgba(hex, alpha = 1) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Make renderGradient globally accessible for color updates
window.renderGradient = renderGradient;

// Admin panel functions removed - using fixed warm gradient

// Video Section Functionality
function initializeVideoSection() {
    const videoContainer = document.querySelector('.video-container');
    
    if (videoContainer) {
        videoContainer.addEventListener('click', function() {
            // Show AI warning first
            showAIWarning();
            
            // Add a visual feedback
            const playButton = this.querySelector('.play-button');
            if (playButton) {
                playButton.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    playButton.style.transform = 'scale(1)';
                }, 150);
            }
        });

        // Add hover effects
        videoContainer.addEventListener('mouseenter', function() {
            const overlay = this.querySelector('.video-overlay');
            if (overlay) {
                overlay.style.opacity = '0.8';
            }
        });

        videoContainer.addEventListener('mouseleave', function() {
            const overlay = this.querySelector('.video-overlay');
            if (overlay) {
                overlay.style.opacity = '1';
            }
        });
    }
}

// Show AI content warning
function showAIWarning() {
    // Create AI warning popup
    const warning = document.createElement('div');
    warning.className = 'ai-warning';
    warning.innerHTML = `
        <h4>AI-Generated Content</h4>
        <p>This video contains AI-generated educational content about digital addiction and the Rat Park experiment.</p>
        <div class="ai-warning-buttons">
            <button class="primary-btn" onclick="proceedToVideo()">Watch Video</button>
            <button class="secondary-btn" onclick="closeAIWarning()">Cancel</button>
        </div>
    `;
    
    document.body.appendChild(warning);
    
    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(5px);
        z-index: 14000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    document.body.appendChild(backdrop);
    window.currentBackdrop = backdrop;
    
    // Animate in
    setTimeout(() => {
        warning.classList.add('active');
        backdrop.style.opacity = '1';
    }, 100);
    
    // Store reference for cleanup
    window.currentAIWarning = warning;
}

// Proceed to video after warning
function proceedToVideo() {
    closeAIWarning();
    setTimeout(() => {
        openVideoPopup();
    }, 300);
}

// Close AI warning
function closeAIWarning() {
    const warning = window.currentAIWarning;
    const backdrop = window.currentBackdrop;
    
    if (warning) {
        warning.classList.remove('active');
        if (backdrop) {
            backdrop.style.opacity = '0';
        }
        
        setTimeout(() => {
            if (document.body.contains(warning)) {
                document.body.removeChild(warning);
            }
            if (backdrop && document.body.contains(backdrop)) {
                document.body.removeChild(backdrop);
            }
            window.currentAIWarning = null;
            window.currentBackdrop = null;
        }, 400);
    }
}

// Open video popup
function openVideoPopup() {
    // Create video popup
    const popup = document.createElement('div');
    popup.className = 'video-popup';
    popup.innerHTML = `
        <div class="video-popup-content">
            <button class="video-popup-close" onclick="closeVideoPopup()">×</button>
            <video controls autoplay>
                <source src="/static/circuitweb/assets/CircuitExplan.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Animate in
    setTimeout(() => {
        popup.classList.add('active');
    }, 100);
    
    // Store reference for cleanup
    window.currentVideoPopup = popup;
    
    // Close on background click
    popup.addEventListener('click', function(e) {
        if (e.target === popup) {
            closeVideoPopup();
        }
    });
}

// Close video popup
function closeVideoPopup() {
    const popup = window.currentVideoPopup;
    if (popup) {
        popup.classList.remove('active');
        setTimeout(() => {
            document.body.removeChild(popup);
            window.currentVideoPopup = null;
        }, 300);
    }
}

// Initialize CTA buttons
function initializeCTAButtons() {
    const primaryCTA = document.querySelector('.cta-primary');
    const secondaryCTA = document.querySelector('.cta-secondary');
    
    if (primaryCTA) {
        primaryCTA.addEventListener('click', function() {
            showNotification('Community building feature coming soon! Join our waitlist to be the first to experience Circuit\'s anti-addiction matchmaking.');
        });
    }
    
    if (secondaryCTA) {
        secondaryCTA.addEventListener('click', function() {
            showNotification('Learn more about Circuit\'s research-backed approach to solving digital isolation and building genuine connections.');
        });
    }
}

// Initialize interactive demo
function initializeDemo() {
    // Initialize voice demo only
    initializeVoiceDemo();
}

async function simpleAnalyze() {
    const textInput = document.getElementById('textInput');
    const results = document.getElementById('results');
    
    if (!textInput || !results) return;
    
    const text = textInput.value.trim();
    if (!text) {
        alert('Enter text to analyze');
        return;
    }
    
    results.innerHTML = '<p style="color: #22c55e;">Analyzing...</p>';
    results.style.display = 'block';
    
    try {
        const data = await makeAPIRequest('/analyze-text', {
            method: 'POST',
            body: JSON.stringify({ text: text })
        });
        
        if (data.success && data.result && data.result.emotion_analysis) {
            const emotions = data.result.emotion_analysis.emotions;
            const primary = data.result.emotion_analysis.overall_emotion;
            const confidence = data.result.emotion_analysis.confidence;
            
            results.innerHTML = `
                <div style="background: rgba(34, 197, 94, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
                    <h4 style="color: #16a34a; margin-bottom: 16px;">Analysis Complete</h4>
                    <p style="margin-bottom: 8px;"><strong>Primary:</strong> <span style="color: #22c55e; text-transform: capitalize; font-weight: 700;">${primary}</span></p>
                    <p style="margin-bottom: 16px;"><strong>Confidence:</strong> ${Math.round(confidence * 100)}%</p>
                    <div style="text-align: left; max-width: 250px; margin: 0 auto;">
                        ${Object.entries(emotions).map(([emotion, value]) => 
                            `<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="text-transform: capitalize;">${emotion}:</span>
                                <span style="font-weight: 600;">${Math.round(value * 100)}%</span>
                            </div>`
                        ).join('')}
                    </div>
                </div>
            `;
        } else {
            results.innerHTML = `<p style="color: #ef4444;">${data.error || 'Analysis failed'}</p>`;
        }
        
    } catch (error) {
        results.innerHTML = `<p style="color: #ef4444;">${error.message}</p>`;
    }
}

function liveSpeechAnalysis() {
    const results = document.getElementById('results');
    const speechBtn = document.getElementById('speechBtn');
    const textInput = document.getElementById('textInput');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        results.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
                <p style="color: #dc2626;">Speech recognition unavailable</p>
                <p style="color: #666; font-size: 14px;">Use Chrome or Edge</p>
            </div>
        `;
        results.style.display = 'block';
        return;
    }
    
    if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
        results.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
                <p style="color: #dc2626;">Requires HTTPS</p>
                <p style="color: #666; font-size: 14px;">Use text input instead</p>
                <button onclick="focusTextInput()" 
                        style="margin-top: 12px; padding: 8px 16px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer; font-family: 'Sohne', sans-serif;">
                    Use Text Input
                </button>
            </div>
        `;
        results.style.display = 'block';
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false; // Disable interim for more stability
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    // Try to improve reliability
    if ('webkitSpeechRecognition' in window) {
        recognition.serviceURI = 'wss://www.google.com/speech-api/v2/recognize';
    }
    
    const timeout = setTimeout(() => {
        recognition.stop();
        results.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
                <p style="color: #dc2626;">Timed out</p>
                <p style="color: #666; font-size: 14px;">Try text input instead</p>
                <button onclick="focusTextInput()" 
                        style="margin-top: 12px; padding: 8px 16px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer; font-family: 'Sohne', sans-serif;">
                    Use Text Input
                </button>
            </div>
        `;
        speechBtn.textContent = 'Speech Analysis';
        speechBtn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
        speechBtn.onclick = liveSpeechAnalysis;
    }, 10000);
    
    results.innerHTML = `
        <div style="background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
            <p style="color: #1d4ed8; font-weight: 600;">Listening...</p>
            <p style="color: #666; font-size: 14px;">Speak now</p>
        </div>
    `;
    results.style.display = 'block';
    
    speechBtn.textContent = 'Stop';
    speechBtn.style.background = '#ef4444';
    speechBtn.onclick = () => {
        recognition.stop();
        speechBtn.textContent = 'Speech Analysis';
        speechBtn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
        speechBtn.onclick = liveSpeechAnalysis;
        results.innerHTML = '<p style="color: #666;">Stopped</p>';
    };
    
    recognition.onresult = async (event) => {
        clearTimeout(timeout);
        
        const transcript = event.results[0][0].transcript;
        
        results.innerHTML = `
            <div style="background: rgba(34, 197, 94, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
                <p style="color: #16a34a; font-weight: 600; margin-bottom: 16px;">"${transcript}"</p>
                <p style="color: #22c55e;">Analyzing...</p>
            </div>
        `;
        
        textInput.value = transcript;
        await simpleAnalyze();
        
        speechBtn.textContent = 'Speech Analysis';
        speechBtn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
        speechBtn.onclick = liveSpeechAnalysis;
    };
    
    recognition.onerror = (event) => {
        clearTimeout(timeout);
        
        const errors = {
            'network': 'Network issue',
            'not-allowed': 'Microphone access denied',
            'no-speech': 'No speech detected',
            'audio-capture': 'Microphone unavailable'
        };
        
        const errorMessage = errors[event.error] || event.error;
        
        results.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; text-align: center;">
                <p style="color: #dc2626; margin-bottom: 12px;">${errorMessage}</p>
                <button onclick="focusTextInput()" 
                        style="padding: 10px 20px; background: #22c55e; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: 'Sohne', sans-serif; font-weight: 600;">
                    Use Text Input
                </button>
            </div>
        `;
        
        speechBtn.textContent = 'Speech Analysis';
        speechBtn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
        speechBtn.onclick = liveSpeechAnalysis;
    };
    
    recognition.onend = () => {
        if (speechBtn.textContent.includes('Stop')) {
            speechBtn.textContent = 'Speech Analysis';
            speechBtn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
            speechBtn.onclick = liveSpeechAnalysis;
        }
    };
    
    recognition.start();
}

// Set example text function
function setExampleText(text) {
    const textInput = document.getElementById('textInput');
    if (textInput) {
        textInput.value = text;
        textInput.focus();
        
        // Add a subtle animation to show the text changed
        textInput.style.background = 'rgba(34, 197, 94, 0.1)';
        setTimeout(() => {
            textInput.style.background = 'rgba(255, 255, 255, 0.95)';
        }, 300);
    }
}

// Focus text input helper
function focusTextInput() {
    const textInput = document.getElementById('textInput');
    const results = document.getElementById('results');
    
    if (textInput) {
        textInput.focus();
        textInput.select();
        
        // Hide error results
        if (results) {
            results.style.display = 'none';
        }
        
        // Add visual feedback
        textInput.style.borderColor = '#16a34a';
        textInput.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.2)';
        setTimeout(() => {
            textInput.style.borderColor = '#22c55e';
            textInput.style.boxShadow = 'none';
        }, 1000);
    }
}

// Set example text and automatically analyze
async function setExampleAndAnalyze(text) {
    const textInput = document.getElementById('textInput');
    if (textInput) {
        textInput.value = text;
        
        // Add visual feedback
        textInput.style.background = 'rgba(34, 197, 94, 0.1)';
        setTimeout(() => {
            textInput.style.background = 'rgba(255, 255, 255, 0.95)';
        }, 300);
        
        // Automatically analyze after setting text
        setTimeout(() => {
            simpleAnalyze();
        }, 400);
    }
}



// Add keyboard navigation
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        // Ensure focus is visible on interactive elements
        const focusableElements = document.querySelectorAll('button, .action-card, .persona-card, .nav-item');
        focusableElements.forEach(el => {
            el.addEventListener('focus', function() {
                this.style.outline = '2px solid #6366F1';
                this.style.outlineOffset = '2px';
            });
            
            el.addEventListener('blur', function() {
                this.style.outline = 'none';
            });
        });
    }
});

// Add touch gestures for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', function(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
        const rightArrow = document.querySelector('.right-arrow');
        const leftArrow = document.querySelector('.left-arrow');
        
        if (diff > 0 && rightArrow) {
            // Swipe left - next personas
            rightArrow.click();
        } else if (diff < 0 && leftArrow) {
            // Swipe right - previous personas
            leftArrow.click();
        }
    }
}

// Toggle expandable value cards
function toggleValue(card) {
    card.classList.toggle('expanded');
}

// Timeline navigation functionality
function initializeTimelineNavigation() {
    let currentTimelineIndex = 0;
    const timelineData = [
        {
            year: "1978 | SOCIAL CONNECTION RESEARCH",
            title: "Understanding isolation and community resilience",
            image: "Assets/Ratparkimage.png",
            content: [
                "Landmark experiments in behavioral psychology demonstrated that addiction patterns were strongly influenced by social environment and community connections, not just individual willpower or substance properties.",
                "The groundbreaking Rat Park experiment determined that when subjects had access to social interaction, enriched environments, and community bonds, they displayed natural resilience to addictive behaviors and compulsive patterns.",
                "This research laid the groundwork for understanding how social connections serve as protective factors against various forms of behavioral and substance addiction."
            ]
        },
        {
            year: "1990s | DIGITAL REWARD SYSTEMS",
            title: "The rise of variable-ratio reward mechanisms",
            image: "Assets/DigitalRewards.png",
            content: [
                "As personal computers and early internet emerged, software designers discovered they could create compelling experiences using psychological principles from behavioral research and gambling studies.",
                "Variable-ratio reward schedules, where rewards come at unpredictable intervals, proved incredibly effective at maintaining user engagement by exploiting dopamine's reward prediction error mechanisms.",
                "What started as game design principles gradually evolved into sophisticated systems designed to capture attention through neurochemical manipulation rather than genuine satisfaction."
            ]
        },
        {
            year: "2007 | NEUROCHEMICAL UNDERSTANDING",
            title: "Mapping the brain's social reward systems",
            image: "Assets/NeuroChem.png",
            content: [
                "Advances in neuroscience helped reveal how social interactions activate oxytocin and endocannabinoid systems, creating reward experiences distinct from dopamine-driven individual achievements.",
                "It has been determined that social rewards engage the same brain circuits as individual rewards, but with crucial differences: sharing victories with friends can be more rewarding than solo wins, and social bonds help prevent tolerance buildup."
            ]
        }
    ];

    const timelineItem = document.querySelector('.timeline-item');
    const prevButton = document.querySelector('.timeline-prev');
    const nextButton = document.querySelector('.timeline-next');
    const dots = document.querySelectorAll('.timeline-dot');

    if (!timelineItem || !prevButton || !nextButton) {
        return; // Timeline not found on this page
    }

    function updateTimeline(index) {
        const data = timelineData[index];
        const yearElement = timelineItem.querySelector('.timeline-year');
        const titleElement = timelineItem.querySelector('.timeline-content h3');
        const contentElement = timelineItem.querySelector('.timeline-content');
        const imageElement = timelineItem.querySelector('.placeholder-portrait');

        if (yearElement) yearElement.textContent = data.year;
        if (titleElement) titleElement.textContent = data.title;

        // Update image
        if (imageElement && data.image) {
            imageElement.innerHTML = `<img src="${data.image}" alt="${data.title}" style="width: auto; height: auto; max-width: 350px; object-fit: contain; border-radius: 8px;">`;
        }

        // Update content paragraphs
        const existingParagraphs = contentElement.querySelectorAll('p');
        existingParagraphs.forEach(p => p.remove());

        data.content.forEach(paragraph => {
            const p = document.createElement('p');
            p.textContent = paragraph;
            contentElement.appendChild(p);
        });

        // Update dots
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });

        currentTimelineIndex = index;
    }

    // Event listeners
    prevButton.addEventListener('click', () => {
        const newIndex = currentTimelineIndex > 0 ? currentTimelineIndex - 1 : timelineData.length - 1;
        updateTimeline(newIndex);
    });

    nextButton.addEventListener('click', () => {
        const newIndex = currentTimelineIndex < timelineData.length - 1 ? currentTimelineIndex + 1 : 0;
        updateTimeline(newIndex);
    });

    // Dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            updateTimeline(index);
        });
    });

    // Initialize with first item
    updateTimeline(0);
}

// About page video functionality
function initializeAboutVideo() {
    const videoContainer = document.querySelector('.about-page .vision-video');
    
    if (videoContainer) {
        videoContainer.addEventListener('click', function() {
            openVideoPopup();
        });

        // Add hover effects
        videoContainer.addEventListener('mouseenter', function() {
            const playButton = this.querySelector('.play-button');
            if (playButton) {
                playButton.style.transform = 'scale(1.1)';
            }
        });

        videoContainer.addEventListener('mouseleave', function() {
            const playButton = this.querySelector('.play-button');
            if (playButton) {
                playButton.style.transform = 'scale(1)';
            }
        });
    }
}

// Voice Demo Functionality
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function initializeVoiceDemo() {
    const recordBtn = document.getElementById('recordBtn');
    
    if (!recordBtn) {
        console.warn('Record button not found! Element with ID "recordBtn" does not exist.');
        return;
    }

    recordBtn.addEventListener('click', toggleRecording);
}

async function toggleRecording() {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const emotionResults = document.getElementById('emotionResults');
    const demoStatus = document.getElementById('demoStatus');

    if (!isRecording) {
        try {
            if (demoStatus) demoStatus.textContent = 'Requesting microphone...';
            
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            if (demoStatus) demoStatus.textContent = 'Recording...';
            
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                if (demoStatus) demoStatus.textContent = 'Processing...';
                
                try {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    await analyzeAudio(audioBlob);
                } catch (error) {
                    showNotification('Processing error');
                    if (demoStatus) demoStatus.textContent = 'Error';
                }
                
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.onerror = (error) => {
                showNotification('Recording error');
            };

            mediaRecorder.start();
            isRecording = true;

            recordBtn.classList.add('recording');
            recordBtn.querySelector('.record-text').textContent = 'Stop';
            recordBtn.querySelector('.record-icon').textContent = '';
            recordingStatus.style.display = 'flex';
            emotionResults.style.display = 'none';

            showNotification('Recording started');

        } catch (error) {
            if (demoStatus) demoStatus.textContent = 'Microphone error';
            
            let msg = 'Microphone unavailable';
            if (error.name === 'NotAllowedError') {
                msg = 'Microphone access denied';
            } else if (error.name === 'NotFoundError') {
                msg = 'No microphone found';
            }
            
            showNotification(msg);
            showTextInputFallback();
        }
    } else {
        try {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
            isRecording = false;

            recordBtn.classList.remove('recording');
            recordBtn.querySelector('.record-text').textContent = 'Record';
            recordBtn.querySelector('.record-icon').textContent = '';
            recordingStatus.style.display = 'none';
            
            if (demoStatus) demoStatus.textContent = 'Analyzing...';
            showNotification('Processing audio...');
            
        } catch (error) {
            showNotification('Error stopping');
        }
    }
}

async function analyzeAudio(audioBlob) {
    const demoStatus = document.getElementById('demoStatus');
    
    try {
        if (demoStatus) demoStatus.textContent = 'Analyzing...';
        showLoadingState();
        
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('retry_mode', 'aggressive');
        
        const result = await makeAPIRequest('/analyze-audio', {
            method: 'POST',
            body: formData
        });
        
        if (result.success && result.result) {
            if (demoStatus) demoStatus.textContent = 'Done';
            displayEmotionResults(result.result);
        } else {
            if (demoStatus) demoStatus.textContent = 'Unavailable';
            showAudioFallbackMessage(result.error || 'Audio analysis unavailable', 'Try text input');
        }
        
    } catch (error) {
        if (demoStatus) demoStatus.textContent = 'Error';
        showAudioFallbackMessage('Audio analysis failed', 'Try text input');
    }
}

function displayEmotionResults(analysisResult) {
    try {
        const emotionResults = document.getElementById('emotionResults');
        const transcriptionText = document.getElementById('transcriptionText');
        const emotionBars = document.getElementById('emotionBars');
        const primaryEmotion = document.getElementById('primaryEmotion');
        const confidenceScore = document.getElementById('confidenceScore');
        
        if (!emotionResults || !transcriptionText || !emotionBars || !primaryEmotion || !confidenceScore) {
            throw new Error('Missing DOM elements');
        }

        const transcription = analysisResult.transcription || 'No speech detected';
        const isDemoResult = analysisResult.isDemo === true;
        transcriptionText.textContent = transcription;
        
        if (isDemoResult) {
            const demoIndicator = document.createElement('span');
            demoIndicator.style.cssText = 'font-size: 12px; color: #f59e0b; font-weight: 600; margin-left: 8px;';
            demoIndicator.textContent = '(demo)';
            transcriptionText.appendChild(demoIndicator);
        }

        if (analysisResult.emotion_analysis) {
            const emotions = analysisResult.emotion_analysis.emotions;
            const overallEmotion = analysisResult.emotion_analysis.overall_emotion;
            const confidence = analysisResult.emotion_analysis.confidence;

            emotionBars.innerHTML = '';
            Object.entries(emotions).forEach(([emotion, value]) => {
                const percentage = Math.round(value * 100);
                const emotionBar = document.createElement('div');
                emotionBar.className = 'emotion-bar';
                emotionBar.innerHTML = `
                    <span class="emotion-name">${emotion}</span>
                    <div class="emotion-progress">
                        <div class="emotion-fill emotion-${emotion}" style="width: ${percentage}%"></div>
                    </div>
                    <span class="emotion-value">${percentage}%</span>
                `;
                emotionBars.appendChild(emotionBar);
            });

            primaryEmotion.textContent = overallEmotion;
            confidenceScore.textContent = Math.round(confidence * 100) + '%';
        }

        emotionResults.style.display = 'block';
        
        const demoStatus = document.getElementById('demoStatus');
        if (demoStatus) demoStatus.textContent = 'Done';
        
    } catch (error) {
        showNotification('Display error');
        
        try {
            const emotionResults = document.getElementById('emotionResults');
            if (emotionResults) {
                emotionResults.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #ef4444;">
                        <p>Unable to display results</p>
                        <button onclick="resetDemo()" style="margin-top: 10px; padding: 8px 16px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer;">Retry</button>
                    </div>
                `;
                emotionResults.style.display = 'block';
            }
        } catch (uiError) {}
    }
}

function showTextInputFallback() {
    const emotionResults = document.getElementById('emotionResults');
    emotionResults.innerHTML = `
        <div class="text-fallback" style="text-align: center; padding: 20px;">
            <p style="color: #666; margin-bottom: 16px;">Text analysis:</p>
            <div style="display: flex; gap: 8px; max-width: 400px; margin: 0 auto;">
                <input type="text" id="textInput" placeholder="Enter text to analyze" 
                       style="flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-family: 'Sohne', sans-serif; font-size: 14px;"
                       onkeypress="if(event.key==='Enter') analyzeText()">
                <button onclick="analyzeText()" style="padding: 12px 20px; background: #22c55e; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: 'Sohne', sans-serif; font-weight: 600;">Analyze</button>
            </div>
        </div>
    `;
    emotionResults.style.display = 'block';
}

async function analyzeText() {
    const textInput = document.getElementById('textInput');
    const text = textInput ? textInput.value.trim() : '';
    const demoStatus = document.getElementById('demoStatus');
    
    if (!text) {
        showNotification('Enter text to analyze');
        return;
    }

    try {
        if (demoStatus) demoStatus.textContent = 'Analyzing...';
        showLoadingState();
        
        const result = await makeAPIRequest('/analyze-text', {
            method: 'POST',
            body: JSON.stringify({ text: text })
        });
        
        if (result.success && result.result) {
            if (demoStatus) demoStatus.textContent = 'Done';
            displayEmotionResults(result.result);
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        if (demoStatus) demoStatus.textContent = 'Error';
        showError(error.message);
    }
}

function showDemoResults(userText = "I'm excited about this project", isDemo = true) {
    try {
        let emotions = {
            anticipation: 0.45, joy: 0.35, trust: 0.12, surprise: 0.05,
            anger: 0.01, fear: 0.01, sadness: 0.01, disgust: 0.00
        };
        let primaryEmotion = "anticipation";
        
        const text = userText.toLowerCase();
        
        if (text.includes('excited') || text.includes('happy') || text.includes('great') || text.includes('amazing')) {
            emotions = { joy: 0.72, anticipation: 0.15, trust: 0.08, surprise: 0.03, anger: 0.01, fear: 0.01, sadness: 0.00, disgust: 0.00 };
            primaryEmotion = "joy";
        } else if (text.includes('nervous') || text.includes('worried') || text.includes('anxious') || text.includes('scared')) {
            emotions = { fear: 0.58, anticipation: 0.22, sadness: 0.12, anger: 0.04, joy: 0.02, trust: 0.01, surprise: 0.01, disgust: 0.00 };
            primaryEmotion = "fear";
        } else if (text.includes('angry') || text.includes('frustrated') || text.includes('mad') || text.includes('furious')) {
            emotions = { anger: 0.65, disgust: 0.18, sadness: 0.08, fear: 0.05, anticipation: 0.02, joy: 0.01, trust: 0.01, surprise: 0.00 };
            primaryEmotion = "anger";
        } else if (text.includes('sad') || text.includes('disappointed') || text.includes('upset') || text.includes('hurt')) {
            emotions = { sadness: 0.55, fear: 0.18, anger: 0.12, anticipation: 0.08, disgust: 0.04, joy: 0.02, trust: 0.01, surprise: 0.00 };
            primaryEmotion = "sadness";
        }
        
        displayEmotionResults({
            transcription: userText,
            emotion_analysis: { overall_emotion: primaryEmotion, confidence: 0.78, emotions: emotions },
            isDemo: isDemo
        });
        
    } catch (error) {
        showNotification('Error generating results');
        try {
            displayEmotionResults({
                transcription: userText,
                emotion_analysis: {
                    overall_emotion: "neutral",
                    confidence: 0.50,
                    emotions: { anticipation: 0.5, joy: 0.2, trust: 0.1, surprise: 0.1, anger: 0.05, fear: 0.03, sadness: 0.02, disgust: 0.00 }
                },
                isDemo: isDemo
            });
        } catch (fallbackError) {
            showNotification('Cannot display results');
        }
    }
}

function showLoadingState() {
    const emotionResults = document.getElementById('emotionResults');
    if (emotionResults) {
        emotionResults.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #22c55e;">
                <p style="color: #16a34a; margin-bottom: 8px;">Analyzing...</p>
                <div style="margin-top: 20px;">
                    <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #22c55e; border-radius: 50%; border-top-color: transparent; animation: spin 1s linear infinite;"></div>
                </div>
            </div>
        `;
        emotionResults.style.display = 'block';
    }
}

function showError(message) {
    const emotionResults = document.getElementById('emotionResults');
    if (emotionResults) {
        emotionResults.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #ef4444;">
                <p style="color: #dc2626; margin-bottom: 12px;">${message}</p>
                <button onclick="resetDemo()" style="padding: 12px 24px; background: #22c55e; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: 'Sohne', sans-serif; font-weight: 600;">Retry</button>
            </div>
        `;
        emotionResults.style.display = 'block';
    }
}

function showAudioFallbackMessage(message, suggestion) {
    const emotionResults = document.getElementById('emotionResults');
    if (emotionResults) {
        emotionResults.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <p style="color: #666; margin-bottom: 16px;">${message}</p>
                <p style="color: #22c55e; font-weight: 600; margin-bottom: 20px;">${suggestion}</p>
                <div style="max-width: 400px; margin: 0 auto;">
                    <input type="text" id="fallback-text" placeholder="Type what you said..." 
                           style="width: 100%; padding: 12px 16px; border: 2px solid #22c55e; border-radius: 8px; font-family: 'Sohne', sans-serif; margin-bottom: 12px;" />
                    <button onclick="analyzeTextFromFallback()" 
                            style="padding: 12px 24px; background: #22c55e; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: 'Sohne', sans-serif; font-weight: 600;">Analyze</button>
                </div>
            </div>
        `;
        emotionResults.style.display = 'block';
    }
}

async function analyzeTextFromFallback() {
    const text = document.getElementById('fallback-text')?.value?.trim();
    if (text) {
        const directTextInput = document.getElementById('directTextInput');
        if (directTextInput) {
            directTextInput.value = text;
        }
        await analyzeDirectText();
    } else {
        showNotification('Enter text to analyze');
    }
}

async function testAPIDirectly() {
    const emotionResults = document.getElementById('emotionResults');
    const demoStatus = document.getElementById('demoStatus');
    
    try {
        if (demoStatus) demoStatus.textContent = 'Testing...';
        
        const testText = "I am thrilled about this project";
        
        const result = await makeAPIRequest('/analyze-text', {
            method: 'POST',
            body: JSON.stringify({ text: testText })
        });
        
        if (result.success) {
            if (emotionResults) {
                const emotions = result.result.emotion_analysis.emotions;
                const overallEmotion = result.result.emotion_analysis.overall_emotion;
                const confidence = result.result.emotion_analysis.confidence;
                
                emotionResults.innerHTML = `
                    <div style="text-align: center; padding: 20px; background: rgba(34, 197, 94, 0.1); border-radius: 12px;">
                        <h3 style="color: #16a34a; margin-bottom: 16px;">Test Complete</h3>
                        <p style="margin-bottom: 12px;"><strong>Text:</strong> "${testText}"</p>
                        <p style="margin-bottom: 12px;"><strong>Primary:</strong> <span style="color: #22c55e; font-weight: 700; text-transform: capitalize;">${overallEmotion}</span></p>
                        <p style="margin-bottom: 16px;"><strong>Confidence:</strong> ${Math.round(confidence * 100)}%</p>
                        <div style="text-align: left; max-width: 300px; margin: 0 auto;">
                            ${Object.entries(emotions).map(([emotion, value]) => 
                                `<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="text-transform: capitalize;">${emotion}:</span>
                                    <span style="font-weight: 600;">${Math.round(value * 100)}%</span>
                                </div>`
                            ).join('')}
                        </div>
                        <button onclick="resetDemo()" style="margin-top: 16px; padding: 8px 16px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer;">Reset</button>
                    </div>
                `;
                emotionResults.style.display = 'block';
            }
            
            if (demoStatus) demoStatus.textContent = 'Done';
            
        } else {
            throw new Error(result.error || 'Test failed');
        }
        
    } catch (error) {
        if (demoStatus) demoStatus.textContent = 'Failed';
        showNotification('Test failed: ' + error.message);
        
        if (emotionResults) {
            emotionResults.innerHTML = `
                <div style="text-align: center; padding: 20px; background: rgba(239, 68, 68, 0.1); border-radius: 12px;">
                    <p style="color: #dc2626; margin-bottom: 16px;">${error.message}</p>
                    <button onclick="resetDemo()" style="padding: 8px 16px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer;">Reset</button>
                </div>
            `;
            emotionResults.style.display = 'block';
        }
    }
}

function resetDemo() {
    const emotionResults = document.getElementById('emotionResults');
    const demoStatus = document.getElementById('demoStatus');
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const directTextInput = document.getElementById('directTextInput');
    
    if (emotionResults) emotionResults.style.display = 'none';
    if (recordingStatus) recordingStatus.style.display = 'none';
    if (demoStatus) demoStatus.textContent = 'Ready';
    if (directTextInput) directTextInput.value = '';
    
    isRecording = false;
    audioChunks = [];
    
    if (recordBtn) {
        recordBtn.classList.remove('recording');
        recordBtn.querySelector('.record-text').textContent = 'Record';
        recordBtn.querySelector('.record-icon').textContent = '';
    }
    
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}

async function analyzeDirectText() {
    const directTextInput = document.getElementById('directTextInput');
    const text = directTextInput ? directTextInput.value.trim() : '';
    const demoStatus = document.getElementById('demoStatus');
    
    if (!text) {
        showNotification('Enter text to analyze');
        if (directTextInput) directTextInput.focus();
        return;
    }

    try {
        if (demoStatus) demoStatus.textContent = 'Analyzing...';
        showLoadingState();
        
        const result = await makeAPIRequest('/analyze-text', {
            method: 'POST',
            body: JSON.stringify({ text: text })
        });
        
        if (result.success && result.result) {
            if (demoStatus) demoStatus.textContent = 'Done';
            displayEmotionResults(result.result);
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        if (demoStatus) demoStatus.textContent = 'Error';
        showError(error.message);
    }
}


