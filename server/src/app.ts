import express, { Application } from "express";
import { WebSocketServer } from "ws";
import http from "http";
import path from "path";
import * as dotenv from "dotenv";

// import cookieParser from "cookie-parser";

import router from "./index-router"

dotenv.config({ path: path.join(__dirname, '../.env')});

const app: Application = express();

app.use(express.static(path.join(__dirname, "public")));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(router);


const server = http.createServer(app);
const port = Number(process.env.HTTP_PORT);

server.listen(port, () => {
    console.log(`start! express server on port ${port}`);
});

const wss: WebSocketServer = new WebSocketServer({ port: Number(process.env.WS_PORT) });

wss.on("connection", (ws, req) => {
    console.log(`WS is opened! at port ${process.env.WS_PORT}`);

    // console.log(wss.clients);
    ws.on('message', (data) => {
        console.log(data.toString());
        wss.clients.forEach(client => {
            client.send(data.toString())
        });
    });
});