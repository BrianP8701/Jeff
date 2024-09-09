import { container } from '../utils/container';
import { PrismaClient } from '@prisma/client';
import { gmailClient } from '../services/clients/gmail';
import { processAndStoreEmail } from '../services/dataLoaders/email';
import { processFiles } from '../services/dataLoaders/files';
import { getContentsForUrl } from '../services/clients/exa';
import { createLink } from '../dao/linkDao';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

const FOLDER_PATH = process.env.FOLDER_PATH || 'jeff_storage';

async function ingestRecentEmails(days: number = 7) {
  const prisma = container.get(PrismaClient);

  try {
    const recentEmailThreads = await gmailClient.readEmails(days);

    for (const thread of Object.values(recentEmailThreads)) {
      for (const email of thread) {
        try {
          const storedEmail = await processAndStoreEmail(email);
          console.log(`Stored email: ${storedEmail.id} - ${storedEmail.subject}`);
        } catch (error: any) {
          if (error.code === 'P2002') {
            console.log(`Email already exists: ${email.subject}`);
          } else {
            console.error(`Error processing email: ${error}`);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error during email ingestion:', error);
  }

  console.log("Email ingestion complete.");
}

async function ingestFiles(folderPath: string) {
  try {
    await processFiles(folderPath);
  } catch (error) {
    console.error('Error during file ingestion:', error);
  }
}

async function ingestBrowserHistory() {
  try {
    console.log("Getting history");
    const historyFilePath = path.join(FOLDER_PATH, 'browser_history.json');
    const historyData = fs.readFileSync(historyFilePath, 'utf8');
    const historyEntries = JSON.parse(historyData);

    for (const entry of historyEntries) {
      try {
        const content = await getContentsForUrl(entry.url);
        await createLink({
          url: entry.url,
          title: entry.title,
          content: content,
        });
        console.log(`Stored link: ${entry.url}`);
      } catch (error) {
        console.error(`Error processing link ${entry.url}:`, error);
      }
    }
  } catch (error) {
    console.error('Error during history ingestion:', error);
  }
}

async function main() {
  const prisma = container.get(PrismaClient);

  // Ingest emails
  await ingestRecentEmails();

  // Ingest files
  await ingestFiles(FOLDER_PATH);

  // Ingest browser history
  await ingestBrowserHistory();

  await prisma.$disconnect();
}

main().catch((error) => {
  console.error('Error in main ingest process:', error);
  process.exit(1);
});