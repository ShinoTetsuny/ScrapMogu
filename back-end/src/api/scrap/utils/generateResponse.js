import dotenv from 'dotenv';
dotenv.config();
import Openai from 'openai';

const client = new Openai({
    baseURL: process.env.OPENAI_BASE_URL,
    apiKey: process.env.OPENAI_API_KEY,
})

async function generateResponse(text) {
    try {
        const response = await client.chat.completions.create({
            model: 'phi-3.1-mini-128k-instruct',
            messages: [{ role: 'user', content: text }],
            max_tokens: 1000,
            temperature: 0.7,
        });

        return response.choices[0].message.content;
    } catch (error) {
        console.error('Error generating response:', error);
        throw error;
    }
}

export default generateResponse;