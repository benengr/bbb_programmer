import express from "express";
import UploadController from "./controllers/UploadController";
const app = express();
const port = 8080;
import cors from "cors";
app.use(cors());

app.get("/", (req, res) => {
    res.send( "Hello world!" );
});

app.use("/api/v1", UploadController);

app.listen(port, () => {
    // tslint:disable-next-line:no-console
    console.log(`server started at http://localhost:${port}`);
});
