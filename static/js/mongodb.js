var socket = new WebSocket("ws://localhost:8000/ws");
      socket.onmessage = function(event) {
          var data = JSON.parse(event.data);
          document.getElementById("data").innerHTML = data;
      };