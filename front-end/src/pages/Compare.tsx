import React from 'react';
import { useLocation } from 'react-router-dom';
import Card from '../components/Card';

const mockCharacters = [
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
    image: 'https://static.wikia.nocookie.net/game-of-thrones-le-trone-de-fer/images/f/fa/Jon_Snow.png',
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
    image: 'https://static.wikia.nocookie.net/heros/images/6/65/Tyrion_Lannister_Infobox.png',
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

  return (
    <div className="mt-6">
      <h2 className="text-2xl font-bold mb-4">🔍 Comparaison de personnages</h2>

      {selectedCharacters.length === 2 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {selectedCharacters.map((char) => (
            <Card key={char.id} character={char} />
          ))}
        </div>
      ) : (
        <p className="text-red-600">⚠️ Vous devez sélectionner exactement 2 personnages pour comparer.</p>
      )}
    </div>
  );
}
