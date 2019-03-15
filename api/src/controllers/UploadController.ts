import { exec } from "child_process";
import express from "express";
import fs from "fs";
import multer from "multer";
import path from "path";

const uploadDir = "./uploads";

const storage = multer.diskStorage({
    destination: uploadDir,
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

    console.info(`running "unzip ${uploadDir}/${req.file.filename}"`);
    try {
        await exec(`cd ${uploadDir} && unzip ${req.file.filename}`);
        await exec(`rm ${uploadDir}/${req.file.filename}`);
        console.info("Success");
        res.sendStatus(200).end();
    } catch (err) {
        console.info("Error");
        console.error(err);
        res.sendStatus(500).send("Could not unzip file");
    }
});

export default router;
