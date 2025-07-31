// src/components/Card.tsx
import React from 'react';

interface CharacterProps {
  character: {
    name: string;
    image: string;
    description: string;
    attributes: Record<string, string>;
  };
}

export default function Card({ character }: CharacterProps) {
  return (
    <div className="bg-white rounded-2xl shadow p-4 flex flex-col h-full">
      <img
        src={character.image}
        alt={character.name}
        className="w-full h-48 object-cover rounded-xl mb-3"
      />
      <h3 className="text-lg font-semibold">{character.name}</h3>
      <p className="text-sm text-gray-600 line-clamp-3">{character.description}</p>
      <ul className="text-sm text-gray-700 mt-2 space-y-1">
        {Object.entries(character.attributes).map(([key, value]) => (
          <li key={key}>
            <span className="font-medium capitalize">{key}:</span> {value}
          </li>
        ))}
      </ul>
    </div>
  );
}
