// Clean script for CircuitWeb about page

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing about page...');
    
    // Initialize only what we need for about page
    initializeNavigation();
    initializeTimelineNavigation();
    initializeAboutVideo();
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

// Video popup functionality
function openVideoPopup() {
    // Create video popup
    const popup = document.createElement('div');
    popup.className = 'video-popup';
    popup.innerHTML = `
        <div class="video-popup-content">
            <button class="video-popup-close" onclick="closeVideoPopup()">×</button>
            <video controls autoplay>
                <source src="CircuitDemo.mp4" type="video/mp4">
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
            if (document.body.contains(popup)) {
                document.body.removeChild(popup);
            }
            window.currentVideoPopup = null;
        }, 300);
    }
}



