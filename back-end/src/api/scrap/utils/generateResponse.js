import dotenv from 'dotenv';
dotenv.config();
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Pas de baseURL ici
});

async function generateResponse(text) {
  try {
    const response = await client.chat.completions.create({
      model: 'gpt-3.5-turbo', 
      messages: [
        {
          role: 'user',
          content: `
Tu es un assistant qui extrait les informations importantes depuis un HTML.

Voici un HTML :\n\n${text}\n\n

Retourne uniquement un objet JSON contenant les informations extraites.
Exemple : { "titre": "...", "description": "...", "auteurs": [...] }.

Pas de texte explicatif, pas de phrase autour. Juste du JSON valide.
          `,
        },
      ],
      max_tokens: 1000,
      temperature: 0.2,
    });

    const raw = response.choices[0].message.content.trim();

    // On tente de parser le JSON proprement
    const result = JSON.parse(raw);
    console.log('Réponse générée :', result);
    return result;
  } catch (error) {
    console.error('Erreur dans generateResponse :', error?.response?.data || error);
    throw error;
  }
}

export default generateResponse;
