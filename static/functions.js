document.addEventListener("DOMContentLoaded", function () {
    const startBtn = document.querySelector(".start-btn");
    let pollingInterval = null; // Store interval for student polling

    // Toggle Face Detection
    startBtn.addEventListener("click", function () {
        fetch("/toggle_detection", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.face_detection_enabled) {
                    startBtn.innerText = "STOP";
                    startRecognizing(); // Start recognizing when detection is enabled
                } else {
                    startBtn.innerText = "START";
                    stopRecognizing(); // Stop recognizing when detection is disabled
                }
            })
            .catch(error => console.error("Error:", error));
    });

    // Function to start polling for recognized students
    function startRecognizing() {
        if (!pollingInterval) {
            pollingInterval = setInterval(() => {
                fetch("/recognized_student")
                    .then(response => response.json())
                    .then(data => {
                        if (data["student-name"] && data["id-number"]) {
                            document.querySelector(".id-number").textContent = data["id-number"];
                            document.querySelector(".student-name").textContent = data["student-name"];
                        }
                    })
                    .catch(error => console.error("Error fetching recognized student:", error));
            }, 1000); // Fetch updated data every second
        }
    }

    // Function to stop polling
    function stopRecognizing() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const registerBtn = document.querySelector(".register-btn");  /*attendance.html register button*/

    if (registerBtn) {
        registerBtn.addEventListener("click", function () {
            fetch("/disable_detection", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (!data.face_detection_enabled) {
                        window.location.href = "/register";  // Redirect after disabling detection
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }
}); /*reseting start button when navigating*/

document.addEventListener("DOMContentLoaded", function () {
    // Listen for the REGISTER button click
    document.querySelector(".regis-btn").addEventListener("click", function () {
        registerStudent();
    });

    function registerStudent() {
        let idNumber = document.getElementById("idNumber").value.trim();
        let studentName = document.getElementById("studentName").value.trim();

        if (!idNumber || !studentName) {
            alert("Please enter both Student ID and Name!");
            return;
        }

        fetch("/register_student", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idNumber: idNumber, studentName: studentName })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Show success or error message
            if (data.redirect) {
                window.location.href = data.redirect; // Redirect to attendance page if specified
            }
        })
        .catch(error => console.error("Error:", error));
    }
});/*registering student*/
