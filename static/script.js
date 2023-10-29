// static/script.js

// Süre başladığında çalışacak kod
function startTimer(duration, display, remainingTime, remainingQuestions) {
    let timer = remainingTime || duration;
    const countdown = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0 || remainingQuestions <= 0) {
            clearInterval(countdown); // Sayacı durdur
            window.location.href = leaderboardURL;
        }
    }, 1000);
}

window.onload = function () {
    const display = document.querySelector("#time-left");
    const remainingTime = parseInt(display.getAttribute("data-remaining-time")) || 60;
    const remainingQuestions = parseInt(document.querySelector("input[name='remaining_questions']").value) || 10;
    startTimer(remainingTime, display, remainingTime, remainingQuestions);
};
