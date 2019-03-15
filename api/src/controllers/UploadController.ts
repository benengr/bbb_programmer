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

router.post("/upload", upload, (req, res) => {
    console.info(`${req.file.originalname} uploaded successfully`);
    res.sendStatus(200).end();
});

export default router;
