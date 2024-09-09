import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { marked } from 'marked';
import { PDFDocument } from 'pdf-lib';
import { createWorker } from 'tesseract.js';
import { container } from '../../utils/container';
import { PrismaClient } from '@prisma/client';
import { getEmbedding, chunkContent } from '../embeddings/embed';
import { createFile } from '../../dao/fileDao';
import { createEmbedding } from '../../dao/embeddingDao';
import { fromPath } from 'pdf2pic';

const FOLDER_PATH = process.env.FOLDER_PATH || 'jeff_storage';

async function getFileContents(filePath: string): Promise<string> {
  const ext = path.extname(filePath).toLowerCase();

  if (ext === '.md' || ext === '.txt') {
    const content = fs.readFileSync(filePath, 'utf-8');
    return ext === '.md' ? marked(content) : content;
  } else if (ext === '.pdf') {
    return ocrPdf(filePath);
  } else {
    throw new Error(`Unsupported file type: ${ext}`);
  }
}

async function ocrPdf(filePath: string): Promise<string> {
  const worker = await createWorker();
  let text = '';

  const options = {
    density: 300,
    saveFilename: "temp_page",
    savePath: "./temp",
    format: "png",
    width: 2480,
    height: 3508
  };

  const convert = fromPath(filePath, options);
  const pdfDoc = await PDFDocument.load(fs.readFileSync(filePath));

  for (let i = 0; i < pdfDoc.getPageCount(); i++) {
    const result = await convert(i + 1);
    const base64 = (result as any).base64;
    const { data: { text: pageText } } = await worker.recognize(`data:image/png;base64,${base64}`);
    text += pageText + '\n';
  }

  await worker.terminate();
  return text.replace(/\0/g, '');
}

function getContentHash(content: string): string {
  return crypto.createHash('sha256').update(content).digest('hex');
}

export async function processFiles(folderPath: string): Promise<void> {
  const prisma = container.get(PrismaClient);

  const processFile = async (filePath: string) => {
    const ext = path.extname(filePath).toLowerCase();

    if (['.md', '.txt', '.pdf'].includes(ext)) {
      try {
        const content = await getFileContents(filePath);
        const chunks = chunkContent(content);

        for (let i = 0; i < chunks.length; i++) {
          const chunk = chunks[i];
          const contentHash = getContentHash(chunk);

          const existingFile = await prisma.file.findFirst({
            where: { contentHash }
          });

          if (existingFile) continue;

          const embedding = await getEmbedding(chunk);

          const fileData = {
            name: `${path.basename(filePath)}_chunk_${i + 1}`,
            path: filePath,
            content: chunk,
            contentHash: contentHash,
          };

          const storedFile = await createFile(fileData);
          await createEmbedding({
            embedding,
            contentType: 'FILE',
            fileId: storedFile.id,
          });

          console.log(`Stored file chunk: ${storedFile.id} - ${storedFile.name}`);
        }
      } catch (error) {
        console.error(`Error processing file ${filePath}:`, error);
      }
    }
  };

  const processDirectory = async (dir: string) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        await processDirectory(fullPath);
      } else {
        await processFile(fullPath);
      }
    }
  };

  await processDirectory(folderPath);
}

if (require.main === module) {
  processFiles(FOLDER_PATH).catch(console.error);
}
