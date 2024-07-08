document.body.addEventListener('htmx:afterRequest', (ev) => {
    if (ev.detail.requestConfig.path == "/infra") {
        resetTimer();
    }
})
const elapsedTimeElem = document.getElementById("elapsedTime");
var totalSeconds = 0; // reset this to zero when you reset as below
const iterTimer = (fn) => { totalSeconds += 1; fn(totalSeconds); };
const iterLCR = () => { iterTimer(renderLCR) };

var handle = setInterval(iterLCR, 1000);


function resetTimer() {
    clearInterval(handle);
    totalSeconds = 0;
    renderLCR(totalSeconds);
    handle = setInterval(iterLCR, 1000);
}

function renderLCR(time){ 
    elapsedTimeElem.innerHTML = "Last completed request: " + time + "s ago";
}
