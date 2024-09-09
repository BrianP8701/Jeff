import { createEmail } from '../../dao/emailDao';
import { createEmbedding } from '../../dao/embeddingDao';
import { getEmbedding } from '../embeddings/embed';

export async function processAndStoreEmail(email: any) {
  const storedEmail = await createEmail({
    sender: email.sender,
    subject: email.subject,
    body: email.body,
    messageId: email.messageId,
  });

  const embedding = await getEmbedding(email.body);

  await createEmbedding({
    embedding,
    contentType: 'EMAIL',
    emailId: storedEmail.id,
  });

  return storedEmail;
}
