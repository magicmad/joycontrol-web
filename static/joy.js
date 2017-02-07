
$("#log2").text("");
$("#log3").text("");



var socket = new WebSocket("ws://10.1.1.137:90/ws");

// callback-Funktion wird gerufen, wenn die Verbindung erfolgreich aufgebaut werden konnte
socket.onopen = function ()
{
    $("#log2").append("Verbindung wurde erfolgreich aufgebaut");
};

// callback-Funktion wird gerufen, wenn eine neue Websocket-Nachricht eintrifft
socket.onmessage = function (messageEvent)
{
  if(messageEvent.data.startsWith("C"))
  {
    $("#log3").text(messageEvent.data);
    drawCompass(messageEvent.data.slice(1));
  }
//  else if(messageEvent.data.startsWith("C"))
//  {
//    $("#log3").append(messageEvent.data);
//  }
};

// callback-Funktion wird gerufen, wenn eine Fehler auftritt
socket.onerror = function (errorEvent)
{
    $("#log2").append("Error! Die Verbindung wurde unerwartet geschlossen");
};

// callback-Funktion wird gerufen, wenn die Verbindung beendet wird
socket.onclose = function (closeEvent)
{
    $("#log2").append('Die Verbindung wurde geschlossen --- Code: '
        + closeEvent.code + ' --- Grund: ' + closeEvent.reason);
};


function toRad(val)
{
    return val * Math.PI / 180;
}

function drawCompass(angle)
{
    var needle = document.getElementById('needle');  
    needle.setAttribute('transform', 'translate(50, 50) rotate(' + angle + ') translate(-50, -50)');
}


function adjustJoyValue(value)
{
    var multiplier = -100;
    if(value < 0)
        multiplier = 100;

    value = value * value * multiplier;
    return value;
}


var lastL = 0;
var lastR = 0;

// we need a gamepad selection, check if it is still alive
// if there is none, list pads and show list to user to select one
function runAnimation()
{
    if(socket.readyState == 1)
    {
        var activeGamepad = null;

        var gamepads = navigator.getGamepads();

        $("#log").text(""); 

        for (var i = 0; i < gamepads.length; ++i)
        {
            var pad = gamepads[i];
            if(pad != null && pad.connected)
            {
                $("#log").append(pad.id);
                activeGamepad = pad;
                break;
            }
        }


        // use active gamepad
        if(activeGamepad != null)
        {
            var l = activeGamepad.axes[1];
            var r = activeGamepad.axes[3];
                
            $("#log").append("<br>");
            $("#log").append("L: " + l + " R: " + r);

            if (Math.abs(lastL - l) > 0.05 || Math.abs(lastR - r) > 0.05)
            {
                lastL = l;
                lastR = r;
                
                l = adjustJoyValue(l);
                r = adjustJoyValue(r);

                socket.send(l + ";" + r);
                $("#log2").append(Date.now() + " - L: " + l + " R: " + r);
            }
        }
        else
        {
            // stop engines
        }
    }

    window.requestAnimationFrame(runAnimation);

}

window.requestAnimationFrame(runAnimation);
