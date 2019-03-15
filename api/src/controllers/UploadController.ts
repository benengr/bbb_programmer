import { exec } from "child_process";
import express from "express";
import fs from "fs";
import multer from "multer";
import path from "path";

const storage = multer.diskStorage({
    destination: "./uploads",
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});

const upload = multer({
    limits: {fileSize: 1024 * 1024 * 100},
    storage,
}).single("firmware");

const router = express.Router();

router.post("/upload", upload, async (req, res) => {
    console.info(`${req.file.originalname} uploaded successfully`);

    console.info(`Extracting ${req.file.filename}`);
    try {
        await exec(`unzip ${req.file.filename}`);
        console.info("Success");
        res.sendStatus(200).end();
    } catch (err) {
        console.info("Error");
        console.error(err);
        res.sendStatus(500).send("Could not unzip file");
    }
});

export default router;
