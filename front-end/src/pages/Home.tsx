import React from 'react';
import SearchBar from '../components/SearchBar';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  const handleSearch = (url: string) => {
    const encoded = encodeURIComponent(url);
    navigate(`/fandom?url=${encoded}`);
  };

  return (
    <div className="flex flex-col items-center mt-16 px-4">
      <h1 className="text-3xl font-bold mb-6">🔎 Scrapeur Universel Fandom</h1>
      <SearchBar onSearch={handleSearch} />
    </div>
  );
}
