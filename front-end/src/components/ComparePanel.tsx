import React from 'react';
import Card from './Card';

export default function ComparePanel({ items }: { items: any[] }) {
  if (items.length < 2) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <Card character={items[0]} />
      <Card character={items[1]} />
    </div>
  );
}
