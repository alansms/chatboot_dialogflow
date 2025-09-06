// FiapNet - Main JavaScript Application

class FiapNetApp {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.loadStats();
    }
    
    setupEventListeners() {
        // Global event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.initializePage();
        });
        
        // Navigation active state
        this.setActiveNavigation();
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    initializeComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    initializePage() {
        // Page-specific initialization
        const currentPage = this.getCurrentPage();
        
        switch (currentPage) {
            case 'chat':
                this.initializeChat();
                break;
            case 'status':
                this.initializeStatus();
                break;
            case 'faq':
                this.initializeFAQ();
                break;
            case 'index':
                this.initializeHome();
                break;
        }
    }
    
    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('/chat')) return 'chat';
        if (path.includes('/status')) return 'status';
        if (path.includes('/faq')) return 'faq';
        if (path.includes('/admin')) return 'admin';
        return 'index';
    }
    
    setActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href.replace('/', ''))) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    
    // Home page initialization
    initializeHome() {
        // Animate stats on scroll
        this.animateStatsOnScroll();
        
        // Initialize feature cards hover effects
        this.initializeFeatureCards();
    }
    
    animateStatsOnScroll() {
        const statsSection = document.querySelector('.bg-light');
        if (!statsSection) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateNumbers();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(statsSection);
    }
    
    animateNumbers() {
        const numberElements = document.querySelectorAll('.stat-item h3');
        
        numberElements.forEach(element => {
            const finalNumber = parseInt(element.textContent);
            if (isNaN(finalNumber)) return;
            
            let currentNumber = 0;
            const increment = finalNumber / 50;
            const timer = setInterval(() => {
                currentNumber += increment;
                if (currentNumber >= finalNumber) {
                    element.textContent = finalNumber;
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(currentNumber);
                }
            }, 50);
        });
    }
    
    initializeFeatureCards() {
        const featureCards = document.querySelectorAll('.card');
        
        featureCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }
    
    // Chat page initialization
    initializeChat() {
        if (typeof ChatApp !== 'undefined') {
            this.chatApp = new ChatApp();
        }
    }
    
    // Status page initialization
    initializeStatus() {
        if (typeof StatusApp !== 'undefined') {
            this.statusApp = new StatusApp();
        }
    }
    
    // FAQ page initialization
    initializeFAQ() {
        this.initializeFAQSearch();
        this.initializeAccordionAnimations();
    }
    
    initializeFAQSearch() {
        const searchInput = document.getElementById('faq-search');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            this.filterFAQItems(searchTerm);
        });
    }
    
    filterFAQItems(searchTerm) {
        const accordionItems = document.querySelectorAll('.accordion-item');
        
        accordionItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = 'block';
                item.style.animation = 'fadeIn 0.3s ease-in';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    initializeAccordionAnimations() {
        const accordionButtons = document.querySelectorAll('.accordion-button');
        
        accordionButtons.forEach(button => {
            button.addEventListener('click', () => {
                const target = document.querySelector(button.getAttribute('data-bs-target'));
                if (target) {
                    setTimeout(() => {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'nearest'
                        });
                    }, 300);
                }
            });
        });
    }
    
    // Load statistics
    loadStats() {
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                this.updateStatsDisplay(data);
            })
            .catch(error => {
                console.error('Erro ao carregar estatísticas:', error);
            });
    }
    
    updateStatsDisplay(data) {
        const elements = {
            'chamados-ativos': data.chamados_ativos,
            'clientes-cadastrados': data.clientes_cadastrados,
            'total-chamados': data.total_chamados
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    // Utility methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    showLoading(element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<span class="loading"></span> Carregando...';
        element.disabled = true;
        
        return () => {
            element.innerHTML = originalContent;
            element.disabled = false;
        };
    }
    
    // API methods
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            this.showNotification('Erro na comunicação com o servidor', 'danger');
            throw error;
        }
    }
    
    // WebSocket connection (for real-time features)
    connectWebSocket() {
        // In production, implement real WebSocket connection
        // For now, simulate connection status
        this.isConnected = true;
        this.updateConnectionStatus();
    }
    
    updateConnectionStatus() {
        const statusElement = document.getElementById('status-indicator');
        const connectionElement = document.getElementById('connection-status');
        
        if (statusElement) {
            statusElement.innerHTML = this.isConnected 
                ? '<i class="fas fa-circle me-1"></i>Online'
                : '<i class="fas fa-circle me-1"></i>Offline';
            statusElement.className = `badge ${this.isConnected ? 'bg-success' : 'bg-danger'} me-2`;
        }
        
        if (connectionElement) {
            connectionElement.textContent = this.isConnected 
                ? 'Conectado' 
                : 'Desconectado';
        }
    }
}

// Initialize the application
const app = new FiapNetApp();

// Global utility functions
window.FiapNet = {
    showNotification: (message, type) => app.showNotification(message, type),
    apiRequest: (url, options) => app.apiRequest(url, options),
    showLoading: (element) => app.showLoading(element)
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FiapNetApp;
}
