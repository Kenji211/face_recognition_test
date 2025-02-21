document.addEventListener("DOMContentLoaded", function () {
    const startBtn = document.querySelector(".start-btn");

    startBtn.addEventListener("click", function () {
        fetch("/toggle_detection", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.face_detection_enabled) {
                    startBtn.innerText = "STOP";
                } else {
                    startBtn.innerText = "START";
                }
            })
            .catch(error => console.error("Error:", error));
    });
}); /*start scanning attendance button*/

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
            alert(data.message); // Show success message
        })
        .catch(error => console.error("Error:", error));
    }
});/*registering student*/