let ws;
let currentItineraryContent = '';

function validateInputs() {
    const destination = document.getElementById("destination").value.trim();
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    const budgetMin = document.getElementById("budgetMin").value;
    const budgetMax = document.getElementById("budgetMax").value;

    if (!destination) {
        alert("Please enter a destination");
        return false;
    }

    if (!startDate || !endDate) {
        alert("Please select both start and end dates");
        return false;
    }

    if (new Date(startDate) > new Date(endDate)) {
        alert("Start date must be before end date");
        return false;
    }

    if (!budgetMin || !budgetMax) {
        alert("Please enter your budget range");
        return false;
    }

    if (parseFloat(budgetMin) > parseFloat(budgetMax)) {
        alert("Minimum budget must be less than maximum budget");
        return false;
    }

    const activities = document.querySelectorAll('input[name="activities"]:checked');
    if (activities.length === 0) {
        alert("Please select at least one preferred activity");
        return false;
    }

    return true;
}

function getSelectedActivities() {
    const checkboxes = document.querySelectorAll('input[name="activities"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function startPlanning() {
    if (!validateInputs()) {
        return;
    }

    const progressDiv = document.getElementById("progress");
    const clusterSelectionDiv = document.getElementById("cluster-selection");
    const itineraryDiv = document.getElementById("itinerary");
    const copyButton = document.getElementById("copyButton");

    // Clear previous content
    progressDiv.innerHTML = "";
    itineraryDiv.innerHTML = "";
    clusterSelectionDiv.style.display = "none";
    copyButton.style.display = "none";
    currentItineraryContent = '';

    // Open WebSocket connection
    ws = new WebSocket("ws://127.0.0.1:5000/ws");

    ws.onmessage = function(event) {
        const message = event.data;
        if (message.includes("Please review the options and select the correct cluster")) {
            clusterSelectionDiv.style.display = "block";
        }

        if (message.startsWith("Itinerary generated successfully!")) {
            currentItineraryContent = message.replace("Itinerary generated successfully!", "").trim();
            itineraryDiv.innerHTML = marked.parse(currentItineraryContent);
            copyButton.style.display = "block";
        } else {
            const messageElement = document.createElement("div");
            messageElement.className = "progress-message";
            messageElement.textContent = message;
            progressDiv.appendChild(messageElement);
        }

        requestAnimationFrame(() => {
            progressDiv.scrollTop = progressDiv.scrollHeight;
        });
    };

    ws.onopen = function() {
        const preferences = {
            destination: document.getElementById("destination").value,
            additional_destinations: document.getElementById("additionalDestinations").value.split(",").map(d => d.trim()).filter(d => d),
            start_date: document.getElementById("startDate").value,
            end_date: document.getElementById("endDate").value,
            budget_min: parseFloat(document.getElementById("budgetMin").value),
            budget_max: parseFloat(document.getElementById("budgetMax").value),
            travel_style: document.getElementById("travelStyle").value,
            preferred_activities: getSelectedActivities(),
            number_of_travelers: parseInt(document.getElementById("travelers").value),
            accessibility_requirements: document.getElementById("accessibility").value.trim() || null,
            dietary_restrictions: document.getElementById("dietary").value
                .split(",")
                .map(d => d.trim())
                .filter(d => d) || null,
            output_format: document.getElementById("outputFormat").value
        };

        console.log("Sending WebSocket payload:", preferences);
        ws.send(JSON.stringify(preferences));
    };

    ws.onerror = function(error) {
        const messageElement = document.createElement("div");
        messageElement.className = "progress-message error";
        messageElement.textContent = "Error: " + error.message;
        messageElement.style.borderLeftColor = "#FE363B";
        progressDiv.appendChild(messageElement);
        progressDiv.scrollTop = progressDiv.scrollHeight;
    };

    ws.onclose = function() {
        console.log("WebSocket connection closed");
        const messageElement = document.createElement("div");
        messageElement.className = "progress-message";
        messageElement.textContent = "Connection closed. Please refresh to start a new session.";
        progressDiv.appendChild(messageElement);
    };
}

function submitClusterSelection() {
    const clusterSelection = document.getElementById("cluster-input").value;
    if (ws && clusterSelection) {
        ws.send(clusterSelection);
        document.getElementById("cluster-selection").style.display = "none";
        document.getElementById("cluster-input").value = "";
    }
}

async function copyItinerary() {
    if (currentItineraryContent) {
        try {
            await navigator.clipboard.writeText(currentItineraryContent);
            const copyButton = document.getElementById("copyButton");
            const originalText = copyButton.textContent;
            copyButton.textContent = "Copied!";
            setTimeout(() => {
                copyButton.textContent = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy itinerary to clipboard');
        }
    }
}

// Set minimum date for date inputs to today
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("startDate").min = today;
    document.getElementById("endDate").min = today;

    // Update end date minimum when start date changes
    document.getElementById("startDate").addEventListener('change', function() {
        document.getElementById("endDate").min = this.value;
        if (document.getElementById("endDate").value < this.value) {
            document.getElementById("endDate").value = this.value;
        }
    });
});