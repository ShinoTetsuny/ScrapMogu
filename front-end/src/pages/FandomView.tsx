import React, { useEffect, useState } from 'react';
import Card from '../components/Card';
import { useSearchParams } from 'react-router-dom';
import { fetchFandomData } from '../services/api';

export default function FandomView() {
  const [params] = useSearchParams();
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = params.get('url');
    if (url) {
      fetchFandomData(url).then((res) => {
        setData(res);
        setLoading(false);
      });
    }
  }, [params]);

  return (
    <div className="p-6">
      {loading ? (
        <div className="text-center">Chargement...</div>
      ) : (
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3">
          {data.map((char, i) => (
            <Card key={i} character={char} />
          ))}
        </div>
      )}
    </div>
  );
}
