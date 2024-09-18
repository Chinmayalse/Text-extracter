import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, fetch }) => {
  const { message, extracted_data, user_id } = await request.json();

  try {
    const response = await fetch('http://localhost:8000/chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, extracted_data, user_id })
    });

    if (!response.ok) {
      throw new Error('Failed to get response from backend');
    }

    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error in chatbot API:', error);
    return json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
};