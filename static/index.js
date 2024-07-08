document.body.addEventListener('htmx:afterRequest', (ev) => {
    if (ev.detail.requestConfig.path == "/poll" && ev.detail.successful) {
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
    elapsedTimeElem.innerHTML = "Last successful request: " + time + "s ago";
    if (time > 5) {
        elapsedTimeElem.classList.remove('status-ok');
        elapsedTimeElem.classList.add('status-critical');
    } else {
        elapsedTimeElem.classList.add('status-ok');
        elapsedTimeElem.classList.remove('status-critical');
    }
}
