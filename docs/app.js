let currentCustomer = null;

function loadCustomer(customerType) {
    currentCustomer = customerType;
    const customer = customerData[customerType];
    
    // Hide initial message and show customer details
    document.getElementById('initialMessage').classList.add('hidden');
    document.getElementById('customerDetails').classList.remove('hidden');
    
    // Load customer profile
    document.getElementById('customerName').textContent = customer.name;
    document.getElementById('customerAge').textContent = customer.age;
    document.getElementById('customerBackground').textContent = customer.background;
    document.getElementById('customerEmotion').textContent = customer.emotionalState;
    document.getElementById('customerProblem').textContent = customer.problem;
    
    // Load success criteria
    const successCriteriaList = document.getElementById('successCriteria');
    successCriteriaList.innerHTML = customer.successCriteria.map((criterion, index) => 
        `<div class="flex items-start mb-3 bg-white rounded-lg p-3 shadow-sm">
            <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                ${index + 1}
            </div>
            <span class="text-gray-800 flex-1">${criterion}</span>
        </div>`
    ).join('');
    
    // Load performance analysis if available
    if (customer.hasAnalysis) {
        document.getElementById('performanceSection').classList.remove('hidden');
        document.getElementById('detailedAnalysisSection').classList.remove('hidden');
        
        const scoreElement = document.getElementById('performanceScore');
        scoreElement.textContent = customer.performanceScore;
        scoreElement.className = 'score-badge ' + customer.scoreClass;
        
        // Load what went well
        const wellList = document.getElementById('whatWentWell');
        wellList.innerHTML = customer.whatWentWell.map(item => 
            `<div class="flex items-start mb-2">
                <svg class="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span>${item}</span>
            </div>`
        ).join('');
        
        // Load mistakes
        const mistakesList = document.getElementById('criticalMistakes');
        mistakesList.innerHTML = customer.criticalMistakes.map(item => 
            `<div class="flex items-start mb-2">
                <svg class="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>
                <span>${item}</span>
            </div>`
        ).join('');
        
        // Load key learnings
        const learningsList = document.getElementById('keyLearnings');
        learningsList.innerHTML = customer.keyLearnings.map(item => 
            `<div class="flex items-start mb-2">
                <span class="text-2xl mr-2">📚</span>
                <span>${item}</span>
            </div>`
        ).join('');
        
        // Load recommendations
        const recommendationsList = document.getElementById('recommendations');
        recommendationsList.innerHTML = customer.recommendations.map(item => 
            `<div class="flex items-start mb-2">
                <span class="text-2xl mr-2">💡</span>
                <span>${item}</span>
            </div>`
        ).join('');
    } else {
        document.getElementById('performanceSection').classList.add('hidden');
        document.getElementById('detailedAnalysisSection').classList.add('hidden');
    }
    
    // Load chat transcript
    const chatTranscript = document.getElementById('chatTranscript');
    chatTranscript.innerHTML = customer.dialogue.map(message => {
        if (message.role === 'CSR') {
            return `
                <div class="flex justify-end">
                    <div class="max-w-[70%]">
                        <div class="text-xs text-gray-500 mb-1 text-right font-semibold">CSR (You)</div>
                        <div class="chat-bubble-csr p-4 shadow-sm">
                            ${escapeHtml(message.message)}
                        </div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="flex justify-start">
                    <div class="max-w-[70%]">
                        <div class="text-xs text-gray-500 mb-1 font-semibold">Customer (AI)</div>
                        <div class="chat-bubble-customer p-4 shadow-sm text-gray-800">
                            ${escapeHtml(message.message)}
                        </div>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add visual feedback for selected customer
document.querySelectorAll('.customer-card').forEach(card => {
    card.addEventListener('click', function() {
        document.querySelectorAll('.customer-card').forEach(c => {
            c.classList.remove('border-purple-500', 'bg-purple-50');
            c.classList.add('border-transparent');
        });
        this.classList.remove('border-transparent');
        this.classList.add('border-purple-500', 'bg-purple-50');
    });
});

