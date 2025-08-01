import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';

import Home from './pages/Home';
import FandomView from './pages/FandomView';
import Compare from './pages/Compare';
import Card from './components/Card';

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

export default function App() {
  const [showMock, setShowMock] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const navigate = useNavigate();

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

  // 🔍 Récupération des options de filtres
  const attributeOptions = useMemo(() => {
    const result: Record<string, Set<string>> = {};
    mockCharacters.forEach((char) => {
      for (const [key, value] of Object.entries(char.attributes)) {
        if (!result[key]) result[key] = new Set();
        result[key].add(value);
      }
    });
    return result;
  }, []);

  // 🧠 Application des filtres aux personnages
  const filteredCharacters = useMemo(() => {
    return mockCharacters.filter((char) =>
      Object.entries(filters).every(([key, value]) =>
        char.attributes[key as keyof typeof char.attributes] === value
      )
    );
  }, [filters]);

  const handleFilterChange = (attribute: string, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [attribute]: value,
    }));
  };

  const clearFilters = () => setFilters({});

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

        {/* MOCK: Affichage fictif + sélection */}
        <div className="mt-8 border-t pt-6">
          <h2 className="text-lg font-semibold mb-4">🧪 Test avec données fictives</h2>

          <button
            onClick={() => setShowMock(!showMock)}
            className="mb-4 px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition"
          >
            {showMock ? 'Masquer les données' : 'Afficher des exemples'}
          </button>

          {showMock && (
            <>
              {/* 🎛️ Filtres dynamiques */}
              <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                {Object.entries(attributeOptions).map(([key, values]) => (
                  <div key={key}>
                    <label className="block text-sm font-semibold mb-1 capitalize">{key}</label>
                    <select
                      className="w-full border p-2 rounded"
                      value={filters[key] ?? ''}
                      onChange={(e) => handleFilterChange(key, e.target.value)}
                    >
                      <option value="">— Tous —</option>
                      {[...values].map((val) => (
                        <option key={val} value={val}>
                          {val}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>

              <button
                onClick={clearFilters}
                className="text-sm text-blue-600 underline mb-4"
              >
                Réinitialiser les filtres
              </button>

              {/* 🧩 Liste des cartes filtrées */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {filteredCharacters.map((char) => (
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
