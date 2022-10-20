import express, { Response, Request, NextFunction } from "express";
import path from "path";

const indexRouter = express.Router();

indexRouter.get("/", (req: Request, res: Response, next: NextFunction) => {
    // console.log(path.join(__dirname + "/public/html/index.html"));
    res.sendFile(path.join(__dirname + "/public/html/index.html"));
});

export default indexRouter;