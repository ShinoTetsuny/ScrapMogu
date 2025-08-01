import React, { useState, useEffect } from 'react';

export default function SearchBar({
  onSearch,
  initialUrl = '',
}: {
  onSearch: (url: string) => void;
  initialUrl?: string;
}) {
  const [url, setUrl] = useState(initialUrl);

  useEffect(() => {
    setUrl(initialUrl); // pour mettre à jour si ça vient du routeur
  }, [initialUrl]);

  return (
    <div className="flex gap-2 items-center w-full max-w-2xl">
      <input
        className="flex-grow p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        type="url"
        placeholder="Entrez l’URL du fandom (ex: https://starwars.fandom.com)"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button
        onClick={() => onSearch(url)}
        className="px-4 py-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition"
      >
        Scraper
      </button>
    </div>
  );
}
