import { useState, useEffect } from "react";


type UseFetchConfig = {
  onCompleted?: (data: any) => void;
};

export const useFetch = <T>(
  url: string,
  options: UseFetchConfig = {}
): { loading: boolean; error: any; data: any } => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const abortController = new AbortController();
    const signal = abortController.signal;

    setLoading(true);
    fetch(url, { credentials: 'include', signal })
      .then((r) => r.json())
      .then((data) => {
        setData(data);
        setLoading(false);
        options.onCompleted && options.onCompleted(data);
      })
      .catch((e) => {
        setError(e);
        setLoading(false);
      });
    return () => {
      abortController.abort();
    };
  }, [url]);

  return { loading, data, error };
};