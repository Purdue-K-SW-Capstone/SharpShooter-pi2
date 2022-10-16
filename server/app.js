const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 5000 });

wss.on('connection', (ws) => {

    console.log("WS is opened!");

    // console.log(wss.clients);
    ws.on('message', (data) => {
        console.log(data.toString());
        wss.clients.forEach(client => {
            client.send(data.toString())
        });
    });
});
