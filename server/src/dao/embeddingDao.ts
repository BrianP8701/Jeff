import { PrismaClient, ContentType } from '@prisma/client';
import { container } from '../utils/container';
import pgvector from 'pgvector';

// Prisma doesn't support pgvector types, so we need to use raw SQL and make our own create input types
type EmbeddingCreateInput = {
  embedding: number[];
  contentType: ContentType;
  emailId?: string;
  fileId?: string;
  linkId?: string;
};

export async function createEmbedding(data: EmbeddingCreateInput) {
  const prisma = container.get(PrismaClient);
  const embedding = pgvector.toSql(data.embedding);
  return prisma.$executeRaw`
    INSERT INTO "Embedding" (id, embedding, "contentType", "emailId", "fileId", "linkId")
    VALUES (gen_random_uuid(), ${embedding}::vector, ${data.contentType}, ${data.emailId}, ${data.fileId}, ${data.linkId})
  `;
}

export type SimilaritySearchResult = {
  content_type: ContentType;
  source: string;
  title: string;
  content: string;
  distance: number;
};

export async function performSimilaritySearch(queryEmbedding: number[], limit: number): Promise<SimilaritySearchResult[]> {
  const prisma = container.get(PrismaClient);
  const embedding = pgvector.toSql(queryEmbedding);
  const results = await prisma.$queryRaw<SimilaritySearchResult[]>`
    SELECT 
      e."contentType" as content_type,
      COALESCE(em."messageId", f.path, l.url) AS source,
      COALESCE(em.subject, f.name, l.title) AS title,
      COALESCE(em.body, f.content, l.content) AS content,
      e.embedding <-> ${embedding}::vector AS distance
    FROM 
      "Embedding" e
      LEFT JOIN "Email" em ON e."emailId" = em.id
      LEFT JOIN "File" f ON e."fileId" = f.id
      LEFT JOIN "Link" l ON e."linkId" = l.id
    ORDER BY distance
    LIMIT ${limit}
  `;

  return results;
}

export async function clearAllTables() {
  const prisma = container.get(PrismaClient);
  await prisma.embedding.deleteMany();
  await prisma.email.deleteMany();
  await prisma.file.deleteMany();
  await prisma.link.deleteMany();
}