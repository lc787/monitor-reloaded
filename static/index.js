var totalSeconds = 0; // reset this to zero when you reset as below
document.body.addEventListener('htmx:afterRequest',resetTimer)
var timer = document.getElementById("timer");

setInterval(setTime, 1000);

function setTime(){
    ++totalSeconds;
    timer.innerHTML = "Last Request:" + pad(totalSeconds) + " s";
}

function pad(val){
    var valString = val + "";
    if(valString.length < 2)
    {
        return "0" + valString;
    }
    else
    {
        return valString;
    }
}

// reset() function
function resetTimer(){
    document.getElementById("timer").innerHTML = "Last Request: 00s";
    totalSeconds = 0
}
