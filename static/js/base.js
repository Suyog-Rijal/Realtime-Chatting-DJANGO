window.baseJsLoaded = true;
var chatSockets = [];

function clearChatSockets() {
    chatSockets.forEach(function(socket) {
        socket.close();
    });
    chatSockets = [];
}