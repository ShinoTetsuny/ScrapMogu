import React from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';

export default function Home() {
  const navigate = useNavigate();

  const handleSearch = (url: string) => {
    navigate(`/fandom?url=${encodeURIComponent(url)}`);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Bienvenue 👋</h1>
      <SearchBar onSearch={handleSearch} />
    </div>
  );
}
