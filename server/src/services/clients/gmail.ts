import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import dotenv from 'dotenv';

dotenv.config();

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const TOKEN_PATH = 'token.json';

interface EmailThread {
  [threadId: string]: Array<{
    sender: string;
    subject: string;
    body: string;
    messageId: string;
  }>;
}

class GmailClient {
  private auth: OAuth2Client;

  constructor() {
    this.auth = new google.auth.OAuth2(
      process.env.GMAIL_CLIENT_ID,
      process.env.GMAIL_CLIENT_SECRET,
      'urn:ietf:wg:oauth:2.0:oob'
    );

    this.auth.setCredentials({
      refresh_token: process.env.GMAIL_REFRESH_TOKEN,
    });
  }

  async readEmails(days: number = 7): Promise<EmailThread[string][]> {
    const gmail = google.gmail({ version: 'v1', auth: this.auth });
    const date = new Date();
    date.setDate(date.getDate() - days);
    const query = `after:${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;

    try {
      const res = await gmail.users.messages.list({
        userId: 'me',
        q: query,
      });

      const messages = res.data.messages || [];
      const emailThreads: EmailThread = {};

      for (const message of messages) {
        const fullMessage = await gmail.users.messages.get({
          userId: 'me',
          id: message.id!,
        });

        const threadId = fullMessage.data.threadId!;
        const headers = fullMessage.data.payload?.headers;
        const sender = headers?.find(h => h.name === 'From')?.value || '';
        const subject = headers?.find(h => h.name === 'Subject')?.value || '';
        const messageId = headers?.find(h => h.name === 'Message-ID')?.value || '';
        const body = this.getEmailBody(fullMessage.data);

        if (!emailThreads[threadId]) {
          emailThreads[threadId] = [];
        }

        emailThreads[threadId].push({
          sender,
          subject,
          body,
          messageId,
        });
      }

      return Object.values(emailThreads);
    } catch (error) {
      console.error('The API returned an error:', error);
      throw error;
    }
  }

  private getEmailBody(message: any): string {
    if (message.payload?.body?.data) {
      return Buffer.from(message.payload.body.data, 'base64').toString();
    }

    if (message.payload?.parts) {
      for (const part of message.payload.parts) {
        if (part.mimeType === 'text/plain' && part.body?.data) {
          return Buffer.from(part.body.data, 'base64').toString();
        }
      }
    }

    return '';
  }
}

export const gmailClient = new GmailClient();
