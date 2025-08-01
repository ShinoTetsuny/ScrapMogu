import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import Card from '../components/Card';

type Character = {
  id: string;
  name: string;
  image: string;
  description: string;
  attributes: Record<string, string>;
  serie: string;
};

export default function FandomView() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchParams] = useSearchParams();
  const [url, setUrl] = useState('');

  useEffect(() => {
    const initialUrl = searchParams.get('url');
    if (initialUrl) {
      setUrl(initialUrl);
      handleSearch(initialUrl);
    }
  }, [searchParams]);

  const handleSearch = async (fandomUrl: string) => {
    setLoading(true);
    setError(null);
    setUrl(fandomUrl);

    try {
      const response = await fetch('http://localhost:3000/api/scrap/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: fandomUrl }),
      });

      if (!response.ok) throw new Error('Scraping échoué');

      const data = await response.json();
      const serieName = new URL(fandomUrl).hostname.split('.')[0];

      const charactersData = Array.isArray(data) ? data : data.characters;

      if (!Array.isArray(charactersData)) {
        throw new Error("La réponse ne contient pas un tableau de personnages.");
      }

      const parsed: Character[] = charactersData.map((char: any, index: number) => ({
        id: char.id || `${serieName}-${index}`,
        name: char.name,
        image: char.image,
        description: char.description,
        attributes: char.attributes || {},
        serie: serieName,
      }));


      setCharacters(parsed);
      localStorage.setItem('characters', JSON.stringify(parsed));
    } catch (err: any) {
      console.error(err);
      setError('Erreur lors du scraping.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">🔍 Résultats du Fandom</h1>
      <SearchBar onSearch={handleSearch} initialUrl={url} />

      {loading && <p className="text-indigo-600 mt-4">Chargement en cours...</p>}
      {error && <p className="text-red-600 mt-4">{error}</p>}

      {characters.length > 0 && (
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {characters.map((char) => (
            <Card key={char.id} character={char} />
          ))}
        </div>
      )}
    </div>
  );
}
