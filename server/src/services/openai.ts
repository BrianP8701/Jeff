import OpenAI from 'openai';
import { container } from '../utils/container';

export async function generateAnswerSummary(question: string, content: string, model: string = 'gpt-4'): Promise<string> {
  const openai = container.get(OpenAI);

  const messages = [
    {
      role: "user" as const,
      content: `Answer the following question: ${question}. Only use information from the following text and provide as brief of an answer as possible: \n ${content}`
    }
  ];

  const response = await openai.chat.completions.create({
    model: model,
    messages: messages,
    temperature: 0.0
  });

  return response.choices[0].message.content || '';
}