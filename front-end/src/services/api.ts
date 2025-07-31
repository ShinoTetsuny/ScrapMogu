export const fetchFandomData = async (url: string): Promise<any[]> => {
  const res = await fetch(`http://localhost:8000/scrape?url=${encodeURIComponent(url)}`);
  if (!res.ok) throw new Error('Erreur lors de la récupération des données');
  return res.json();
};
