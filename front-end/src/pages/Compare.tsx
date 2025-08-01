// src/pages/Compare.tsx
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import Card from '../components/Card';
import type { Character } from '../types/character';

function mapRawCharacter(raw: any): Character {
  const attributes: Record<string, string> = {};

  if (raw.attribute1_name && raw.attribute1_value) {
    attributes[raw.attribute1_name] = raw.attribute1_value;
  }

  if (raw.attribute2_name && raw.attribute2_value) {
    attributes[raw.attribute2_name] = raw.attribute2_value;
  }

  return {
    id: raw.source_url,
    name: raw.name,
    image: raw.image_url,
    description: raw.description,
    attributes,
  };
}

export default function Compare() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const ids = searchParams.get('ids')?.split(',') ?? [];

  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const res = await fetch('http://localhost:3000/api/scrap/history');
        const data = await res.json();
        const mapped = data.characters.map(mapRawCharacter);
        setCharacters(mapped);
      } catch (err) {
        console.error('Erreur lors du fetch des personnages:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCharacters();
  }, []);

  const selectedCharacters = characters.filter((char) => ids.includes(char.id));

  const renderComparisonTable = () => {
    if (selectedCharacters.length !== 2) return null;

    const [charA, charB] = selectedCharacters;
    const allKeys = Array.from(
      new Set([...Object.keys(charA.attributes), ...Object.keys(charB.attributes)])
    );

    return (
      <div className="mt-8">
        <h3 className="text-xl font-semibold mb-3">🧮 Comparaison détaillée</h3>
        <table className="min-w-full table-auto border border-gray-300 rounded-lg overflow-hidden text-sm">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="p-2 border">Attribut</th>
              <th className="p-2 border">{charA.name}</th>
              <th className="p-2 border">{charB.name}</th>
            </tr>
          </thead>
          <tbody>
            {allKeys.map((key) => {
              const valA = charA.attributes[key] ?? '—';
              const valB = charB.attributes[key] ?? '—';
              const isSame = valA === valB;

              return isSame ? (
                <tr key={key} className="bg-green-100 font-medium text-green-800">
                  <td className="border p-2">{key}</td>
                  <td className="border p-2 text-center" colSpan={2}>
                    {valA}
                  </td>
                </tr>
              ) : (
                <tr key={key}>
                  <td className="border p-2 font-medium">{key}</td>
                  <td className="border p-2">{valA}</td>
                  <td className="border p-2">{valB}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="mt-6">
      <h2 className="text-2xl font-bold mb-4">🔍 Comparaison de personnages</h2>

      {loading ? (
        <p>Chargement des personnages...</p>
      ) : selectedCharacters.length === 2 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {selectedCharacters.map((char) => (
              <Card key={char.id} character={char} />
            ))}
          </div>
          {renderComparisonTable()}
        </>
      ) : (
        <p className="text-red-600">⚠️ Vous devez sélectionner exactement 2 personnages pour comparer.</p>
      )}
    </div>
  );
}
