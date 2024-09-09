import OpenAI from 'openai';
import dotenv from 'dotenv';
import { encode } from 'gpt-3-encoder';
import { container } from '../../utils/container';

dotenv.config();

export function numTokensFromString(string: string, modelName: string = "text-embedding-3-large"): number {
  return encode(string).length;
}

export function chunkContent(content: string, maxTokens: number = 5000): string[] {
  const chunks: string[] = [];
  let currentChunk = "";
  let currentTokens = 0;

  for (const line of content.split('\n')) {
    const lineTokens = numTokensFromString(line);
    if (currentTokens + lineTokens > maxTokens) {
      chunks.push(currentChunk.trim());
      currentChunk = line;
      currentTokens = lineTokens;
    } else {
      currentChunk += line + '\n';
      currentTokens += lineTokens;
    }
  }

  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }

  return chunks;
}

export async function getEmbedding(text: string): Promise<number[]> {
  try {
    const openai = container.get(OpenAI);
    const response = await openai.embeddings.create({
      model: "text-embedding-3-large",
      input: text,
    });
    return response.data[0].embedding
  } catch (error) {
    console.error('Error getting embedding:', error);
    throw error;
  }
}
