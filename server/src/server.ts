import express, { Request, Response } from 'express';
import { performSimilaritySearch } from './dao/embeddingDao';
import { generateAnswerSummary } from './services/openai';
import dotenv from 'dotenv';
import { getEmbedding } from './services/embeddings/embed';

dotenv.config();

const app = express();
app.use(express.json());


enum ItemType {
  FILE = "FILE",
  URL = "URL"
}

interface SearchResult {
  type: ItemType;
  source: string;
  title: string;
  distance: number;
}

interface SearchResponse {
  results: SearchResult[];
  answer_summary: string | null;
  error?: string;
}

interface SearchRequest {
  query: string;
  limit?: number;
}

app.post('/search', async (req: Request<{}, {}, SearchRequest>, res: Response<SearchResponse>) => {
  const { query, limit = 5 } = req.body;
  console.log(`Search endpoint accessed with query: ${query}`);

  try {
    const queryEmbedding = await getEmbedding(query);
    const results = await performSimilaritySearch(queryEmbedding, limit);

    let summaryContextString = "";
    const searchResults: SearchResult[] = results.map(result => {
      summaryContextString += "\n\n" + result.content;
      let itemType = result.content_type === 'FILE' ? ItemType.FILE : ItemType.URL;
      let source = result.source;

      if (result.content_type === 'EMAIL') {
        source = `https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox/${source}`;
      }

      return {
        type: itemType,
        source: source,
        title: result.title,
        distance: result.distance
      };
    });

    const answerSummary = await generateAnswerSummary(query, summaryContextString);

    console.log(`Search results: ${JSON.stringify(searchResults)}`);
    res.json({ results: searchResults, answer_summary: answerSummary });
  } catch (error) {
    console.error('Error during search:', error);
    res.status(500).json({ results: [], answer_summary: null, error: 'An error occurred during the search' });
  }
});

const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
