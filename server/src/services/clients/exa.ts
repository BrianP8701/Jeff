import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const EXA_API_URL = 'https://api.exa.ai/contents';
const EXA_API_KEY = process.env.EXA_KEY;

interface ExaResponse {
  results: Array<{
    text: string;
  }>;
}

export async function getContentsForUrl(webUrl: string): Promise<string> {
  try {
    const response = await axios.post<ExaResponse>(
      EXA_API_URL,
      {
        ids: [webUrl],
        text: { includeHtmlTags: false },
      },
      {
        headers: {
          'accept': 'application/json',
          'content-type': 'application/json',
          'x-api-key': EXA_API_KEY,
        },
      }
    );

    return response.data.results[0].text;
  } catch (error) {
    console.error('Error fetching content from Exa:', error);
    throw error;
  }
}
