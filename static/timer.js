var totalSeconds = 0;
const iterLSR = (elem) => { totalSeconds += 1; renderLSR(elem, totalSeconds); };

var handle = null;

function resetTimer(elem) {
    clearInterval(handle);
    totalSeconds = 0;
    renderLSR(elem, totalSeconds);
    handle = setInterval(iterLSR, 1000, elem);
}

function renderLSR(elem, time){ 
    elem.innerHTML = "Last successful request: " + time + "s ago";
    if (time > 5) {
        elem.classList.remove('status-ok');
        elem.classList.add('status-critical');
    } else {
        elem.classList.add('status-ok');
        elem.classList.remove('status-critical');
    }
}
