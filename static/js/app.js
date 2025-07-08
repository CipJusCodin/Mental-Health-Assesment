document.addEventListener('DOMContentLoaded', function() {
    const submitAssessment = document.getElementById('submit-assessment');
    const backToAssessment = document.getElementById('back-to-assessment');
    const assessmentContainer = document.getElementById('assessment-container');
    const resultsContainer = document.getElementById('results-container');
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendMessage = document.getElementById('send-message');
    const assessmentLoader = document.getElementById('assessment-loader');
    const chatLoader = document.getElementById('chat-loader');
    const errorMessage = document.getElementById('error-message');
    
    // Store assessment results
    let rawAssessmentResults = '';
    
    // Submit assessment
    submitAssessment.addEventListener('click', function() {
        // Show loader and hide error
        assessmentLoader.style.display = 'block';
        errorMessage.style.display = 'none';
        submitAssessment.disabled = true;
        
        // Collect all form data
        const formData = {};
        
        // Get PHQ9 scores
        for (let i = 1; i <= 9; i++) {
            const selectedOption = document.querySelector(`input[name="phq${i}"]:checked`);
            formData[`phq${i}`] = selectedOption ? selectedOption.value : "0";
        }
        
        // Get GAD7 scores
        for (let i = 1; i <= 7; i++) {
            const selectedOption = document.querySelector(`input[name="gad${i}"]:checked`);
            formData[`gad${i}`] = selectedOption ? selectedOption.value : "0";
        }
        
        // Send data to API
        fetch('/api/assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            assessmentLoader.style.display = 'none';
            submitAssessment.disabled = false;
            
            if (data.error) {
                // Show error
                errorMessage.textContent = data.error;
                errorMessage.style.display = 'block';
                return;
            }
            
            // Store raw assessment for chat
            rawAssessmentResults = data.raw_assessment || '';
            
            // Display results
            document.getElementById('depression-status').textContent = data.depression_status || '';
            document.getElementById('assessment-scores').textContent = 
                `PHQ-9 Score: ${data.phq9_score || 0}, GAD-7 Score: ${data.gad7_score || 0}`;
            
            // Clear and populate lists
            const dietList = document.getElementById('diet-recommendations');
            dietList.innerHTML = '';
            if (data.diet_recommendations && Array.isArray(data.diet_recommendations)) {
                data.diet_recommendations.forEach(item => {
                    if (item && item.trim()) {
                        const li = document.createElement('li');
                        li.textContent = item;
                        dietList.appendChild(li);
                    }
                });
            }
            
            const lifestyleList = document.getElementById('lifestyle-recommendations');
            lifestyleList.innerHTML = '';
            if (data.lifestyle_recommendations && Array.isArray(data.lifestyle_recommendations)) {
                data.lifestyle_recommendations.forEach(item => {
                    if (item && item.trim()) {
                        const li = document.createElement('li');
                        li.textContent = item;
                        lifestyleList.appendChild(li);
                    }
                });
            }
            
            document.getElementById('medication-considerations').textContent = data.medication_considerations || '';
            document.getElementById('disclaimer').textContent = data.disclaimer || '';
            
            // Show results and chat
            assessmentContainer.style.display = 'none';
            resultsContainer.style.display = 'block';
            chatContainer.style.display = 'block';
        })
        .catch(error => {
            // Hide loader and show error
            assessmentLoader.style.display = 'none';
            submitAssessment.disabled = false;
            errorMessage.textContent = "An error occurred. Please try again.";
            errorMessage.style.display = 'block';
            console.error('Error:', error);
        });
    });
    
    // Back to assessment
    backToAssessment.addEventListener('click', function() {
        resultsContainer.style.display = 'none';
        assessmentContainer.style.display = 'block';
        // Clear chat history
        chatMessages.innerHTML = '';
    });
    
    // Chat functionality
    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function sendQuery(query) {
        // Show loader
        chatLoader.style.display = 'block';
        sendMessage.disabled = true;
        
        // Send query to API
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                assessment_results: rawAssessmentResults
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            chatLoader.style.display = 'none';
            sendMessage.disabled = false;
            
            if (data.error) {
                addMessage("Error: " + data.error, false);
                return;
            }
            
            addMessage(data.answer, false);
        })
        .catch(error => {
            // Hide loader
            chatLoader.style.display = 'none';
            sendMessage.disabled = false;
            addMessage("Sorry, an error occurred. Please try again.", false);
            console.error('Error:', error);
        });
    }
    
    // Send message button
    sendMessage.addEventListener('click', function() {
        const query = chatInput.value.trim();
        if (query) {
            addMessage(query, true);
            chatInput.value = '';
            sendQuery(query);
        }
    });
    
    // Enter key in chat input
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = chatInput.value.trim();
            if (query) {
                addMessage(query, true);
                chatInput.value = '';
                sendQuery(query);
            }
        }
    });
});