import React from 'react';
import { useLocation } from 'react-router-dom';
import Card from '../components/Card';
import type { Character } from '../types/character';

const mockCharacters : Character[] = [
  {
    id: '1',
    name: 'Aria Stark',
    image: 'https://static.posters.cz/image/1300/135445.jpg',
    description: 'Assassine formée par les Sans-Visages.',
    attributes: {
      origine: 'Winterfell',
      rôle: 'Assassin',
      affiliation: 'Maison Stark',
    },
  },
  {
    id: '2',
    name: 'Jon Snow',
    image: 'https://static.wikia.nocookie.net/heroes-and-villain/images/4/47/Jon_Snow_profile.jpg',
    description: 'Commandant de la Garde de Nuit devenu Roi du Nord.',
    attributes: {
      origine: 'Château Noir',
      rôle: 'Guerrier',
      affiliation: 'Maison Stark',
    },
  },
  {
    id: '3',
    name: 'Daenerys Targaryen',
    image: 'https://static.wikia.nocookie.net/wrestling-for-life/images/e/e3/Daenerys_Targaryen.jpg',
    description: 'Mère des Dragons, héritière des Targaryen.',
    attributes: {
      origine: 'Dragonstone',
      rôle: 'Reine',
      affiliation: 'Maison Targaryen',
    },
  },
  {
    id: '4',
    name: 'Tyrion Lannister',
    image: 'https://cdn.theatlantic.com/thumbor/YWaxYWJGr9OU6p9xaaVD5vvw3_M=/480x168:3312x3000/1080x1080/media/img/mt/2019/04/80393c4672f3dbfa94c07164fc4b90bc95f0c620a6c96900108badc1cde33d36/original.jpg',
    description: 'Main de la Reine et stratège politique.',
    attributes: {
      origine: 'Casterly Rock',
      rôle: 'Conseiller',
      affiliation: 'Maison Lannister',
    },
  },
];


export default function Compare() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const ids = searchParams.get('ids')?.split(',') ?? [];

  const selectedCharacters = mockCharacters.filter((char) => ids.includes(char.id));

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

      {selectedCharacters.length === 2 ? (
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