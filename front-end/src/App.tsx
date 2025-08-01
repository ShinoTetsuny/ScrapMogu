import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';

import Home from './pages/Home';
import FandomView from './pages/FandomView';
import Compare from './pages/Compare';
import Card from './components/Card';

interface Character {
  id: string;
  name: string;
  image: string;
  description: string;
  attributes: Record<string, string>;
  serie: string;
}

export default function App() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCharacters, setShowCharacters] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (showCharacters) {
      setLoading(true);
      fetch('http://localhost:3000/api/scrap/history')
        .then(res => res.json())
        .then(data => {
          setCharacters(data.characters || []);
          setLoading(false);
        })
        .catch(err => {
          setError('Erreur lors du chargement des personnages.');
          setLoading(false);
        });
    }
  }, [showCharacters]);

  const toggleSelection = (id: string) => {
    setSelected(prev => {
      if (prev.includes(id)) return prev.filter(pid => pid !== id);
      if (prev.length < 2) return [...prev, id];
      return prev;
    });
  };

  const compareSelected = () => {
    if (selected.length === 2) {
      navigate(`/compare?ids=${selected.join(',')}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-white shadow sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-indigo-600">
            Scrapeur Universel 🔍
          </Link>
          <nav className="space-x-4 text-sm">
            <Link to="/" className="hover:underline">
              Accueil
            </Link>
            <Link to="/compare" className="hover:underline">
              Comparateur
            </Link>
          </nav>
        </div>
      </header>

      <main className="py-6 px-4 max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/fandom" element={<FandomView />} />
          <Route path="/compare" element={<Compare />} />
        </Routes>

        <div className="mt-8 border-t pt-6">
          <h2 className="text-lg font-semibold mb-4">🧪 Données scrappées</h2>

          <button
            onClick={() => setShowCharacters(!showCharacters)}
            className="mb-4 px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition"
          >
            {showCharacters ? 'Masquer' : 'Charger les personnages'}
          </button>

          {loading && <p className="text-gray-500">Chargement en cours...</p>}
          {error && <p className="text-red-500">{error}</p>}

          {showCharacters && characters.length > 0 && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {characters.map((char) => (
                  <div key={char.id} className="relative">
                    <Card character={char} />
                    <button
                      onClick={() => toggleSelection(char.id)}
                      className={`absolute top-2 right-2 px-2 py-1 text-xs rounded ${
                        selected.includes(char.id)
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-200 text-gray-800'
                      }`}
                    >
                      {selected.includes(char.id) ? 'Sélectionné' : 'Sélectionner'}
                    </button>
                  </div>
                ))}
              </div>

              <div className="mt-4">
                <button
                  onClick={compareSelected}
                  disabled={selected.length !== 2}
                  className={`px-4 py-2 rounded-xl transition font-medium ${
                    selected.length === 2
                      ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Comparer les {selected.length}/2 sélectionnés
                </button>
              </div>
            </>
          )}
        </div>
      </main>

      <footer className="text-center text-sm text-gray-500 py-4 border-t mt-6">
        © 2025 - Projet Scraper Fandom | TS + Vite + Tailwind
      </footer>
    </div>
  );
}
